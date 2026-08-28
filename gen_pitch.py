#!/usr/bin/env python3
"""Audit a rendered voice pack's pitch and write voice/<pack>/pitch.json.

ElevenLabs renders short isolated utterances unpredictably. A one-word cue like
"Hold" can come back near the voice's true register on one take and half an
octave up on the next — which, in an app whose whole job is to sound calm while
somebody sits in air hunger, is the single worst failure mode there is. The app
cannot hear it, so this script measures every clip's median F0 (autocorrelation
over voiced frames) and ships the verdict as pitch.json:

    {"baseline": 176, "threshold": 273, "avoid": ["hold", "exhale"]}

The baseline is the median F0 of the pack's LONG clips — the coaching lines are
whole sentences, so they carry their own prosodic context and reliably land in
the voice's real register. Anything measuring more than `RATIO` above that is
listed in "avoid", and at run time the app speaks those lines with the device
voice instead of playing a squeaked take. The real fix is a re-render:

    python3 gen_voice.py --voice-id <id> --pack <pack> --force --only <slug,slug,...>

Run after every gen_voice.py session so the table matches the takes:

    pip install numpy imageio-ffmpeg     # once; bundles a static ffmpeg
    python3 gen_pitch.py --pack vera
"""
import argparse, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SR = 22050
RATIO = 1.45          # ~6.5 semitones sharp: where "emphatic" ends and "helium" begins
LONG_S = 1.1          # a clip this long is a sentence, not a bare cue


def decode(ff, path):
    import numpy as np
    p = subprocess.run([ff, "-v", "error", "-i", path, "-f", "f32le", "-ac", "1",
                        "-ar", str(SR), "-"], capture_output=True)
    return np.frombuffer(p.stdout, dtype=np.float32)


def median_f0(x, sr=SR):
    """Median F0 over voiced frames; None when nothing voiced (silence, noise)."""
    import numpy as np
    frame, hop = int(0.040 * sr), int(0.010 * sr)
    lag_lo, lag_hi = int(sr / 400), int(sr / 60)   # 60-400 Hz search band
    f0s = []
    rms_all = np.sqrt(np.mean(x ** 2)) if len(x) else 0
    for start in range(0, len(x) - frame, hop):
        fr = x[start:start + frame].astype(np.float64)
        if np.sqrt(np.mean(fr ** 2)) < max(0.02, 0.5 * rms_all):
            continue                                # silence / breath
        fr = fr - fr.mean()
        ac = np.correlate(fr, fr, "full")[frame - 1:]
        if ac[0] <= 0:
            continue
        ac /= ac[0]
        k = int(np.argmax(ac[lag_lo:lag_hi]))
        if ac[lag_lo + k] < 0.5:
            continue                                # unvoiced frame
        f0s.append(sr / (lag_lo + k))
    return float(np.median(f0s)) if f0s else None


def main():
    ap = argparse.ArgumentParser(description="Write pitch.json for a rendered voice pack.")
    ap.add_argument("--pack", default="vera", help="pack directory under voice/")
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
    f0, dur = {}, {}
    files = sorted(f for f in os.listdir(d) if f.endswith(".mp3"))
    for i, f in enumerate(files, 1):
        x = decode(ff, os.path.join(d, f))
        v = median_f0(x)
        if v:
            f0[f[:-4]] = v
            dur[f[:-4]] = len(x) / SR
        if i % 25 == 0:
            print(f"  measured {i}/{len(files)}")

    longs = sorted(v for k, v in f0.items() if dur[k] >= LONG_S)
    if len(longs) < 8:
        sys.exit("Not enough long clips to establish the voice's register — "
                 "render the `line` style before auditing pitch.")
    baseline = longs[len(longs) // 2]
    threshold = baseline * RATIO
    avoid = sorted(k for k, v in f0.items() if v > threshold)

    # Sanity gate: on a creaky or breathy voice the tracker cannot follow the
    # irregular glottal pulses and reads fry as high pitch. A real helium
    # problem affects a minority of takes; if most clips flag, the measurement
    # is untrustworthy and shipping it would gut the pack. Refuse to write.
    if len(avoid) > 0.25 * len(f0):
        sys.exit(f"{len(avoid)}/{len(f0)} clips flagged — the pitch tracker "
                 f"can't follow this voice (creak/fry?). Not writing pitch.json.")

    out = {"baseline": round(baseline), "threshold": round(threshold), "avoid": avoid}
    with open(os.path.join(d, "pitch.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)
        fh.write("\n")
    print(f"{len(files)} clips, register {baseline:.0f} Hz, "
          f"{len(avoid)} flagged above {threshold:.0f} Hz -> voice/{args.pack}/pitch.json")
    if avoid:
        print("Re-render these to fix them properly:")
        print("  --only " + ",".join(avoid))


if __name__ == "__main__":
    main()
