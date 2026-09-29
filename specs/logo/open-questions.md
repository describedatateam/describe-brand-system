# `.describe(` — Logo master, open questions

Raised while building `brandkit/logo/` v1.0. Each one is a decision only you can
make. Where I had to pick something to ship, I say what I picked and how to undo it.

**Blocking Phase 02:** Q8 alone. The rest can be answered at leisure — they are
recorded so the choice is explicit rather than inherited by accident.

---

## Q1 — The favicon's ground was a circle on a square canvas ✅ fixed

`5a-favicon.svg` filled its background with `<circle cx="100" cy="100" r="120">`
on a `-20 -20 240 240` canvas. The circle touches the canvas edges but the four
**corners are transparent** — the corner of that square is 169.7 units from the
centre, not 120.

On any platform that composites the icon onto a light surface, or applies its
own mask, the navy field appears as a circle with bitten corners.

**Shipped:** full-bleed `<rect x="-20" y="-20" width="240" height="240">`.

**If a round icon was intended,** say so — it should be an explicit circle at a
deliberate radius with the corners left empty on purpose, not a radius that
happens to reach the edge midpoints.

---

## Q2 — Bright blue on navy is 2.65:1 ⚠️ needs your approval

`5a-reversed.svg` and `5a-favicon.svg` both keep the stem at `BLUE #0F58E5`
against a navy ground or a navy context.

```
BLUE #0F58E5  on  NAVY #092052   =  2.65 : 1
```

That is below every threshold — 3:1 for non-text graphics, 4.5:1 for text. The
stem is the mark's one active element, so it is precisely the part that
disappears. §1.3 already forbids the mirror case ("navy text must never sit on
bright blue"); this is the same collision from the other side.

**Shipped:** dark tiers use `LIGHT_BLUE #5B93FF` — **5.27:1** on navy. §1.3 lists
it as an implementation-only generator colour usable "only when explicitly
approved", and §28 says dark mode "is not a simple colour inversion; it is
separately balanced". This is that separate balancing, and it needs your yes.

**Alternatives if you'd rather not promote `LIGHT_BLUE`:**

| Option | Ratio on navy | Cost |
|---|---|---|
| `LIGHT_BLUE #5B93FF` *(shipped)* | 5.27 | promotes a generator colour to brand status |
| Stem in `OFF_WHITE`, drop the active colour in dark | 14.74 | dark mark loses its one accent |
| Lighten navy to a dark-surface-only value | varies | changes §28's dark surface token |

Change one constant — `LIGHT_BLUE` in `generate_logo.py` — to switch.

---

## Q3 — `stem top = 21.86` is the only number I could not derive

Everything else in the mark falls out of the axis:

```
dot           = bowl centre + 42 · u(139.40°)   ✓ derived
bowl centre   = C + 44 · u(139.40°)             ✓ derived, 44 = 86 − 42, tangent
ring gap      = axis ± 14°                      ✓ derived
star          = C + 86 · u(319.40°)             ✓ derived
alidade tip   = C + 116 · u(319.40°)            ✓ derived
stem x        = bowl centre x + 42 = 108.59     ✓ derived, right tangent
stem bottom   = bowl centre y + 42 = 170.63     ✓ derived, bowl's lowest point
rule          = the bowl's horizontal diameter  ✓ derived

stem top      = 21.86                           ✗ not derivable
```

At x = 108.59 the ring sits at y = 14.43, so the stem stops **7.43 units short of
the ring** — close enough to look intentional, far enough that it isn't tangency.
Its distance from C is 78.61, which is not 86, not 44, not 42.

Three readings, all plausible:

1. **It's deliberate** — the stem is a cursor and stops short of the ring on purpose. Then it should be stated as a ratio (stem length = 148.77 = 1.771 × bowl diameter) so it survives redrawing.
2. **It was meant to touch the ring** at y = 14.43, and 21.86 is drift.
3. **It was meant to touch the ring's bounding box** at y = 12.00 or the canvas grid at y = 20.00.

**Shipped:** 21.86 exactly, preserving the approved mark. Flagged rather than
silently rationalised, because Gate 02 requires "5a proportions unchanged" and I
am not willing to change a proportion on a guess.

---

## Q4 — "Do not add an outward arm to the star" vs the alidade that's already there

§6 states the one locked rule in the whole system:

> **The star remains an upper-right target marker. Do not add an outward arm to it.**

But 5a already carries a 30-unit ray at 319.40°, extending radially outward from
the ring to a tip 116 units from C. That is an outward arm. It is also present in
2b, 4a, 6a and 6b.

It is not decoration. It is collinear with the dot, the bowl centre, the ring
centre and the star — it is the far end of the mark's only axis, and it is the
single feature that stops the graduated ring reading as a clock face.

**Shipped:** preserved exactly, and treated as load-bearing geometry called *the
alidade* throughout the spec.

**The rule needs rewording either way.** Most likely it means "do not add a
*second* arm / do not extend it further", in which case say that. If it genuinely
means the 30-unit ray should go, that is a change to the locked mark and Phase 01
reopens.

---

## Q5 — §6 and §22 disagree about filenames

```
§6  required variants     logo/describe-5a-primary-light.svg
§22 naming convention     logo-5a-primary-light-v1.0.svg
```

§22 is the section that defines the convention and its own examples match it.
§6's list omits the system prefix and the version.

**Shipped:** §22, with §6's variant words (`primary`, `inverted`, `engraved`,
`favicon`, `mark-only`) kept intact, so both sections are satisfied as far as they
can be. Recommend deleting the filenames from §6 and leaving it to name variants
only.

---

## Q6 — What does "inverted" mean?

§6 requires `inverted-light` and `inverted-dark`. §27 describes a "Tier 1 /
inverted mark" for small sizes with engraving, fine graduation and star detail
removed.

Read as *colour*-inverted, `inverted-dark` duplicates `primary-dark`.

**Shipped:** read as §27's **Tier 1 small-use tier** — same geometry, fewer
elements, heavier strokes. `-light` and `-dark` are then the two grounds it can
sit on. I also added `inverted-ink`, which §6 doesn't list but single-ink small
use plainly needs.

If "inverted" was meant to mean "knocked out of a filled container", that is what
the favicon files now are, and the word should move.

---

## Q7 — Two different whites were doing the same job

`5a-reversed.svg` drew the mark in `LIGHT_GREY #CBD5E1`; `5a-favicon.svg` drew the
same mark in `OFF_WHITE #F6F8FC`. §28 sets dark-mode text to `OFF_WHITE`.

**Shipped:** `OFF_WHITE` for all dark-tier ink. `LIGHT_GREY` on navy is 10.55:1
and would also work — but two values for one job is how a system drifts.

Worth noting this is *not* in tension with "light is modelled by desaturating
toward grey rather than moving toward white" — that rule is about modelling
illumination in generated imagery, not about the dark-surface ink token.

---

## Q8 — There is no wordmark 🔴 blocking

None of the 5a files contain letterforms. They are all mark-only. §6 requires
"correct real letterforms" and "approved wordmark letterforms only", and §32's
definition of done needs the lockup.

The wordmark is blocked on §7, which still has two open decisions:

- Latin headings: **Prata or Fraunces** — final choice required
- Arabic headings: **Amiri or El Messiri** — final choice required

Until those land, none of this can be built: the `.describe(|` lockup, the Arabic
`من البيانات إلى القرار` descriptor lockup, lockup clear space, the horizontal
and stacked arrangements, or the RTL mirrored lockup (§8).

**This is the real Phase 01 blocker**, not the mark. Resolving the display face
is the highest-value next decision in the system.

`logo-5a-mark-only-v1.0.svg` exists now as a stable filename so the lockup can be
added later without breaking references.

---

## Q9 — "approximately 24 grid cells" as a minimum size

§27 and §5 both use this phrase, but the base grid is never defined, so "24 grid
cells" has no length.

**Shipped:** read as **24 px**, and tested by rasterising at true pixel size.
The measured answer is that 24px is achievable only by the favicon tier, and only
because it drops the star rays and the dot. §4 of the spec has the full table.

If a grid cell is not a pixel, the minimum-size rule needs restating in px.

---

## Q10 — The sibling variants are still in the export folder

`2b`, `4a`, `6a` and `6b` sit alongside `5a` in
`Logo Design With Astrolabe Inspiration (2)/export/`, with no marker saying which
is canonical. §0 says 5a is locked.

Worth moving them to an `archive/` subfolder so nobody downstream picks one up by
accident. I have not moved or deleted anything.
