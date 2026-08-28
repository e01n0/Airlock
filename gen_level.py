#!/usr/bin/env python3
"""Even out a rendered voice pack's loudness, and report what is wrong with it.

Every clip in a pack is rendered in isolation, so ElevenLabs gives each one its
own level. On a bright voice that spread is a few dB and the app's playback
normalisation absorbs it. On a soft, breathy voice — the kind this app wants —
it can reach 25dB: some coaching lines come back so quiet that they sit under
the app's silence-trim threshold entirely and the coach drops the line without
a sound. That is not something you can hear in a spot check of six clips, so it
gets measured here instead.

This script normalises every clip in place to a common RMS with a peak ceiling
(so nothing clips), and prints a QA report: silent clips, clipped clips, and
clips whose length is wildly out of step with their text, which is what a
truncated or wrong-text render looks like from the outside.

Run it after rendering, before gen_pitch.py:

    pip install numpy imageio-ffmpeg      # once; bundles a static ffmpeg
    python3 gen_level.py --pack wren --dry-run    # report only
    python3 gen_level.py --pack wren
"""
import argparse, json, os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
SR = 22050
TARGET_RMS = 0.075       # matches NORM_RMS in index.html (~ -22 dBFS)
PEAK_CEIL  = 0.89        # leave headroom; clips are concatenated at playback
MAX_GAIN   = 12.0        # past this the "speech" is room tone — report, don't amplify


def decode(ff, path):
    import numpy as np
    p = subprocess.run([ff, "-v", "error", "-i", path, "-f", "f32le", "-ac", "1",
                        "-ar", str(SR), "-"], capture_output=True)
    return np.frombuffer(p.stdout, dtype="<f4")


NUM_WORDS = {"0":"zero","1":"one","2":"two","3":"three","4":"four","5":"five","6":"six",
             "7":"seven","8":"eight","9":"nine","10":"ten","11":"eleven","12":"twelve",
             "13":"thirteen","14":"fourteen","15":"fifteen","16":"sixteen","17":"seventeen",
             "18":"eighteen","19":"nineteen","20":"twenty"}


def syllables(text):
    """Rough syllable count. Digits are spelled out first — "Round 1" is spoken
    as two syllables, and counting vowel groups in "1" finds none, which would
    flag every round call as suspiciously long."""
    t = re.sub(r"\d+", lambda m: " " + NUM_WORDS.get(m.group(), m.group()) + " ", text.lower())
    return max(1, len(re.findall(r"[aeiouy]+", t)))


def main():
    ap = argparse.ArgumentParser(description="Normalise and QA a rendered voice pack.")
    ap.add_argument("--pack", default="wren", help="pack directory under voice/")
    ap.add_argument("--dry-run", action="store_true", help="report only, change nothing")
    args = ap.parse_args()
    try:
        import numpy as np
        from imageio_ffmpeg import get_ffmpeg_exe
    except ImportError:
        sys.exit("pip install numpy imageio-ffmpeg first (bundles a static ffmpeg).")
    ff = get_ffmpeg_exe()

    d = os.path.join(ROOT, "voice", args.pack)
    if not os.path.isdir(d):
        sys.exit(f"no such pack: voice/{args.pack}/")
    with open(os.path.join(ROOT, "voice", "phrases.json"), encoding="utf-8") as f:
        phrases = {p["slug"]: p["text"] for p in json.load(f)}

    missing, quiet, clipped, rows = [], [], [], []
    for slug, text in phrases.items():
        path = os.path.join(d, slug + ".mp3")
        if not os.path.exists(path):
            missing.append(slug)
            continue
        x = decode(ff, path)
        if not len(x):
            missing.append(slug)
            continue
        peak = float(np.abs(x).max())
        rms = float(np.sqrt(np.mean(x ** 2)))
        gain = min(TARGET_RMS / rms if rms > 1e-6 else 1.0, PEAK_CEIL / max(peak, 1e-6))
        # Voiced seconds, measured the way the app's trim does it: relative to
        # this clip's own peak, so a quiet take is not scored as a short one.
        voiced = float((np.abs(x) > max(0.004, peak * 0.06)).sum()) / SR
        rows.append((slug, text, voiced, peak, rms, gain))
        if peak < 0.05:
            quiet.append((slug, peak))
        if peak >= 0.99:
            clipped.append(slug)

    if not rows:
        sys.exit("nothing to measure.")

    peaks = [r[3] for r in rows]   # rows: slug, text, voiced secs, peak, rms, gain
    spread = 20 * np.log10(max(peaks) / max(min(peaks), 1e-6))
    print(f"voice/{args.pack}/: {len(rows)} clips")
    print(f"  peak spread before levelling: {spread:.1f} dB "
          f"({min(peaks):.3f} … {max(peaks):.3f})")

    # Length against text: a clip far off the pack's own words-per-second is
    # the signature of a truncated render or the wrong text.
    per_syl = float(np.median([r[2] / syllables(r[1]) for r in rows]))
    odd = [(r[0], r[1], r[2], r[2] / syllables(r[1]) / per_syl) for r in rows
           if not 0.5 < (r[2] / syllables(r[1]) / per_syl) < 2.0]
    if quiet:
        print(f"  ! {len(quiet)} clip(s) rendered near-silent — re-render these:")
        print("      --only " + ",".join(s for s, _ in sorted(quiet, key=lambda z: z[1])))
    if clipped:
        print(f"  ! {len(clipped)} clip(s) already clipping: {', '.join(clipped)}")
    if odd:
        print(f"  ! {len(odd)} clip(s) an odd length for their text:")
        for slug, text, dur, ratio in sorted(odd, key=lambda z: z[3])[:8]:
            print(f"      {ratio:4.2f}x expected  {dur:4.2f}s  {slug:<30} “{text}”")
    if missing:
        print(f"  ! missing from the pack: {', '.join(missing)}")

    if args.dry_run:
        print("\n--dry-run: nothing written.")
        return

    changed = 0
    for slug, text, dur, peak, rms, gain in rows:
        if abs(gain - 1.0) < 0.03 or gain > MAX_GAIN:
            continue
        path = os.path.join(d, slug + ".mp3")
        tmp = tempfile.mktemp(suffix=".mp3")
        r = subprocess.run([ff, "-v", "error", "-y", "-i", path,
                            "-af", f"volume={gain:.4f}", "-codec:a", "libmp3lame",
                            "-b:a", "128k", tmp], capture_output=True)
        if r.returncode == 0 and os.path.getsize(tmp) > 0:
            os.replace(tmp, path)
            changed += 1
        else:
            if os.path.exists(tmp):
                os.remove(tmp)
            print(f"  ! failed to level {slug}: {r.stderr.decode()[:120]}", file=sys.stderr)
    print(f"\nlevelled {changed} clip(s) to RMS {TARGET_RMS} "
          f"(peak ceiling {PEAK_CEIL}). Bump VOICE_REV in index.html.")


if __name__ == "__main__":
    main()
