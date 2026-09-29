# .describe( — geometric primitives

**ROLE 02 deliverable.** The vocabulary extracted from the locked 5a mark, as
code. Nothing in this folder is a new idea; every primitive is a
generalisation of a relationship that already exists in the logo.

```
astrolabe.py      the generator — constants, primitives, plates
svg/              46 plates, one per primitive, light/dark aware
png/light/        46 plates rastered at 1200px, transparent background
png/dark/         the same 46, in the dark environment
render_png.py     the rasteriser (playwright + chromium)
manifest.json     canon, palette, family notes, plate bodies
PRIMITIVES.md     this file
```

Run `python3 astrolabe.py` to regenerate the vectors, then
`python3 render_png.py` for the rasters — or `python3 render_png.py 2048` for
print. The PNGs carry no background, so a plate drops onto any surface without
bringing a white box with it; use the `light/` set on off-white and the `dark/`
set on navy. For anything that will be resized, recoloured or animated, use the
SVG — the PNGs are for slide decks, documents and hand-off to tools that won't
take vectors.

Import the generator to build anything else:

```python
from astrolabe import broken_ring, radial_scale, tally, polar, THETA, R
```

---

## 1. The derivation

The mark is not a composition of parts. It falls out of **one angle**.

```
θ  = −40.6°        the sight axis
R  = 86            ring radius, on a 200-unit canvas centred at (100,100)
κ  = r/R = 0.4884  the tangent ratio (r = 42)
gap = 28°          the aperture
```

From those four numbers, everything else is forced:

| Element | Where it comes from |
|---|---|
| Star | sits **on** the ring at θ |
| Positional dot | sits on the ring at θ + 180° — antipodal to the star |
| Bowl centre | on the sight axis, at distance `R − r = 44` from the ring centre |
| Tangency | the bowl touches the ring **exactly at the dot** |
| Aperture | 28°, centred on θ — the instrument is open where it is looking |
| Star phase | θ mod 45° = 4.4°, so one of the eight arms lies along θ |
| Long arm | that arm, extended to 30 units — the sighting ray |
| Stem | the vertical tangent to the bowl at its rightmost point |
| Horizontal rule | the bowl's own diameter, terminating at that tangent |

Change θ and the whole mark rotates coherently — ring gap, star, dot, bowl and
stem all follow. That is the grammar, and it is why a chart axis and a loading
state built from this file belong to the same instrument.

`svg/e06-proof.svg` draws the derivation. `svg/z01-mark.svg` rebuilds 5a from
the constants alone and matches the original exactly — the canon verifies
itself. If a future edit breaks that match, the constants are wrong, not the
logo.

### Stroke ratios

One base unit `u = 2`, four weights, nothing in between:

```
ring   4.0   =  2.0u    structure
stem   6.8   =  3.4u    the active stroke — one per composition, at most
mark   3.0   =  1.5u    ticks, pointers, data
hair   1.2   =  0.6u    construction, grids, metadata
```

---

## 2. The families

| | Family | What it is for |
|---|---|---|
| **A** | Arcs | partial circles, broken rings, and the tangency that holds them together |
| **B** | Measurement | ticks, scales, the measuring edge — how the system states a **quantity** |
| **C** | Orientation | crosshairs, sight lines, pointers — how it states a **direction** |
| **D** | Instrument details | pivots, apertures, tabs — what makes it read as a made object |
| **E** | Construction | the generating geometry, left visible rather than cleaned away |
| **F** | Data | axes, points, trajectories, fields — where the identity meets real numbers |
| **G** | Tallies | counting as a functional device: index, position, progress |
| **H** | Orbit | the secondary motif — broken ring plus markers, at every scale |

Each plate in `svg/` is named `<family><nn>-<slug>.svg`.

---

## 3. Rules the code enforces

These are not style notes. They are guards in `astrolabe.py`, so a downstream
asset cannot quietly break them.

**Graduation is never uniform all the way round.** `radial_scale()` raises on a
sweep of 330° or more. A fully graduated circle reads as a clock; a graduated
*sector* reads as an instrument. Asymmetry is the whole difference.

**A closed ring is not a ring.** `broken_ring()` raises on `gap <= 0`. If you
want a plain circle, call `circle()` and know that you have left the vocabulary.

**Coral is never a default.** No primitive reaches for the `mark` class on its
own. `data_series()` takes an explicit list of outlier indices, so coral is
always a judgement someone made about the data — never an automatic rule and
never a way to make a composition more colourful.

**Everything paints with semantic classes**, never raw hex: `ink`, `body`,
`faint`, `active`, `mark`. That is what makes light mode, dark mode and
single-ink the same drawing rather than three drawings. Set the five CSS
variables and the whole library follows.

**`body` and `faint` do most of the work.** The greys are the instrument body.
If a composition is mostly navy and blue, it is wrong.

---

## 4. Class map

```
ink     structure and type          light #092052   dark #F6F8FC
body    instrument body — the grey that carries the drawing
                                    light #64748B   dark #94A3B8
faint   construction, grids, inactive
                                    light #CBD5E1   dark #1E3A6B
active  computational / directional — stems, selection, progress
                                    light #0F58E5   dark #4F86F7
mark    ONLY a genuine outlier      light #E5484D   dark #F0696D
ground  surface                     light #F6F8FC   dark #092052
```

Dark mode is a separate environment, not an inversion: `faint` becomes a deep
blue that belongs on navy, and `active` lifts so it survives the darker ground.

---

## 5. Using the library

Every primitive returns an SVG fragment string. Compose them, then wrap:

```python
from astrolabe import *

body = (broken_ring(cls="body", w=W_MARK)
        + radial_scale(a0=THETA + 30, a1=THETA + 140)
        + index_mark(angle=THETA + 95)
        + tally_progress(7, 12, 36, 180))

open("out.svg", "w").write(svg_doc(body))
```

A few worth knowing by name:

- `measuring_edge()` — the recurring layout device. A vertical ticked rule near
  the margin that headers and content align to. Use it on the site, in decks,
  in reports, in posts. It is the design spine; mirror it for RTL.
- `tangent_pair(show_proof=True)` — the one construction any asset can quote
  when it needs to feel like the logo without drawing the logo.
- `orbit()` / `orbit_frame()` / `calibration_loader()` — the secondary motif.
  The loader is an *alignment*, not a spinner: the ring closes toward the sight
  axis as work completes.
- `cell_field(density=fn)` — the flat-cell texture, 24% gap. `density` is a
  function of `(i, j)`, so the pattern is always a rendering of something real.
- `star()` — eight arms, one long. Do not add a ninth, do not let it collapse
  to a four-point sparkle, and do not use it as a decorative sprinkle: it is a
  sighting target and should appear once.

### Tiers

Small sizes (favicon, avatar, nav, pattern): ring plus dot plus stem, no
graduation, no construction. Large sizes (covers, posters, hero, print): expose
the scale, the construction circles, the leaders. `mark_5a(construction=True)`
is the maximum; anything more is illustration.

---

## 6. Checking your work

Run the brief's final design test against any composition built from this file:

1. Could it belong to a generic AI startup? → if yes, redesign.
2. Is there a real relationship to measurement, information, orientation,
   computation or knowledge? → if no, remove it.
3. Does it use the vocabulary **without drawing an astrolabe**? → if yes, good.
4. Is coral saying something? → if no, remove it.
5. Would it still read as .describe( with the logo removed? → if no, the system
   is too logo-dependent.
6. Does it survive in one colour? → set `ink`, `body`, `faint`, `active` and
   `mark` to the same value and look again.
7. Is the information still clear with the decorative layer gone? → delete
   every `faint` element and check.

Tests 6 and 7 are mechanical with this library, which is most of the reason it
exists.
