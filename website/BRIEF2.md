# .describe( homepage — brief, phase 2

Read `BRIEF.md` first: the output format, brand rules, chart rules, honesty
rules and voice there all still apply. This file says what has **changed**.
Where the two disagree, this file wins.

## What the founder said

1. **"The website is speech heavy."** Too many words. It reads like a document.
2. **The 1-bit al-Sufi bitmaps and the dithered hero sky are not having the
   effect she wanted.** They are **pinned for later**: they come off the page
   now. Don't use `web_assets.json`, the hero sky, or any al-Sufi mask. They
   will be explored later with colour treatment and fuller compositions, but
   not in this phase.
3. **Decide the brand's graphics while building the site.** Three directions
   are in play and can be combined:
   - **Geometry from the mark.** The Role 02 library in `/home/claude/geometry/`
     (`astrolabe.py`, `svg/`, `PRIMITIVES.md`): broken rings, graduated
     sectors, the measuring edge, sight lines, tangent pairs, tallies, orbit,
     construction lines, cell fields. Every shape derives from the mark's
     angle θ = −40.6°. Build with the Python primitives and inline the SVG.
     Obey the library's guards (no fully graduated circle, no closed ring,
     the star appears once, greys do most of the work).
   - **Type as graphics.** Big Fraunces numerals, Latin and Arabic set large,
     counting tallies as marks (the founder wants a flavour of historically
     authentic counting ticks, like Ugaritic/cuneiform tallies).
   - **Data as the image.** Real numbers from `uci_audit.json` doing the
     visual work: big figures, the waterfall, the monthly chart, small
     multiples. **Only real numbers**; never a decorative fake chart.

   The graphics must mean something where they sit (the brand test: a real
   relationship to measurement, information or orientation). No generic
   blobs, gradients, stock imagery or AI-generated pictures.

## Copy: cut it by more than half

The current page has **~2,450 visible words** (outside the chart, table and
form). Target: **≤ 1,100**. Rough budgets:

| Section | Now | Target |
|---|---|---|
| Hero | 84 | ≤ 45 |
| Who we help / not for | 185 | ≤ 110 |
| Services (3) | 488 | ≤ 220 |
| Method (5 stages) | 338 | ≤ 120 |
| Proof | 385 | ≤ 200 |
| Where we are | 62 | ≤ 40 |
| About | 371 | ≤ 140 |
| FAQ | 261 | ≤ 150 (fewer, shorter answers; drop one if it repeats) |
| Contact | 179 | ≤ 80 |

How to cut: say each thing once. Replace paragraphs with a number, a label, a
diagram or a list. Kill throat-clearing and restated premises. Keep every
real fact that matters (prices, days, revisions, the proof numbers, reply
time, languages, Gaza in About, no completed commercial projects yet). Never
invent anything. `python3 /home/claude/website/wordcount.py` prints the count
per section.

## Keep what already works (round 4 fixes — don't regress)

- `html{scroll-padding-block-start}` so focus never hides under the nav.
- Chart tooltip stays with a focused bar on scroll.
- Table-twin headers 10.5px mono; mobile flag note wraps.
- One focus style: the kit's four-corner sighting frame.
- Every interactive target ≥ 24px at 390px wide.
- Run `shoot.py` first (it writes `_preview.html`), then
  `python3 /home/claude/website/a11y_check.py`, which must report: `under nav: []`,
  `small: []`, table headers 10.5px, tooltip after scroll `True`.

## Files

- Start from `/home/claude/website/template.html` + `build.py` (the round-4
  version). Restructure freely.
- Output: `/home/claude/website/site.html` (artifact format: no doctype/html/
  head/body; starts with `<title>`).
- Render: `python3 /home/claude/website/shoot.py <tag>` → `shots/`.
- Inspiration and the graphics direction: `/home/claude/website/inspo/INSPO.md`
  (from the visual agent).

## Stop rule

A critic grade of **9 or 10** ends the loop. 8 or below goes back to the
designer. At most six rounds.

---

## Founder feedback after round 4 (overrides anything above)

1. **Numbers need room.** Some figures don't have a comfortable empty space
   around them. Every big figure (hero, findings, section numerals, services
   figures, the rulers' values) needs clear space on all sides, proportional to
   its size: roughly ≥ 0.5× its cap height above and below, and labels never
   touching a figure or a rule. Check every one at 390 and 1280.
2. **The two graphics at the start of the page collide.** The hero's main
   ruler and the magnified ×16 "vernier" read as overlapping: the dashed
   projection lines cross the space where the labels and the bracket sit, and
   the two rulers are too close. Either separate them with real space so each
   reads alone, or redesign the pair so the relationship is obvious at a
   glance. It must not be hard to read.
3. **The hero sky is back.** She liked the dithered Milky Way hero and says it
   is safe to add. The al-Sufi figures stay pinned; only the sky returns, and
   only in the hero. Two options, and **the agents decide** which is better:
   - **A. Light field** (the earlier one): `/home/claude/illustrations/bitmaps/hero-sky/hero-sky_field.png`,
     2400×1200, Bayer-ordered, painted with `--faint` on the ground colour.
   - **B. Night plate** (her own treatment, rebuilt clean from the original scan
     because her 1600px JPEG can't be upscaled crisply; her reference is
     `inspo/founder-hero-reference.jpg`): dark sky, light stars and Milky Way,
     45° line screen. Masks: `/home/claude/illustrations/bitmaps/hero-night/hero-night_lit.png`
     (2400×1200, 1x screens) and `hero-night_lit@2x.png` (4800×2400, for
     ≥2dppx screens), painted with a light token (e.g. `--ground`/off-white)
     on a navy panel (brand navy #092052 in both themes; her violet hue is off
     palette). Preview: `hero-night_preview-navy.png`. Generator: `hero_night.py`.
   - Side by side at 1:1: `inspo/hero-options-1to1.png`.
   **Pixel perfect, whichever wins:** the mask is shown at its natural size,
   never scaled (`mask-size: 2400px 1200px`, anchored, cropped by the box). For
   B, swap to the @2x file inside `@media (min-resolution: 2dppx)` with the
   same CSS size, so every screen pixel is either lit or not. Verify by
   screenshotting at deviceScaleFactor 1 and 2 and checking a zoomed crop:
   there must be no grey or blurred edge pixels in the dither.
   The sky is atmosphere only: no figure or ruler is drawn on top of it. Text
   on it must pass contrast (for B: light text on navy; clear or darken the
   screen behind the text column if needed). The hero ruler graphic can stay,
   but outside the sky, e.g. directly below the hero band, as the page's first
   data graphic.
