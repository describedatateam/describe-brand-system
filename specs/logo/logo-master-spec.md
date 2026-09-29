# `.describe(` — 5a Logo Master Specification

**Version:** 1.0
**Status:** Production — Phase 01, step 1 of `DESIGN_SYSTEM.md` §31
**Canonical mark:** 5a astrolabe mark
**Supersedes:** `Logo Design With Astrolabe Inspiration (2)/export/5a-*.svg`

---

## 1. What changed, and why

The approved 5a export was a set of coordinates. This is the construction those
coordinates came from.

Every shape in `logo-5a-primary-light-v1.0.svg` was diffed against the approved
`5a-master.svg`. The ring, bowl, sighting rule, stem, star centre and dot are
identical. Three of the eight star-ray endpoints differ by 0.01 units —
0.004% of the canvas, last-digit rounding. **The mark has not been redesigned.**

What the rebuild fixes:

| | Approved export | v1.0 master |
|---|---|---|
| File weight | 8,754 B, of which ~7,700 B is C2PA metadata | 1,394 B, no metadata |
| Root element | `width="2000" height="2000"`, no `role` | `viewBox` only, `role="img"` + `<title>`/`<desc>` |
| Layers | flat | grouped `RING BOWL RULE STEM STAR DOT` per §25 |
| Favicon ground | `<circle r="120">` — corners transparent | full-bleed `<rect>` |
| Dark-tier ink | `#CBD5E1` in `-reversed`, `#F6F8FC` in `-favicon` | `#F6F8FC` throughout, per §28 |
| Dark-tier stem | `#0F58E5` on navy — **2.65:1** | `#5B93FF` — 5.27:1 (see Q2) |
| Size tiers | one drawing at all sizes | three tiers, each rasteriser-tested |
| Source of truth | binary export | `generate_logo.py` |

---

## 2. Construction

The whole mark resolves to **one axis**.

```
ring centre      C = (100, 100)        radius R = 86
principal axis     = 139.40° / 319.40°
```

On that axis, in order, lie:

```
the dot           B + 42 · u(139.40°)     = (34.70, 155.97)   r = 5.6
the bowl centre   B = C + 44 · u(139.40°) = (66.59, 128.63)   r = 42
the ring centre   C                       = (100.00, 100.00)
the star          C + 86 · u(319.40°)     = (165.30,  44.03)  r = 2.8
the alidade tip   C + 116 · u(319.40°)    = (188.08,  24.51)
```

`|CB| = 44 = 86 − 42`, so **the bowl is internally tangent to the ring** at the
139.40° point. The ring gap is exactly **±14° about the axis** (305.40° → 333.40°),
so the star sits in the centre of the opening it interrupts.

The remaining elements hang off the bowl:

```
stem          x = B.x + 42 = 108.59   (the bowl's right tangent)
              y = 21.86 → 170.63      (170.63 = B.y + 42, the bowl's lowest point)
sighting rule y = 128.63              (the bowl's horizontal diameter)
              x = 24.59 → 108.59
```

The star carries 8 rays on a 45° grid based at 4.40°, alternating 6 and 10 units.
The four 10-unit rays fall on the principal axis and its perpendicular — they are
the axis cross, not decoration. The ray at 319.40° extends to 30 units: **the
alidade**, the sighting arm that makes the mark an instrument rather than a clock.

**Nothing above is arbitrary except `stem top = 21.86`.** See Q3.

### Base grid

```
canvas    240 × 240 units, viewBox "-20 -20 240 240"
mark bbox x [12.00, 189.58]  y [12.00, 188.00]   →  177.58 × 176.00
precision 2 decimal places (§21.3)
```

---

## 3. Tiers

Three drawings, not one. Each was rasterised at true pixel size and inspected,
not assumed.

### Tier 0 — favicon / app icon · **16–48 px**

`logo-5a-favicon-light` · `logo-5a-favicon-dark`

Ring, bowl, sighting rule, stem, solid star point. Ground baked in as a
full-bleed square.

What survives 16px is not what the construction says matters. **The sighting
rule survives and earns its place** — it makes the bowl read as an instrument
rather than a circle. The star's rays and the `.describe(` dot do not: at 16px
the dot lands on the bowl's stroke and reads as a bump, and the rays dissolve.
So the star reduces to a solid point and the dot is dropped. Both return at
Tier 1.

Strokes: ring/bowl/rule 8, stem 13.

### Tier 1 — inverted / small use · **32–96 px**

`logo-5a-inverted-light` · `-dark` · `-ink`

Full element set, star simplified to a **crosshair plus alidade**: the four rays
of the 4.40° group at 9 units.

It deliberately does *not* keep the four 10-unit axis-cross rays, even though
those are the structurally important ones. The 139.40° ray is collinear with the
alidade, so keeping that set draws one straight line through the star centre and
the mark reads as a multiplication sign. Dropping it leaves a crosshair with a
sighting arm — which is what the star is for.

Strokes: ring/bowl/rule 7, stem 12, star ray 5.

### Tier 2 — primary · **96 px and up**

`logo-5a-primary-light` · `-dark` · `-ink` · and `logo-5a-mark-only`

The canonical mark. Strokes: ring/bowl/rule 4, stem 6.8, star ray 3.

### Tier 3 — engraved · **240 px and up**

`logo-5a-engraved-light` · `-dark`

Primary plus partial graduation and construction geometry (§27: large sizes
"permit partial graduation… permit construction lines").

Graduation runs **334.40° → 64.40°** only — one of the two free arcs, never the
full circle (§3: uniform graduation "reads as a clock"). Seen from C the bowl
occludes the ring from 66.8° to 212.0°, leaving free arcs of 212.0°→305.4° and
333.4°→66.8°, each 93.4° wide and symmetric about the axis. Graduating one and
not the other is the asymmetry that §30 asks to be intentional.

Ticks read inward: minor 4 units at stroke 1.5, major 9 units at stroke 2.5, on
the star's own 5° grid so the graduation and the star share one origin.

Construction layer: the r=44 bowl-centre locus (dashed), the principal axis from
dot to alidade tip (dashed), a centre crosshair and the pivot point — all in
`GREY #64748B`, 3.29:1 on navy and 4.48:1 on off-white.

---

## 4. Minimum size

Measured, not estimated. A stroke needs **≥ 1.0 device px** to render reliably.

Stroke width in device px, by render size (canvas = 240 units):

| | 16 | 24 | 32 | 48 | 64 | 96 | 128 | 240 |
|---|---|---|---|---|---|---|---|---|
| **Tier 0** ring/bowl/rule (8) | 0.53 | 0.80 | 1.07 | 1.60 | 2.13 | 3.20 | 4.27 | 8.00 |
| **Tier 0** stem (13) | 0.87 | 1.30 | 1.73 | 2.60 | 3.47 | 5.20 | 6.93 | 13.00 |
| **Tier 1** ring/bowl/rule (7) | 0.47 | 0.70 | **0.93** | 1.40 | 1.87 | 2.80 | 3.73 | 7.00 |
| **Tier 1** star ray (5) | 0.33 | 0.50 | 0.67 | **1.00** | 1.33 | 2.00 | 2.67 | 5.00 |
| **Tier 2** ring/bowl/rule (4) | 0.27 | 0.40 | 0.53 | 0.80 | 1.07 | **1.60** | 2.13 | 4.00 |
| **Tier 2** star ray (3) | 0.20 | 0.30 | 0.40 | 0.60 | 0.80 | **1.20** | 1.60 | 3.00 |
| **Tier 3** minor tick (1.5) | 0.10 | 0.15 | 0.20 | 0.30 | 0.40 | 0.60 | 0.80 | **1.50** |
| **Tier 3** construction (1) | 0.07 | 0.10 | 0.13 | 0.20 | 0.27 | 0.40 | 0.53 | **1.00** |

**Absolute floor: 16 px, Tier 0 only.** Below that the ring gap closes and the
mark stops being the mark.

---

## 5. Clear space

```
X = 2½ dot-diameters = 28 units
```

The dot is the `.` of `.describe` — the most quotable element in the mark, and
the one a non-designer can count. Clear space is **X on every side**, measured
from the mark's bounding box.

The canonical canvas already bakes this in: the tightest margin in the master
files is 30.42 units (2.72 X) on the right, where the alidade tip runs out.
**So the SVG can be placed flush against other content and clear space is
satisfied automatically.** Do not add padding on top of the file's own canvas,
and do not crop the viewBox to the mark.

Nothing enters X: no type, no rules, no measuring edge, no image edge.

---

## 6. Colourways

| Variant | Ink | Active (stem) | Ground | Contrast |
|---|---|---|---|---|
| `primary-light` | `NAVY #092052` | `BLUE #0F58E5` | `OFF_WHITE #F6F8FC` | 14.74:1 / 5.57:1 |
| `primary-dark` | `OFF_WHITE #F6F8FC` | `LIGHT_BLUE #5B93FF` | `NAVY #092052` | 14.74:1 / 5.27:1 |
| `primary-ink` | `NAVY #092052` | `NAVY #092052` | any light ground | 14.74:1 |

Measured ratios across the palette:

| | on `OFF_WHITE` | on `NAVY` |
|---|---|---|
| `NAVY #092052` | **14.74** | — |
| `OFF_WHITE #F6F8FC` | — | **14.74** |
| `BLUE #0F58E5` | **5.57** | ✗ 2.65 |
| `LIGHT_BLUE #5B93FF` | ✗ 2.80 | **5.27** |
| `LIGHT_GREY #CBD5E1` | ✗ 1.40 | **10.55** |
| `GREY #64748B` | 4.48 | 3.29 |
| `MID_BLUE #14357F` | **10.70** | ✗ 1.38 |

`BLUE` and `LIGHT_BLUE` are not interchangeable — each fails on the other's
ground. §28's "dark mode is not a simple colour inversion; it is separately
balanced" is doing real work here. See **Q2**.

`CORAL` never appears in the mark. It marks genuine outliers in data, nothing else.

### Single ink

`primary-ink` and `inverted-ink` are one colour throughout, no opacity, no
dashes at the primary tier. Safe for foil, engraving, embroidery, fax-grade
reproduction and one-plate print. The engraved tier has **no** single-ink
variant: its construction layer needs a second value to sit back from the mark.

---

## 7. Rules

**Do**

- Use the tier that matches the render size. Three files exist because one drawing cannot serve 16px and 2000px.
- Let the file's own canvas provide clear space.
- Use `primary-ink` whenever reproduction is uncertain.
- Keep the alidade pointing up-right. It is the mark's orientation.

**Do not**

- Add an outward arm to the star (§6). The 30-unit alidade at 319.40° is existing, load-bearing geometry — see **Q4** — but nothing is added to it.
- Rotate, mirror, skew or reflow the mark. The axis is the meaning.
- Recolour the stem to `CORAL`, or to `BLUE` on a navy ground.
- Graduate the full ring.
- Place the mark on `BLUE #0F58E5`: navy on bright blue is 2.65:1 and §1.3 forbids it outright.
- Embed a white box behind the mark. All non-favicon files are transparent.
- Re-export from a drawing app and overwrite these files. Edit `generate_logo.py` and regenerate.

---

## 8. Files

```
brandkit/logo/
  logo-5a-primary-light-v1.0.svg      Tier 2   96px+     transparent
  logo-5a-primary-dark-v1.0.svg       Tier 2   96px+     transparent
  logo-5a-primary-ink-v1.0.svg        Tier 2   96px+     transparent, 1 colour
  logo-5a-inverted-light-v1.0.svg     Tier 1   32–96px   transparent
  logo-5a-inverted-dark-v1.0.svg      Tier 1   32–96px   transparent
  logo-5a-inverted-ink-v1.0.svg       Tier 1   32–96px   transparent, 1 colour
  logo-5a-engraved-light-v1.0.svg     Tier 3   240px+    transparent
  logo-5a-engraved-dark-v1.0.svg      Tier 3   240px+    transparent
  logo-5a-favicon-light-v1.0.svg      Tier 0   16–48px   ground baked in
  logo-5a-favicon-dark-v1.0.svg       Tier 0   16–48px   ground baked in
  logo-5a-mark-only-v1.0.svg          Tier 2   96px+     transparent
  generate_logo.py                    source of truth
```

`mark-only` is currently identical to `primary-light`, because **no wordmark
exists yet**. It is kept as a separate stable filename so the lockup can be
added later without breaking references. See **Q8** — the lockup is blocked on
the Latin display face decision (§7: Prata vs Fraunces).

Naming follows §22 `<system>-<family>-<variant>-<size>-v<major>.<minor>.svg`,
which conflicts with the filenames listed in §6. See **Q5**.

---

## 9. Regenerating

```bash
python3 generate_logo.py brandkit/logo
```

No dependencies. Every constant is at the top of the file. Change `AXIS` and the
dot, bowl, ring gap, star, alidade and graduation all move together — because in
the real mark they are one axis, not five decisions.
