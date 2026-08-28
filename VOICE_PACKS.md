# Recorded voice packs (ElevenLabs)

Airlock's coach is designed as a **recorded human voice** — pre-rendered with
ElevenLabs and shipped as static audio, exactly the way Coach Fred's corner man
works. Every cue is a short clip; the app plays them back-to-back through Web
Audio. That keeps the app self-contained and offline-capable (it just ships some
audio files), and no API key is ever stored in it: you regenerate the voice by
running the script with your own key.

## No pack is committed yet

Rendering a pack spends ElevenLabs characters against a real account, so this
repo ships the **toolchain and the plumbing**, not the audio. Until you render
one, the app uses your **device's own speech engine** (Setup → Coaching → Coach
voice → *Device voice*), which needs no download and works offline, but sounds
like a phone. The chime and the guide tone are synthesised in the browser and
never depended on any of this.

Everything downstream is already wired: `VOICE_PACKS` in `index.html` lists two
pack ids, the picker shows them, the manifest/pitch/prefetch paths are live, and
the service worker carries clips across app upgrades. Render into
`voice/vera/` or `voice/sten/` and it lights up.

## How it works

The coach only ever says a **finite set of short phrases** — each phase cue,
each round call, each count, each coaching line. They are listed in
[`voice/phrases.json`](voice/phrases.json) (103 clips), and that file is
**generated, not hand-written**:

```bash
node gen_phrases.js       # reads index.html -> voice/phrases.json
```

`gen_phrases.js` pulls the coaching-line pools and the per-phase cue words
straight out of `index.html` and adds the fixed lines from the speech call
sites. The runtime looks a clip up by slugifying what it is about to say, so
generating the list from the same source is what stops the vocabulary and the
recordings drifting apart. Add a coaching line to `LINES` in `index.html`,
re-run it, and the new phrase is in the render list.

At runtime the app splits a spoken line on `". "` and plays one clip per clause.

## Consistent delivery across clips

Because cues are recorded alone and heard hundreds of times in a session, the
biggest lever is **stability**: low stability gives every take its own dramatic
read, which is exactly wrong for a phase cue that should sound identical on the
fortieth repeat. `gen_voice.py` sets delivery **per style** (`STYLE_SETTINGS`):

| style | what it covers | delivery |
|---|---|---|
| `cue` | phase cues, round calls, the 5-4-3-2-1 count | high stability, no style — even and unremarkable |
| `line` | coaching lines | looser, a little style, still nowhere near urgent |
| `test` | the BOLT test's instructions | in between |

`--stability/--similarity/--style` override all of it.

Each clip is also rendered in isolation, so two takes can come back at slightly
different volumes. The app levels every clip to a common loudness on playback
(RMS with a peak ceiling so nothing clips) and trims the lead-in/out silence, so
clauses sit together like speech rather than a row of separate takes — no
re-render needed for either.

**Voice speed** re-times clips with a pitch-preserving overlap-add stretch, not
`playbackRate`, so a slower coach stays the same coach.

## Choosing a voice

Pick a **calm** one. This is the opposite brief to a sports app: slow, low,
unhurried, with no exclamation in it. A voice that sounds motivating on a
sample page will sound alarming when it says *"hold"* to somebody forty seconds
into an empty-lung hold. Test it on the longest coaching line, not the shortest
cue.

## Render a pack

1. Get an [ElevenLabs](https://elevenlabs.io) API key and pick a voice; note its
   **voice id** from the Voices page. A paid plan unlocks the full library and
   clears the free tier's attribution and redistribution terms.

2. Render:

   ```bash
   export ELEVENLABS_API_KEY=sk_...
   node gen_phrases.js
   python3 gen_voice.py --voice-id <VOICE_ID> --pack vera --force --stitch
   ```

   `--stitch` chains renders with `previous_request_ids` so the whole batch
   sounds like one recording session. Drop `--force` to fill in only what is
   missing. Pronunciation of any phrase is controlled by its `text` — respell it
   in `index.html`, re-run `gen_phrases.js`, and re-render that one clip with
   `--only <slug>`.

3. Audit the pitch (below), then hit **Test voice** in Setup to hear it.

4. **Commit `voice/<pack>/`** so it deploys with the static site:

   ```bash
   git add voice/vera && git commit -m "Add recorded voice pack"
   ```

5. Bump `VOICE_REV` in `index.html` whenever you re-render clips. The service
   worker serves voice audio cache-first and deliberately carries it across app
   upgrades, so without the bump a returning device plays one stale take before
   its background refresh lands.

## Pitch audit: catching helium takes

ElevenLabs renders short isolated utterances unpredictably. A one-word cue like
*"Hold"* can land in the voice's true register on one take and half an octave up
on the next — which, in an app whose entire job is sounding calm while somebody
sits in air hunger, is the worst thing that can happen to it. The `prev` lead-in
carried by every phrase in `phrases.json` is the first defence: rendering a cue
with sentence context in front of it anchors the register.

For takes already rendered, `gen_pitch.py` measures every clip's median F0
against the register of the pack's long clips (whole sentences carry their own
context and land reliably) and writes the outliers to `voice/<pack>/pitch.json`:

```bash
pip install numpy imageio-ffmpeg   # once; bundles a static ffmpeg
python3 gen_pitch.py --pack vera   # -> voice/vera/pitch.json
```

At run time a line containing a flagged clip is spoken by the device voice
instead — a plainer voice saying the whole thing beats a squeaked *"hold"*. The
file is optional: with no `pitch.json`, nothing is flagged. The script refuses
to write one when more than a quarter of the pack flags, because that means the
pitch tracker cannot follow the voice (creak or fry reads as false falsetto)
rather than that the pack is broken.

The real fix for a flagged clip is a re-render — the script prints the exact
command.

## Offline

The service worker caches each clip the first time it plays
(stale-while-revalidate), so after one online run-through the recorded coach
works offline. **Setup → More → Take the coach offline** fetches the whole pack
in one go before you train somewhere with no signal.

## Adding more packs

`--pack <id>` writes to `voice/<id>/`. Add an entry to `VOICE_PACKS` in
`index.html` and it appears in the picker:

```js
const VOICE_PACKS = [
  { id:"vera", label:"Vera — calm, close" },
  { id:"sten", label:"Sten — flat, factual" },
];
```

## Costs & licensing

Clips are generated against **your** ElevenLabs account and count toward your
character quota — 103 short phrases is a small render. Make sure your plan's
licensing permits redistributing the rendered audio in a deployed app, and don't
commit your API key.
