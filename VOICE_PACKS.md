# Recorded voice packs (ElevenLabs)

Airlock's coach is designed as a **recorded human voice** — pre-rendered with
ElevenLabs and shipped as static audio, exactly the way Coach Fred's corner man
works. Every cue is a short clip; the app plays them back-to-back through Web
Audio. That keeps the app self-contained and offline-capable (it just ships some
audio files), and no API key is ever stored in it: you regenerate the voice by
running the script with your own key.

## The shipped packs

Two, both British women, rendered from `voice/phrases.json` with
`eleven_multilingual_v2`:

| pack | voice | register | character |
|---|---|---|---|
| **`wren`** *(default)* | ElevenLabs **Lily** (`pFZP5JQG7iQjIQuC4Bku`) | ~146 Hz | Low, breathy, unhurried. The brief. |
| **`bly`** | ElevenLabs **Alice** (`Xb7hH8MSUJpSbSDYk0k2`) | ~213 Hz | Clearer and brighter — easier to follow in a noisy room. |

Wren is the default because it is the softer of the two by a wide margin. On a
bare cue like *"Hold"*, Lily reads flat — a 9–15 Hz spread of pitch across the
word — while Alice swings about 150 Hz across the same syllable. That
expressiveness is an asset in a narration and a liability in an app that says
"hold" to somebody forty seconds into an empty-lung hold. Bly is there for
people who find Wren too quiet to follow.

The **device voice** (Setup → Coaching → Coach voice → *Device voice*) remains
as a fallback: it needs no download and covers any line a pack is missing.
Airlock aims its auto-selection at the same brief — a British female voice, with
the British male voices explicitly ranked down so "Daniel" cannot win an en-GB
search by being first in the list — and you can override it with a picker that
names each voice's locale. The chime and the guide tone are synthesised in the
browser and never depended on any of this.

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
   python3 gen_voice.py  --voice-id <VOICE_ID> --pack wren --force --stitch
   python3 gen_level.py  --pack wren     # even out the levels, and QA the render
   python3 gen_pitch.py  --pack wren     # helium audit
   ```

   `--stitch` chains renders with `previous_request_ids` so the whole batch
   sounds like one recording session. Drop `--force` to fill in only what is
   missing. Pronunciation of any phrase is controlled by its `text` — respell it
   in `index.html`, re-run `gen_phrases.js`, and re-render that one clip with
   `--only <slug>`.

3. Act on what `gen_level.py` reports, then hit **Test voice** in Setup to hear
   it. Re-render anything it calls near-silent or an odd length, then level
   again — see *Levelling* below.

4. **Commit `voice/<pack>/`** so it deploys with the static site:

   ```bash
   git add voice/vera && git commit -m "Add recorded voice pack"
   ```

5. Bump `VOICE_REV` in `index.html` whenever you re-render clips. The service
   worker serves voice audio cache-first and deliberately carries it across app
   upgrades, so without the bump a returning device plays one stale take before
   its background refresh lands.

## Levelling: the check that matters most

**Run `gen_level.py` on every pack.** Each clip is rendered in isolation, so
ElevenLabs gives each its own level, and on a soft voice that spread is not
cosmetic. Wren's first render came back spanning **26 dB**, with four coaching
lines so quiet they sat under the app's silence-trim threshold — the coach
dropped those lines with no sound at all, and no spot check of half a dozen
clips would have caught it. Re-rendering the offenders and levelling brought the
pack to 10.6 dB and nothing silent.

`gen_level.py` normalises every clip in place to a common RMS with a peak
ceiling, and reports three things worth acting on before you commit a pack:

- **near-silent clips** — re-render these; levelling a take that is mostly room
  tone just amplifies room tone,
- **clipping**,
- **clips whose voiced length is far out of step with their text**, which is
  what a truncated or wrong-text render looks like from the outside.

The app levels clips again at playback, but that is a safety net with a peak
ceiling on it, not a substitute: it cannot rescue a take that trims to nothing
before it ever reaches the gain stage.

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
real fix is a re-render, and the script prints the exact command; Bly's three
flagged takes were re-rendered and it now audits clean.

**The audit does not work on every voice, and it says so.** When more than a
quarter of a pack flags, the tracker is not following the voice rather than the
pack being broken — a low or breathy read has little periodic energy, and the
estimator splits between the true pitch and its harmonics. Wren trips exactly
this: measured against her sentences she "flags" 29 of 101 clips, all of them
fine. So the script writes `pitch.json` with an empty `avoid` list and a `note`
recording why, rather than either shipping a list that would gut the pack or
leaving no file at all — with no file, the app cannot tell "audited, nothing
wrong" from "never audited", and takes a 404 on every load.

For a voice like that, judge the takes by ear and re-render the suspect ones.

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
