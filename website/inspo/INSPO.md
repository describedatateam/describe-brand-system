# .describe( — graphics direction (phase 2)

Bitmaps and hero sky are pinned. The system is **type as graphics** and **data as the image**, held on **geometry from the mark**. Every device measures or counts something real.

## A. References

| # | Reference | The move worth borrowing |
|---|---|---|
| 1 | [Our World in Data](https://ourworldindata.org) | Opens on counts and gives every chart a source line. **Numbers are the first image, each with its provenance.** |
| 2 | [Studio NAND](https://nand.io) | "Are we right for you?" as three short conditions. Model for *Who we help / not for*. |
| 3 | [Fathom](https://fathom.info) | One plain sentence, no hero picture. |
| 4 | [Tufte, sparklines](https://www.edwardtufte.com/notebook/sparkline-theory-and-practice-edward-tufte/) | "Word-sized graphics" at type resolution. Rulers and counts sit in line with text. |
| 5 | [Isotype](https://en.wikipedia.org/wiki/Isotype_(picture_language)) | More is shown by **more of the same sign, never a bigger sign**. This is the rule for the counting marks. |
| 6 | [Du Bois data portraits](https://dataxdesign.io/chapters/dubois) | Hand-precise charts; new forms when a bar won't show the finding. Licence for the s3 ruler. *(loc.gov returned 403.)* |
| 7 | [Feltron Annual Reports (MoMA)](https://www.moma.org/collection/works/145531) | A year of data set as type: large figure, small label. *(feltron.com timed out.)* |
| 8 | [Whipple Museum: parts of an astrolabe](https://www.whipplemuseum.cam.ac.uk/explore-whipple-collections/astronomy/medieval-astrolabe/parts-astrolabe) | Scales are engraved on the **limb**, the edge: the logic of the spine. |
| 9 | [MHS Oxford astrolabe catalogue](https://www.mhs.ox.ac.uk/astrolabe/) | Islamic and European instruments side by side; Arabic as part of the instrument, not ornament. |
| 10 | [Babylonian cuneiform numerals](https://en.wikipedia.org/wiki/Babylonian_cuneiform_numerals) | Two signs: vertical wedge (1), corner wedge (10). [Akkadian cuneiform was written at Ugarit](https://en.wikipedia.org/wiki/Ugaritic_alphabet); I found no separate Ugaritic numeral signs, so the wedges follow Mesopotamian practice. |
| 11 | [Exchequer tally, Science Museum](https://collection.sciencemuseumgroup.org.uk/objects/co59715/exchequer-tally-and-foil-english-1822-tally-stick) | Notch size encodes the amount; split so **both parties keep a matching record**: "you should be able to check us", made physical. |
| 12 | [Unicode / Adobe tally marks](https://github.com/adobe-fonts/tally-marks) | Tallies are encoded as text (Unicode 11), so they need a text equivalent. |
| 13 | [ZAINA for Mir'a](https://the-brandidentity.com/project/zainas-bilingual-identity-for-mira-unites-arabic-and-latin-scripts-through-shared-punctuation) | Arabic and Latin stacked on one axis, contemporary, not calligraphic. |
| 14 | [29LT](https://www.29lt.com) | Arabic and Latin shown at **matched visual weight**, side by side. |

Not fetched: Reuters Graphics (blocked), dear-data.com (TLS), HSM astrolabe explorer (404).

## B. The graphics system

### Five recurring devices

**1. The measuring edge (page spine).** A 1px `--faint` rule in the left gutter (x = 24px desktop), with minor ticks every 24px and a major tick at each section start. The current section's tick turns `--active` and gets the 4px seated dot (`index_mark`). It mirrors to the right for RTL. On mobile the vertical spine is dropped: each section head gets a full-width `tick_row` instead. *Meaning:* the page is a scale, and you can see where you are on it.

**2. Section numeral plus tally index.** Replaces the small "01 ⊢ label" eyebrow. Fraunces 300 numeral at 96px (56px mobile) in `--body`, with `tally_progress(n, 8)` below it (done ticks `--active`). *Meaning:* position, counted.

**3. Wedge counts.** A cuneiform-style counting mark for small real counts (0–9) only: the five method stages; *Where we are* 1 · 1 · 0; the service facts "4 days" and "2 revisions". The unit wedge's head is cut at 2|θ| = 81.2°, the mark's own angle. Units stack in rows of up to three. **Zero is an empty dashed slot in `--faint`**, the Babylonian empty place, which is the honest way to draw "0 completed projects". Always beside its numeral, `aria-hidden`. No ten-sign on screen: two read as a back arrow (tested). Code: `wedge_number()` in `sketches.py`.

**4. Rulers of real data, drawn to scale.** Every proportion is shown as a segment of a graduated straight rule, never as a pie, donut or dial. Projection lines are dashed `--faint`, the story segment is `--active`, and one coral ring and dot marks the June flagged line (rule stated). Used in the hero (s1) and the proof (s3).

**5. Sight-line annotation.** Elbow leaders (library `leader`) with mono labels of four words or fewer. They replace explanatory sentences in the proof and services, e.g. "Cancellations netted" pointing at −9,251.

Circles live only in the logo and the form's `calibration_loader`.

### The hero

The **source file as a ruler** (s1). The headline and CTA sit left. Under them, `541,909` (rows in the file) in `--body` over a 0–541,909 graduated rule. The clean part (`522,568`) is `--ink`, with the one `--active` index where clean data ends. The 3.6% tail is **magnified ×16 as a vernier**: −5,268 duplicates, −9,251 cancellations, −2,327 postage/fees, −2,495 zero/negative. Caption: *UCI Online Retail, the worked example below.* It is .describe( doing its name: count what's there before analysing. On mobile, magnify ×25 so the vernier fills about 320px, and change the scale label to match.

### Type scale as graphics

| Role | Face | Size (desktop / mobile) | Ink |
|---|---|---|---|
| Hero figure (541,909) | Fraunces 300, lining tabular | clamp(64px, 11vw, 144px) | `--body` |
| Result figure (522,568) | same | 0.75 × hero | `--ink` |
| Section numeral | Fraunces 300 | 96 / 56 | `--body` |
| Headline | Fraunces 300 | clamp(40px, 5.5vw, 72px) | `--ink` |
| Data figures, counts, 37.5% | Fraunces 300 | 44–64 / 36–44 | `--ink` |
| Stage and list heads | Fraunces 300 | 24 | `--ink` |
| Labels | Plex Mono, uppercase | 10.5–11 | `--body` |

**Arabic set large, once:** the existing line «من البيانات إلى القرار» in Amiri at about 1.2× its Latin partner ("From data to decision", Fraunces). The two are stacked on one shared rule in the contact band (refs 13–14): Arabic `dir="rtl"` right-aligned, Latin left-aligned. Only strings Wafa'a has approved.

### What not to do

- No full circles, clock faces, dials, gauges, donuts or pies. Never graduate a full ring.
- Don't draw the mark or an astrolabe large as decoration. The mark stays at logo size, unmodified. The star appears once, in the logo.
- No decorative charts, textures, `cell_field` patterns, dot grids, gradients, blobs, glows or 3D.
- Coral appears in exactly one place: the June flagged line. Never in text.
- No wedges above 9, no wedge without its numeral, no ten-sign.
- At most one `--active` stroke per composition. The greys do the work.
- No mono phrases; labels are four words or fewer.
- Graphics only on hero, method, proof and *Where we are*; other sections get spine and numeral.

## C. Sketch plates (`/home/claude/website/inspo/`)

- `s1-hero-rows-ruler.svg/.png`: hero ruler with the ×16 vernier.
- `s2-spine-and-counts.svg/.png`: spine, section numeral with tally index, method stages in wedges, *Where we are* 1 · 1 · 0.
- `s3-proof-calendar-vs-revenue.svg/.png`: equal calendar months projected onto a revenue-weighted rule. Sep–Nov are 25% of the months and 37.5% of the money. June carries the coral marker.
- `sketches.py` builds all three from `astrolabe.py` and `uci_audit.json` (it asserts the arithmetic). `render.py` rasterises them with the brand fonts.

## D. What I'll check each round

1. **Hero:** is the rows ruler to scale? Do the figures match `uci_audit.json`? Can you read it at 390px?
2. **Spine:** is it present on desktop, replaced by a tick row on mobile, with the active tick tracking the section, mirrored in RTL?
3. **Counts:** are wedges only 0–9, always next to their numeral, with zero as an empty slot?
4. **Colour:** is coral in exactly one place? At most one active stroke per composition? Are greys dominant?
5. **Type:** is the numeral scale as above? Mono labels four words or fewer? Arabic large exactly once, `rtl`, not mixed into English?
6. **Words:** has a diagram or number replaced each paragraph it could?
7. **Design test:** could this be a generic AI startup? Does it survive in one colour? Does it still read with `--faint` deleted?
8. **Dark mode:** do the rulers and wedges hold on navy, with nothing lost to `--faint`?
