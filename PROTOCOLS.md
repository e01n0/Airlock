# Protocols

What each protocol in Airlock is, where the structure comes from, and what it is
actually training. The short version of all of this lives in the app under
**Setup → More → Protocol guide**; this is the long version, plus the numbers.

**Read [the safety section](README.md#safety-first-because-this-one-matters)
first.** Nothing below is worth an injury, and one of these failure modes is
fatal.

---

## The idea underneath all of it

The urge to breathe is driven mostly by **carbon dioxide**, not by a lack of
oxygen. Chemoreceptors watch blood CO₂ (and the pH it shifts) and trigger the
alarm when it rises past a set-point. Habitual over-breathing keeps resting CO₂
low, which drags that set-point down with it — so the alarm fires early, at rest
and under load, and the whole system runs jumpy.

Training **CO₂ tolerance** raises the set-point: the same amount of oxygen, a
later and quieter alarm. That is what every protocol here is aimed at, by two
routes — accumulating CO₂ (holds, shrinking recoveries, air hunger) and reducing
how much you blow off in the first place (slow rates, long exhales, light
breathing).

The one protocol pointed elsewhere is **Power breathing**, which deliberately
*lowers* CO₂ before a hold. It trains composure at the low-oxygen end. Its risks
are different, and worse.

---

## The BOLT score

**Body Oxygen Level Test**, from Patrick McKeown's *Oxygen Advantage* work, and
a close cousin of the Buteyko **Control Pause**:

1. Breathe normally through the nose for a minute or so.
2. Take a normal breath in and let a normal breath out — no big inhale, no
   forced exhale.
3. Pinch your nose and start the clock.
4. Stop at the **first definite urge to breathe** — the first swallow, the first
   twitch of the diaphragm or throat. Not your limit.
5. Your next breath should be calm and through the nose. If you gasp, you held
   too long and the number is not a BOLT.

Rough bands, and how Airlock reads them:

| BOLT | Band | What it means |
|---|---|---|
| < 10s | Very low | Fast, reactive breathing. Coherent breathing and short boxes; no tables yet. |
| 10–20s | Low | The common starting point. Reduced breathing and short CO₂ tables move it fastest. |
| 20–30s | Moderate | Solid. Tables at your score, four or five sessions a week. |
| 30–40s | Good | Comfortable nasal breathing at rest and under light load. |
| 40s+ | Excellent | Athlete range. Maintain it rather than chasing a bigger number. |

**Measure it in the morning**, before coffee and before any breathing practice.
It moves with time of day, food, caffeine and stress, so a reading taken after a
session tells you about the session, not about you. Airlock keeps a twelve-week
trend of the best reading in each week.

### How Airlock scales sessions from it

With **Scale sessions to my score** on (Setup → More), table durations are
computed from your latest BOLT instead of the dials, rounded to five seconds:

| Protocol | Scaling |
|---|---|
| CO₂ table | hold ≈ 0.9 × BOLT · first recovery ≈ 2.4 × BOLT (60–150s) · recovery shrinks by ≈ 0.3 × BOLT each round (5–25s) |
| O₂ table | first hold ≈ 0.8 × BOLT · grows by ≈ 0.25 × BOLT each round · recovery ≈ 3 × BOLT (90–180s) |
| Pyramid | first hold ≈ 0.6 × BOLT · rung ≈ 0.35 × BOLT · recovery ≈ 2.2 × BOLT |
| Apnea walk | hold ≈ 0.7 × BOLT (10–90s) |
| Reduced breathing | pause on empty ≈ 0.25 × BOLT |

These are deliberately conservative. Note especially that a CO₂-table hold sits
**at** your score — a hold you can already do comfortably — so the training
pressure comes from the shrinking recovery rather than from a longer hold. A
table that leaves you gasping is not a harder version of the same stimulus; it
is a different, worse one.

---

## Tables

Freediving's two classic tables, adapted. Both alternate a **breathe-up** window
with a **hold**, and differ only in which one moves.

### CO₂ table
Hold length is fixed; recovery shrinks each round. You start each hold with more
CO₂ still on board than the last, so the same hold gets progressively harder
without ever getting longer. This is the direct CO₂-tolerance table — the one
that moves a BOLT score.

Default: 8 rounds · 45s hold · recovery from 2:00, −15s a round (floor 15s).

### O₂ table
Recovery is fixed and generous; the hold grows each round. You finish each round
further into low oxygen. It builds hold length rather than tolerance.

Default: 8 rounds · hold from 40s, +10s a round · 2:00 recovery.

**Do not run them back to back.** The CO₂ table's whole design is to deny you
full recovery; the O₂ table's is to take you deep on a full one. Alternate days.

### Pyramid table
Holds climb to a peak in the middle and come back down the other side. The
descent is where it earns its place: the same hold that felt long on the way up
arrives easy on the way down, which is a useful thing to feel.

Default: 7 rounds · from 30s · +15s a rung · 90s recovery.

### Full lungs or empty lungs
Every table can hold either way, and it changes what you are training:

- **Empty lungs** (Airlock's default for CO₂ tables) — a *normal* exhale, then
  hold. No oxygen reserve to draw on, so CO₂ climbs fast and the hold is short
  and sharp. This is the Buteyko-shaped version and it transfers straight to
  your BOLT.
- **Full lungs** — the freediving version. A big inhale gives you a reserve, so
  holds are much longer and lean more towards low-oxygen tolerance.

---

## Paced patterns

Each of these is one repeating cycle of inhale / hold / exhale / hold, with any
phase set to zero dropped. Airlock expands them into whole cycles for the
duration you set.

### Box breathing
Equal in, hold, out, hold — 4·4·4·4 by default. Widely used for composure under
stress. The **empty-lung hold at the end of each box** is what makes it CO₂ work
rather than just a calm-down; lengthen the box (5·5·5·5, 6·6·6·6) as it gets
easy.

### Coherent breathing
Around six breaths a minute — 5.5s in, 5.5s out, no holds. The rate where heart
rate and breath fall into step and heart-rate variability peaks. It does not
push CO₂ hard; what it does is lower your resting breathing rate, which is half
of what a good BOLT score is made of.

### 4-7-8
In four, hold seven, out eight, popularised by Andrew Weil. The long hold and
the long exhale both push CO₂ up, and the ratio is a reliable down-shift before
sleep. Four to eight cycles is plenty — it is not meant to be a long session.

### Extended exhale
An exhale roughly twice the inhale, with a pause on empty. Long exhales lean the
whole session parasympathetic; the pause on empty is where the air hunger lives.

### Reduced breathing
Buteyko-style light breathing: deliberately take in **less air than you want**,
so a mild, steady air hunger sits with you for the whole block. Small, slow,
quiet — quiet enough that nobody in the room would hear you.

This is the least dramatic protocol here and one of the most effective, because
it holds a mild CO₂ elevation for minutes rather than seconds. The dose is right
when it is uncomfortable and you could still hold a conversation. If it turns
into panic or gasping, the volume is too low.

Default: 4 rounds of 2 minutes, 3s in · 4s out · 3s pause, with 45 seconds of
normal breathing between rounds.

---

## The two that carry extra risk

### Power breathing
The Wim Hof-shaped round: 30 fast full breaths, then an exhale hold, then one
big breath held on top for 15 seconds.

Understand what it is doing: fast breathing blows CO₂ **off**, which is why the
hold that follows is so long. That makes it a poor CO₂-tolerance protocol and a
good composure protocol — and it means the usual warning signal is muted while
your oxygen falls. **Lie down.** The fainting risk is real and it is the reason
this is the one protocol Airlock warns about in its own settings pane.

Set the hold to zero to hold by feel and tap to release.

### Apnea walk
Walk at an easy pace. On the hold, breathe out normally, pinch your nose and
keep walking until the timer releases you. Movement raises CO₂ far faster than
sitting still, so the holds are short and they bite — a 25-second walking hold
can feel like a minute sitting down.

Level ground, outdoors, nowhere you could fall badly, and nowhere near traffic
or water.

---

## Building a week

Nothing here needs to be long. Twelve to fifteen minutes most days beats an hour
on Sunday, and CO₂ tolerance responds to frequency.

A workable week, and roughly what Airlock's 4-week program does:

- **Every morning:** BOLT test. Thirty seconds, and it is your feedback loop.
- **3–5 ×:** one CO₂ table *or* one reduced-breathing session.
- **1–2 ×:** coherent breathing, 10 minutes, on the days you need less.
- **1 ×:** an apnea walk or an O₂ table, if either appeals.
- **Any evening:** 4-7-8 or extended exhale before sleep — free, and it costs
  you nothing the next morning.

Expect the BOLT score to move over weeks, not days, and expect it to wobble: any
single reading is noise, and the trend strip is the thing to read.

---

## Sources

The structures here are the standard ones from published breathing and
freediving practice, not invented for this app:

- **BOLT** and the nasal-breathing framing — Patrick McKeown, *The Oxygen
  Advantage*.
- **Control Pause, reduced breathing, light breathing** — the Buteyko method.
- **CO₂ and O₂ tables** — standard static-apnea training tables from
  competitive freediving.
- **Coherent / resonance breathing at ~6 breaths per minute** — the resonance
  frequency literature around HRV biofeedback.
- **4-7-8** — Andrew Weil.
- **Power breathing** — the breathing round of the Wim Hof Method.

Airlock is a timer that runs them. It is not medical advice, and it is not a
substitute for a doctor or a qualified instructor.
