#!/usr/bin/env python3
"""
.describe( -- 5a logo master generator
=====================================
Version 1.0

Emits every canonical variant of the 5a astrolabe mark from a single set of
construction constants, so the identity is reproducible from code rather than
from a binary editor file (DESIGN_SYSTEM.md sec.9 acceptance criteria:
"Outputs are reproducible from code").

CONSTRUCTION
------------
The whole mark resolves to ONE axis.

    ring centre  C  = (100, 100)   radius R = 86
    principal axis  = 139.40 deg / 319.40 deg

    On that axis, in order, lie:
        the dot          at  B + 42 * u(139.40)   -- the "." of .describe
        the bowl centre  B  = C + 44 * u(139.40)  -- radius 42
        the ring centre  C
        the star         at  C + 86 * u(319.40)   -- the upper-right target
        the alidade tip  at  C + 116 * u(319.40)  -- the sighting arm

    |CB| = 44 = R - 42, so the bowl is INTERNALLY TANGENT to the ring at the
    139.40 deg point. Nothing here is arbitrary.

    The ring gap is exactly +/- 14 deg about the axis (305.40 -> 333.40),
    so the star sits in the centre of the opening it interrupts.

    The stem sits on the bowl's right tangent (x = B.x + 42 = 108.59) and
    ends on the bowl's lowest point (y = B.y + 42 = 170.63).
    The sighting rule is the bowl's own horizontal diameter.

    The star carries 8 rays on a 45 deg grid based at 4.40 deg, alternating
    6 and 10 units. The four 10-unit rays fall on the principal axis and its
    perpendicular -- they are the axis cross, not decoration. The ray at
    319.40 deg is extended to 30 units: that is the alidade, the sighting arm
    that makes the mark read as an instrument rather than a clock.

NOTE ON FIDELITY TO THE LOCKED MARK
-----------------------------------
This file does not redraw 5a. It derives 5a. Every shape it emits was diffed
against the approved export: the ring, bowl, sighting rule, stem, star centre
and dot are identical, and three of the eight star-ray endpoints differ by
0.01 units (0.004% of the canvas) -- last-digit rounding, nothing more.

That is the point of the rebuild. The approved export was a set of coordinates;
this is the construction those coordinates came from. Change AXIS here and the
dot, bowl, ring gap, star and alidade all move together, because in the real
mark they are one axis, not five decisions.

USAGE
    python3 generate_logo.py <output-dir>
"""

import math
import os
import sys

VERSION = "1.0"

# ---------------------------------------------------------------- palette ---
# DESIGN_SYSTEM.md sec.1.3
NAVY       = "#092052"
BLUE       = "#0F58E5"
CORAL      = "#E5484D"   # not used in the mark -- coral marks outliers only
GREY       = "#64748B"
LIGHT_GREY = "#CBD5E1"
OFF_WHITE  = "#F6F8FC"

# Implementation-only generator colour, sec.1.3: "may be used only when
# explicitly approved". Used here for the dark-tier active stroke because
# BLUE on NAVY measures 2.65:1 -- see specs/logo/open-questions.md Q2.
LIGHT_BLUE = "#5B93FF"

# ----------------------------------------------------------- construction ---
CX, CY   = 100.0, 100.0
R_RING   = 86.0
R_BOWL   = 42.0
D_BOWL   = 44.0            # = R_RING - R_BOWL  -> internal tangency

AXIS     = 319.40          # star / alidade direction
BAXIS    = 139.40          # bowl / dot direction (AXIS - 180)
GAP_HALF = 14.00           # ring opening is AXIS +/- GAP_HALF

R_DOT    = 5.6             # the "." of .describe
R_STAR   = 2.8             # star centre
RAY_BASE = 4.40            # star ray grid origin
RAY_STEP = 45.0
RAY_MINOR, RAY_MAJOR, RAY_ALIDADE = 6.0, 10.0, 30.0

VIEWBOX  = "-20 -20 240 240"    # canonical canvas; see specs/logo clear space


def u(deg):
    r = math.radians(deg)
    return math.cos(r), math.sin(r)


def pt(cx, cy, rad, deg):
    ux, uy = u(deg)
    return cx + rad * ux, cy + rad * uy


def f(v):
    """2dp, trailing zeros stripped -- sec.21.3 wants controlled precision."""
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


BX, BY       = pt(CX, CY, D_BOWL, BAXIS)          # 66.59, 128.63
DOT_X, DOT_Y = pt(BX, BY, R_BOWL, BAXIS)          # 34.70, 155.97
ST_X,  ST_Y  = pt(CX, CY, R_RING, AXIS)           # 165.30, 44.03
GAP_A        = pt(CX, CY, R_RING, AXIS - GAP_HALF)  # 149.82, 29.90
GAP_B        = pt(CX, CY, R_RING, AXIS + GAP_HALF)  # 176.94, 61.59

STEM_X       = BX + R_BOWL                        # 108.59
STEM_BOT     = BY + R_BOWL                        # 170.63
STEM_TOP     = 21.86                              # empirical -- see Q3
RULE_Y       = BY
RULE_X0      = BX - R_BOWL                        # 24.59
RULE_X1      = BX + R_BOWL                        # 108.59

# The bowl, seen from C, occludes the ring from 66.8 deg to 212.0 deg.
# The two free arcs are 212.0->305.4 and 333.4->66.8, each 93.4 deg wide and
# symmetric about the axis. Graduation uses ONE of them, never both, and never
# the full circle (sec.3: uniform graduation "reads as a clock").
GRAD_FROM, GRAD_TO = AXIS + 15.0, AXIS + 105.0    # 334.40 -> 64.40


# ------------------------------------------------------------- primitives ---
def ring(stroke, w):
    """Open ring: the long way round, leaving the 28 deg gap at the axis."""
    return (f'<path d="M{f(GAP_B[0])} {f(GAP_B[1])}'
            f'A{f(R_RING)} {f(R_RING)} 0 1 1 {f(GAP_A[0])} {f(GAP_A[1])}"'
            f' fill="none" stroke="{stroke}" stroke-width="{f(w)}"'
            f' stroke-linecap="round"/>')


def bowl(stroke, w):
    return (f'<circle cx="{f(BX)}" cy="{f(BY)}" r="{f(R_BOWL)}" fill="none"'
            f' stroke="{stroke}" stroke-width="{f(w)}"/>')


def rule(stroke, w):
    return (f'<path d="M{f(RULE_X0)} {f(RULE_Y)}H{f(RULE_X1)}" fill="none"'
            f' stroke="{stroke}" stroke-width="{f(w)}" stroke-linecap="round"/>')


def stem(stroke, w):
    return (f'<path d="M{f(STEM_X)} {f(STEM_TOP)}V{f(STEM_BOT)}" fill="none"'
            f' stroke="{stroke}" stroke-width="{f(w)}" stroke-linecap="round"/>')


def dot(fill):
    return f'<circle cx="{f(DOT_X)}" cy="{f(DOT_Y)}" r="{f(R_DOT)}" fill="{fill}"/>'


def star(stroke, w, simplified=False, alidade=RAY_ALIDADE, r=R_STAR):
    """
    Full star: 8 rays on the 45 deg grid, alternating 6 and 10 units, with the
    319.40 deg ray extended to 30 as the alidade.

    simplified=True keeps the FOUR RAYS PERPENDICULAR TO THE AXIS SET -- the
    4.40 deg group -- at 9 units, plus the alidade. It deliberately does NOT
    keep the four 10-unit axis-cross rays, even though those are the
    structurally important ones: the 139.40 deg ray is collinear with the
    alidade, so keeping that set draws one straight line through the star
    centre and the mark reads as a multiplication sign. Dropping it leaves a
    crosshair with a sighting arm, which is what the star is for.
    (sec.27: "simplify star" at small sizes.)
    """
    segs = []
    if simplified:
        angles = [(RAY_BASE + 90.0 * k, 9.0) for k in range(4)]
    else:
        angles = [(RAY_BASE + RAY_STEP * k,
                   RAY_MAJOR if k % 2 else RAY_MINOR) for k in range(8)]
    for a, length in angles:
        if abs((a - AXIS) % 360.0) < 1e-9:
            continue
        x, y = pt(ST_X, ST_Y, length, a)
        segs.append(f"M{f(ST_X)} {f(ST_Y)}L{f(x)} {f(y)}")
    x, y = pt(ST_X, ST_Y, alidade, AXIS)
    segs.append(f"M{f(ST_X)} {f(ST_Y)}L{f(x)} {f(y)}")
    return (f'<circle cx="{f(ST_X)}" cy="{f(ST_Y)}" r="{f(r)}" fill="{stroke}"/>'
            f'<path d="{"".join(segs)}" fill="none" stroke="{stroke}"'
            f' stroke-width="{f(w)}" stroke-linecap="round"/>')


def graduation(stroke):
    """Partial graduation across ONE free arc only. Ticks read inward."""
    minor, major = [], []
    k = 3
    while True:
        a = AXIS + 5.0 * k
        if a > GRAD_TO + 1e-9:
            break
        depth, bucket = (9.0, major) if k % 3 == 0 else (4.0, minor)
        x0, y0 = pt(CX, CY, R_RING, a)
        x1, y1 = pt(CX, CY, R_RING - depth, a)
        bucket.append(f"M{f(x0)} {f(y0)}L{f(x1)} {f(y1)}")
        k += 1
    return (f'<path d="{"".join(minor)}" fill="none" stroke="{stroke}"'
            f' stroke-width="1.5" stroke-linecap="butt"/>'
            f'<path d="{"".join(major)}" fill="none" stroke="{stroke}"'
            f' stroke-width="2.5" stroke-linecap="butt"/>')


def construction(stroke):
    """Tier 2 only (sec.27: large sizes "permit construction lines")."""
    tip_x, tip_y = pt(CX, CY, R_RING + RAY_ALIDADE, AXIS)
    return (
        f'<circle cx="{f(CX)}" cy="{f(CY)}" r="{f(D_BOWL)}" fill="none"'
        f' stroke="{stroke}" stroke-width="1" stroke-dasharray="5 4"/>'
        f'<path d="M{f(DOT_X)} {f(DOT_Y)}L{f(tip_x)} {f(tip_y)}" fill="none"'
        f' stroke="{stroke}" stroke-width="1" stroke-dasharray="5 4"/>'
        f'<path d="M{f(CX - 9)} {f(CY)}H{f(CX + 9)}M{f(CX)} {f(CY - 9)}V{f(CY + 9)}"'
        f' fill="none" stroke="{stroke}" stroke-width="1" stroke-linecap="round"/>'
        f'<circle cx="{f(CX)}" cy="{f(CY)}" r="2" fill="{stroke}"/>'
    )


# ------------------------------------------------------------------ files ---
def svg(slug, title, desc, body, bg=None):
    """sec.21.1 required root. No width/height: the mark scales to its box."""
    tid, did = f"t-{slug}", f"d-{slug}"
    ground = (f'<rect x="-20" y="-20" width="240" height="240" fill="{bg}"/>'
              if bg else "")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{VIEWBOX}"'
        f' role="img" aria-labelledby="{tid} {did}">'
        f"<title id=\"{tid}\">{title}</title>"
        f"<desc id=\"{did}\">{desc}</desc>"
        f"{ground}{body}</svg>"
    )


def g(name, content):
    """Layer group ids follow sec.25 design-software layer naming."""
    return f'<g id="{name}">{content}</g>'


DESC = ("The .describe( astrolabe mark: an open graduated ring interrupted at "
        "the upper right by a target star, with a tangent bowl, a horizontal "
        "sighting rule and a vertical stem. An instrument for knowing where you "
        "are so you can decide where to go.")


def primary(ink, active, slug, title, bg=None):
    body = (g("RING", ring(ink, 4)) + g("BOWL", bowl(ink, 4))
            + g("RULE", rule(ink, 4)) + g("STEM", stem(active, 6.8))
            + g("STAR", star(ink, 3)) + g("DOT", dot(ink)))
    return svg(slug, title, DESC, body, bg)


def inverted(ink, active, slug, title, bg=None):
    """Tier 1, small use (sec.27): fine detail removed, weights compensated."""
    body = (g("RING", ring(ink, 7)) + g("BOWL", bowl(ink, 7))
            + g("RULE", rule(ink, 7)) + g("STEM", stem(active, 12))
            + g("STAR", star(ink, 5, simplified=True, alidade=20.0))
            + g("DOT", dot(ink)))
    return svg(slug, title, DESC, body, bg)


def favicon(ink, active, slug, title, bg):
    """
    Tier 0, app icon, 16-64px. Tested by rasterising at true pixel size.

    What survives 16px is NOT what the construction says is important. The
    sighting rule survives and earns its place -- it makes the bowl read as an
    instrument rather than a circle. The star's rays and the .describe( dot do
    not: at 16px the dot lands on the bowl's stroke and reads as a bump, and
    the rays dissolve. So the star reduces to a solid point and the dot is
    dropped; both return at the inverted tier (24px and up).

    The ground is a full-bleed square rect. The approved export used
    <circle r="120"> on a square canvas, which left the four corners
    transparent -- see specs/logo/open-questions.md Q1.
    """
    body = (g("RING", ring(ink, 8)) + g("BOWL", bowl(ink, 8))
            + g("RULE", rule(ink, 8)) + g("STEM", stem(active, 13))
            + g("STAR", f'<circle cx="{f(ST_X)}" cy="{f(ST_Y)}" r="8" fill="{ink}"/>'))
    return svg(slug, title, DESC, body, bg)


def engraved(ink, active, con, slug, title, bg=None):
    """Tier 2, large use (sec.27): graduation and construction geometry."""
    body = (g("CONSTRUCTION", construction(con))
            + g("RING", ring(ink, 4) + graduation(ink))
            + g("BOWL", bowl(ink, 4)) + g("RULE", rule(ink, 4))
            + g("STEM", stem(active, 6.8))
            + g("STAR", star(ink, 3)) + g("DOT", dot(ink)))
    return svg(slug, title, DESC, body, bg)


FILES = {
    # --- primary tier: 96px and above ---------------------------------------
    "logo-5a-primary-light":  lambda: primary(NAVY, BLUE,
        "5a-primary-light", ".describe( astrolabe mark, primary, light"),
    "logo-5a-primary-dark":   lambda: primary(OFF_WHITE, LIGHT_BLUE,
        "5a-primary-dark", ".describe( astrolabe mark, primary, dark"),
    "logo-5a-primary-ink":    lambda: primary(NAVY, NAVY,
        "5a-primary-ink", ".describe( astrolabe mark, single ink"),

    # --- inverted / Tier 1: 24-96px -----------------------------------------
    "logo-5a-inverted-light": lambda: inverted(NAVY, BLUE,
        "5a-inverted-light", ".describe( astrolabe mark, small use, light"),
    "logo-5a-inverted-dark":  lambda: inverted(OFF_WHITE, LIGHT_BLUE,
        "5a-inverted-dark", ".describe( astrolabe mark, small use, dark"),
    "logo-5a-inverted-ink":   lambda: inverted(NAVY, NAVY,
        "5a-inverted-ink", ".describe( astrolabe mark, small use, single ink"),

    # --- engraved / Tier 2: 240px and above ---------------------------------
    "logo-5a-engraved-light": lambda: engraved(NAVY, BLUE, GREY,
        "5a-engraved-light", ".describe( astrolabe mark, engraved, light"),
    "logo-5a-engraved-dark":  lambda: engraved(OFF_WHITE, LIGHT_BLUE, GREY,
        "5a-engraved-dark", ".describe( astrolabe mark, engraved, dark"),

    # --- favicon / app icon: 16-64px, ground baked in ------------------------
    "logo-5a-favicon-dark":   lambda: favicon(OFF_WHITE, LIGHT_BLUE,
        "5a-favicon-dark", ".describe( app icon on navy", bg=NAVY),
    "logo-5a-favicon-light":  lambda: favicon(NAVY, BLUE,
        "5a-favicon-light", ".describe( app icon on off-white", bg=OFF_WHITE),

    # --- mark only ----------------------------------------------------------
    # No wordmark exists yet (the Latin display face is undecided), so this is
    # currently identical to primary-light. It is kept as a separate, stable
    # filename so the lockup can be added later without breaking references.
    "logo-5a-mark-only":      lambda: primary(NAVY, BLUE,
        "5a-mark-only", ".describe( astrolabe mark, mark only, no wordmark"),
}


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "brandkit/logo"
    os.makedirs(out, exist_ok=True)
    written = []
    for stem_name, build in FILES.items():
        name = f"{stem_name}-v{VERSION}.svg"
        path = os.path.join(out, name)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(build() + "\n")
        written.append((name, os.path.getsize(path)))
    width = max(len(n) for n, _ in written)
    for name, size in written:
        print(f"  {name:<{width}}  {size:>6,} bytes")
    print(f"\n{len(written)} files written to {out}/")


if __name__ == "__main__":
    main()
