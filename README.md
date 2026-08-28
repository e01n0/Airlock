# Airlock

A breathwork trainer for **CO₂ tolerance** — the thing that decides how calm you
stay when your body starts telling you to breathe. It measures where you are,
sizes the work to that number, and paces every breath out loud so you can shut
your eyes and stop watching a screen. Single self-contained `index.html`, no
build step.

> An airlock equalises pressure before it lets you through. So does this.

## Safety, first, because this one matters

Breath-holding has one genuinely fatal failure mode and it is worth four lines
of your attention:

- **Never in or near water.** Breath-holding before or during swimming causes
  shallow-water blackout, which arrives with no warning. Not in the bath, not in
  the pool, not on a board.
- **Never while driving,** cycling, or standing at the top of stairs.
- **Sit or lie down** somewhere you could faint without hurting yourself.
- Talk to a doctor first if you are pregnant, or live with epilepsy, high blood
  pressure, heart or lung disease, a history of fainting, or an aneurysm.

Airlock shows this once before it will run anything, and keeps it under
**Setup → More → Safety**. It is a training timer, not medical advice.

## What it actually trains

Most people breathe more than they need to. Over-breathing keeps blood CO₂ low,
and because CO₂ is what triggers the urge to breathe, a low set-point makes that
urge arrive early and loudly — at rest, under load, and in the middle of the
night. Training CO₂ tolerance moves the set-point: same oxygen, later alarm.

The measurement is the **BOLT score** (Body Oxygen Level Test): breathe
normally, exhale normally, hold, and stop at the **first definite urge to
breathe** — not at your limit. Under 10 seconds is very reactive breathing;
20 is a common starting point; 40 is the athlete end of the scale. Take it first
thing in the morning, before coffee and before any breathing practice, and it is
comparable week to week.

Airlock keeps a twelve-week trend of your score, and — this is the point —
**sizes the tables from it**. A CO₂-table hold is set at roughly your own BOLT,
so the hold itself stays comfortable and all the training pressure comes from
the shrinking recovery between holds. As the score climbs, so does the work,
without you touching a dial.

## Protocols

**Setup → Session → Protocol** picks what runs. All eleven are described in the
app under **Setup → More → Protocol guide**, and in more depth in
[PROTOCOLS.md](PROTOCOLS.md).

| | What it does |
|---|---|
| **BOLT test** | The measurement. A minute of normal breathing, then one hold you end yourself on the first urge. |
| **CO₂ table** | Fixed hold, shrinking recovery. The direct CO₂-tolerance table — the one that moves your BOLT. |
| **O₂ table** | Generous recovery, growing hold. Builds hold length rather than tolerance. |
| **Pyramid table** | Holds climb to a peak and come back down. The descent is the interesting half. |
| **Box breathing** | Equal in, hold, out, hold. The empty-lung hold at the end of each box is where the work is. |
| **Coherent breathing** | ~6 breaths a minute, no holds. Slows your resting rate, which is half of a good BOLT. |
| **4-7-8** | In four, hold seven, out eight. A reliable down-shift before sleep. |
| **Extended exhale** | Exhale about twice the inhale, with a pause on empty. |
| **Reduced breathing** | Buteyko-style light breathing: deliberately less air than you want, for minutes at a time. |
| **Power breathing** | Fast full breaths, then an exhale hold, then a hold on top. Trains composure at the low-oxygen end. Lying down. |
| **Apnea walk** | Short exhale holds taken while walking. Movement drives CO₂ up fast, so the holds bite. |

Tables can hold on **empty lungs** (a normal exhale, then hold — shorter,
sharper, and what transfers to your BOLT) or **full lungs** (the freediving
version — bigger, longer, more about low oxygen).

### Sequences

**Setup → Session → Sequence** runs blocks back to back, each with its own
protocol and settings: coherent breathing into a CO₂ table, a table into a
wind-down, or the BOLT test on the front of anything. Quick start ships
sixteen ready-made sessions, two of them multi-block, and you can save
your own setup alongside them.

### 4-week program

**Setup → Session → 4-week program** is twelve sessions over four weeks, three a
week, from first paced breathing to a full CO₂ table. Every table entry scales
to your current BOLT when you load it, so week four is only as hard as you have
become. Load the next one, hit start, and finishing it ticks it off.

## The chamber

The instrument in the middle of the screen is the whole interface. The iris
opens through an inhale and closes through an exhale; the ring around it fills
through whatever phase you are in; the number inside is time left, or time
elapsed on a hold you end yourself. Tapping the chamber releases an open hold —
easier to hit with your eyes half shut than a button.

## Sounds

Three layers, and each works without the others:

- **The chime** is synthesised in the browser — no file to download, works on a
  first load with no network. It bends up into an inhale and down into an
  exhale, so the cue itself tells you which way to go. Soft, bell or bowl.
- **The guide tone** (optional) is one sustained voice that glides up through
  the inhale, down through the exhale and sits flat on a hold. Turn it on, put
  the phone face down, and follow it with your eyes shut.
- **The coach** speaks the phases, counts the last five seconds of a hold, and
  drops in coaching lines — how many is up to you (**Full**, **Normal**,
  **Sparse**, **Silent**).

The coach is designed around **recorded clips**, the same way Coach Fred's
corner man is: a finite vocabulary of short phrases, each pre-rendered with
ElevenLabs and played back-to-back, so it sounds like a person rather than a
readout. **No pack is committed to this repo yet** — rendering one costs
ElevenLabs credit against your own account, so the toolchain ships instead and
the app falls back to your **device's own speech engine**, which needs no
download. See [VOICE_PACKS.md](VOICE_PACKS.md) to render a pack with your voice.

## Your record

Airlock keeps everything on your device: sessions, holds, total time spent
holding, current and best day streaks, a sessions-per-week strip, personal
bests, a weekly goal, and milestones that light up as you earn them. Your BOLT
readings get their own twelve-week trend. Every finished session is logged
under **Setup → More → Session log**, and all of it travels in the **.airlock**
backup file.

## Themes

Fifteen looks under **Setup → More → Theme**, each supplying nine colours from
which the whole app is mixed — Airlock, Vacuum, Blue hole, Mariana, Apollo,
Soyuz, Nautilus, Aurora, Nitrox, Kelp, Dawn, Moonlight, Ember, Hyperbaric and a
light **Daylight**.

## Install (PWA)

Airlock is an installable Progressive Web App. Open it in a browser and use
**Install app** (Chrome/Edge) or **Add to Home Screen** (Safari) for a
fullscreen, native-feeling app. Once loaded it works **offline** — a service
worker caches the app shell, and the chamber, the chime and the guide tone need
nothing from the network. Icons are rasterised from `icon-source.svg` by
`gen_icons.py`. A service worker needs HTTPS or `localhost`.

## Run locally

```bash
python3 -m http.server 8080
# open http://localhost:8080
```

## Deploy to Render

### Option A: Dashboard
1. Push this folder to a GitHub/GitLab repo.
2. Render Dashboard → **New** → **Static Site**.
3. Pick the repo. **Build Command:** *(blank)*, **Publish Directory:** `.`
4. **Create Static Site**.

### Option B: Blueprint (uses render.yaml)
Render Dashboard → **New** → **Blueprint** → pick the repo → **Apply**.

## Notes

- iOS only speaks after you tap Start. The coach plays through the mute switch
  by default (**Setup → Coaching → Play on silent**); turning that off makes it
  duck under your music instead, but then the mute switch silences it.
- Vibration is Android-only; iOS Safari doesn't expose it to web apps.
- Offline support and install require HTTPS or `localhost` — not a `file://` URL.
