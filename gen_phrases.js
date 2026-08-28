#!/usr/bin/env node
/*
 * Build voice/phrases.json — the complete spoken vocabulary of the app.
 *
 * Airlock's coach only ever says a finite set of short phrases, and every one
 * of them is a recorded clip (see VOICE_PACKS.md). The runtime looks a clip up
 * by slugifying what it is about to say, so the list of phrases and the list of
 * things the app can say must not drift apart. Rather than maintain the list by
 * hand, this script reads them straight out of index.html: the coaching-line
 * pools, the per-phase cue words, and the fixed lines in the speech call sites.
 *
 *     node gen_phrases.js            # -> voice/phrases.json
 *
 * Then render a pack:
 *     python3 gen_voice.py --voice-id <ID> --pack vera --force
 */
const fs = require("fs");
const path = require("path");

const ROOT = __dirname;
const src = fs.readFileSync(path.join(ROOT, "index.html"), "utf8");

/* Pull an object literal out of the source by name and evaluate it. The
   literals are plain data (strings and arrays), so this is safe and it means
   one edit in index.html reaches the phrase list automatically. */
function literal(name) {
  const at = src.indexOf(`const ${name} = {`);
  if (at < 0) throw new Error(`${name} not found in index.html`);
  let i = src.indexOf("{", at), depth = 0, end = -1;
  for (let j = i; j < src.length; j++) {
    if (src[j] === "{") depth++;
    else if (src[j] === "}") { depth--; if (!depth) { end = j + 1; break; } }
  }
  return eval("(" + src.slice(i, end) + ")");
}

// MUST match slugify() in index.html and slug() in gen_voice.py.
const slugify = s => String(s).toLowerCase().trim()
  .replace(/&/g, "and").replace(/['".,!?:;]/g, "")
  .replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");

// How the app splits a spoken line into clip-sized atoms.
const atoms = t => String(t).split(". ").map(s => s.replace(/\.\s*$/, "").trim()).filter(Boolean);

const LINES = literal("LINES");
const CUE_SAY = literal("CUE_SAY");

const out = [];
const seen = new Set();
/* `prev` is a lead-in the renderer passes as previous_text. Short isolated
   words ("Hold") otherwise come back in an unpredictable register — some takes
   land an octave high. A sentence fragment in front anchors them. */
function add(text, style, prev) {
  const slug = slugify(text);
  if (!slug || seen.has(slug)) return;
  seen.add(slug);
  const e = { slug, text, style };
  if (prev) e.prev = prev;
  out.push(e);
}

const CUE_PREV  = "Settle in, and now, ";
const LINE_PREV = "Keep going. ";

// 1. Phase cues — the words the coach says at every phase change.
Object.values(CUE_SAY).forEach(t => add(t, "cue", CUE_PREV));

// 2. Fixed lines from the speech call sites in index.html.
[
  "Breathe up", "Get ready", "Sit comfortably", "Breathe light",
  "Breathe normally through your nose", "Relax",
  "Normal breath out", "Big breath in", "Breathe out",
  "Hold and keep walking", "Session complete", "Nice work",
  "Breathe out, and hold", "Final round"
].forEach(t => add(t, "cue", CUE_PREV));

// 3. Round calls. Twenty is the ceiling on every rounds/cycles dial.
for (let i = 1; i <= 20; i++) add(`Round ${i}`, "cue", CUE_PREV);

// 4. The spoken count into the end of a phase.
["5", "4", "3", "2", "1"].forEach(n => add(n, "cue", "Three, two, "));

// 5. Coaching lines, split the same way the app splits them.
Object.entries(LINES).forEach(([pool, arr]) =>
  arr.forEach(l => atoms(l).forEach(a => add(a, pool === "test" ? "test" : "line", LINE_PREV))));

fs.mkdirSync(path.join(ROOT, "voice"), { recursive: true });
fs.writeFileSync(path.join(ROOT, "voice", "phrases.json"), JSON.stringify(out, null, 1) + "\n");

const byStyle = out.reduce((a, p) => (a[p.style] = (a[p.style] || 0) + 1, a), {});
console.log(`voice/phrases.json: ${out.length} clips`, byStyle);
