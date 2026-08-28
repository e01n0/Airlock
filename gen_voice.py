#!/usr/bin/env python3
"""Pre-render Airlock's coach with ElevenLabs into a playable voice pack.

Airlock's coach is a recorded human voice, not text-to-speech: every cue is a
short clip, so the app sounds like someone sitting with you and works offline
once the pack is cached. This script renders each phrase listed in
voice/phrases.json to an MP3 into voice/<pack>/, plus a manifest.json of what
is present. Generate the phrase list first with `node gen_phrases.js` — it is
read straight out of index.html, so it can't drift from what the app says.

Nothing here stores a key: you bring your own ElevenLabs API key and voice,
run this once, then commit voice/<pack>/ so it deploys with the static site.

Usage
-----
    export ELEVENLABS_API_KEY=sk_...
    node gen_phrases.js
    python3 gen_voice.py --voice-id <ELEVENLABS_VOICE_ID> --pack vera --force

The pack id must match an entry in VOICE_PACKS in index.html. Without --force,
already-rendered clips are skipped so re-running resumes cheaply.

Pick a CALM voice. This is the opposite brief to a sports app: slow, low,
unhurried, no exclamation in it. A voice that sounds motivating will sound
alarming when it says "hold" to somebody forty seconds into an empty-lung hold.
"""
import argparse, json, os, sys, time, urllib.request, urllib.error

API = "https://api.elevenlabs.io/v1/text-to-speech/{vid}?output_format=mp3_44100_128"
ROOT = os.path.dirname(os.path.abspath(__file__))

# Per-style delivery. Phase cues are short, isolated clips that land many times
# in a session, so they must be consistent with each other and with themselves:
# high stability keeps every "hold" the same "hold". Coaching lines are whole
# sentences said once or twice, and want a little more life — but far less than
# a fight corner would: style stays low so nothing ever sounds urgent.
STYLE_SETTINGS = {
    "cue":  {"stability": 0.75, "similarity": 0.85, "style": 0.0},
    "line": {"stability": 0.55, "similarity": 0.82, "style": 0.10},
    "test": {"stability": 0.60, "similarity": 0.82, "style": 0.05},
}

# MUST match slugify() in index.html and slugify() in gen_phrases.js.
def slug(s):
    import re
    s = s.lower().strip().replace("&", "and")
    s = re.sub(r"['\".,!?:;]", "", s)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def render(text, voice_id, model, key, stability, similarity, style_exag,
           prev_text=None, next_text=None, prev_ids=None):
    payload = {
        "text": text,
        "model_id": model,
        "voice_settings": {
            "stability": stability,
            "similarity_boost": similarity,
            "style": style_exag,
            "use_speaker_boost": True,
        },
    }
    # Sentence context: rendering a short cue "as if mid-sentence" gives it
    # level, non-terminal prosody and — more importantly — anchors its register.
    # Rendered bare, a one-word clip like "Hold!" can come back an octave high.
    if prev_text: payload["previous_text"] = prev_text
    if next_text: payload["next_text"] = next_text
    # Request stitching: condition on the previous renders so a batch sounds
    # like one continuous recording session rather than N separate takes.
    if prev_ids: payload["previous_request_ids"] = prev_ids[-3:]
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        API.format(vid=voice_id), data=body, method="POST",
        headers={"xi-api-key": key, "Content-Type": "application/json",
                 "Accept": "audio/mpeg"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read(), r.headers.get("request-id")


def main():
    ap = argparse.ArgumentParser(description="Render an Airlock ElevenLabs voice pack.")
    ap.add_argument("--voice-id", required=True, help="ElevenLabs voice id")
    ap.add_argument("--pack", default="vera", help="output id under voice/ (match VOICE_PACKS in index.html)")
    ap.add_argument("--styles", default="cue,line,test", help="comma list to render: cue,line,test")
    ap.add_argument("--model", default="eleven_multilingual_v2", help="ElevenLabs model id")
    ap.add_argument("--stability", type=float, default=None, help="override per-style stability for all clips")
    ap.add_argument("--similarity", type=float, default=None, help="override per-style similarity_boost")
    ap.add_argument("--style", type=float, default=None, help="override per-style exaggeration 0..1")
    ap.add_argument("--force", action="store_true", help="re-render clips that already exist")
    ap.add_argument("--sleep", type=float, default=0.3, help="pause between calls (seconds)")
    ap.add_argument("--only", default="", help="comma list of slugs to render; blank = all")
    ap.add_argument("--stitch", action="store_true",
                    help="chain renders with previous_request_ids for one-session consistency")
    args = ap.parse_args()

    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        sys.exit("Set ELEVENLABS_API_KEY in your environment first.")

    phrases_path = os.path.join(ROOT, "voice", "phrases.json")
    if not os.path.exists(phrases_path):
        sys.exit("voice/phrases.json is missing — run `node gen_phrases.js` first.")
    with open(phrases_path, encoding="utf-8") as f:
        phrases = json.load(f)

    # A phrase whose slug does not round-trip would render to a filename the
    # app never asks for: catch it here rather than after paying for the audio.
    bad = [p for p in phrases if slug(p["text"]) != p["slug"]]
    if bad:
        sys.exit("slug mismatch (regenerate phrases.json): " + ", ".join(p["slug"] for p in bad[:5]))

    want = {s.strip() for s in args.styles.split(",") if s.strip()}
    only = {s.strip() for s in args.only.split(",") if s.strip()}
    todo = [p for p in phrases if p["style"] in want and (not only or p["slug"] in only)]
    outdir = os.path.join(ROOT, "voice", args.pack)
    os.makedirs(outdir, exist_ok=True)

    print(f"{len(todo)} clips in styles {sorted(want)} -> voice/{args.pack}/")
    made = skipped = failed = 0
    recent_ids = []
    for i, p in enumerate(todo, 1):
        dest = os.path.join(outdir, p["slug"] + ".mp3")
        if os.path.exists(dest) and not args.force:
            skipped += 1
            continue
        st = STYLE_SETTINGS.get(p["style"], STYLE_SETTINGS["cue"])
        stability  = args.stability  if args.stability  is not None else st["stability"]
        similarity = args.similarity if args.similarity is not None else st["similarity"]
        style_x    = args.style      if args.style      is not None else st["style"]
        for attempt in range(4):
            try:
                audio, rid = render(p["text"], args.voice_id, args.model, key,
                                    stability, similarity, style_x,
                                    p.get("prev"), p.get("next"),
                                    recent_ids if args.stitch else None)
                if args.stitch and rid: recent_ids.append(rid)
                with open(dest, "wb") as out:
                    out.write(audio)
                made += 1
                print(f"  [{i}/{len(todo)}] {p['slug']:<34} “{p['text']}”")
                time.sleep(args.sleep)
                break
            except urllib.error.HTTPError as e:
                msg = e.read().decode("utf-8", "replace")[:200]
                if e.code == 429 and attempt < 3:          # rate limited — back off
                    time.sleep(2 ** attempt)
                    continue
                print(f"  ! {p['slug']}: HTTP {e.code} {msg}", file=sys.stderr)
                failed += 1
                break
            except Exception as e:                          # network blip — retry
                if attempt < 3:
                    time.sleep(2 ** attempt)
                    continue
                print(f"  ! {p['slug']}: {e}", file=sys.stderr)
                failed += 1
                break

    # The manifest is every clip actually present in the pack dir, so the app
    # knows exactly what it can play and what to fall back on.
    slugs = sorted(f[:-4] for f in os.listdir(outdir) if f.endswith(".mp3"))
    with open(os.path.join(outdir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump({"voice": args.voice_id, "model": args.model, "slugs": slugs}, f, indent=2)
        f.write("\n")

    print(f"\nrendered {made}, skipped {skipped}, failed {failed}. "
          f"manifest lists {len(slugs)} clips.")
    print("Next: python3 gen_trim.py --pack %s && python3 gen_pitch.py --pack %s" % (args.pack, args.pack))
    print(f"Then pick the pack under Setup → Coaching → Coach voice and commit voice/{args.pack}/.")


if __name__ == "__main__":
    main()
