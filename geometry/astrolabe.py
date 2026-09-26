"""
astrolabe.py — .describe( geometric primitive library
=====================================================

Every primitive in this file is derived from the locked 5a mark. Nothing here
is a new invention: the constants block below is measured off 5a-master.svg,
and each primitive is a generalisation of a relationship that already exists
in the logo.

THE DERIVATION
--------------
The whole mark falls out of a single angle.

    THETA = -40.6 deg      the sight axis

  · the star sits ON the ring at THETA
  · the positional dot sits on the ring at THETA + 180
  · the bowl is internally tangent to the ring AT THAT DOT, so its centre
    lies on the sight axis at distance (R - r) from the ring centre
  · the ring's aperture is a 28 deg gap centred on THETA — the instrument is
    open exactly where it is looking
  · the star's 8 arms are phased so one arm lies along the sight axis
    (THETA mod 45 = 4.4 deg), and that arm is the long one
  · the stem is the vertical tangent to the bowl at its rightmost point
  · the horizontal rule is the bowl's own diameter, ending at that tangent

Change THETA and the entire mark rotates coherently. That is the grammar.
Every primitive below either uses the sight axis, the tangent ratio, or the
28 deg aperture — which is why a chart axis and a loading state built from
this file look like the same instrument.

    KAPPA = r / R = 42 / 86 = 0.4884     the tangent ratio
    GAP   = 28 deg                        the aperture

RULES ENCODED IN CODE
---------------------
  · graduation is never uniform all the way round (guarded in radial_scale) —
    a fully graduated circle reads as a clock, not an instrument
  · coral is never a default; it is only ever passed explicitly to mark an
    outlier (see data_series)
  · everything survives in one ink (classes degrade to a single stroke)

Usage
-----
    python3 astrolabe.py            writes svg/ and manifest.json
    from astrolabe import broken_ring, polar, THETA

Author: generated for .describe( — geometry workstream (ROLE 02)
"""

from __future__ import annotations

import json
import math
import os
import random

# ---------------------------------------------------------------------------
# 1. CANON — measured from 5a-master.svg. Do not edit without re-measuring.
# ---------------------------------------------------------------------------

CX, CY = 100.0, 100.0      # ring centre, on a 200-unit canvas
R = 86.0                   # ring radius
THETA = -40.6              # sight axis, degrees, screen coords (y down)
GAP = 28.0                 # ring aperture, degrees, centred on THETA
R_BOWL = 42.0              # inner tangent circle
KAPPA = R_BOWL / R         # 0.48837 — the tangent ratio
DOT_R = 5.6                # positional dot
STAR_ARM = 6.0             # orthogonal arm
STAR_DIAG = 10.0           # diagonal arm
STAR_SIGHT = 30.0          # the arm along the sight axis
BLEED = 20.0               # canvas overscan, as in the logo's viewBox

U = 2.0                    # base stroke unit
W_RING = 2.0 * U           # 4.0   structure
W_STEM = 3.4 * U           # 6.8   the active stroke
W_MARK = 1.5 * U           # 3.0   marks and ticks
W_HAIR = 0.6 * U           # 1.2   construction and metadata

PALETTE = {
    "navy": "#092052",
    "blue": "#0F58E5",
    "coral": "#E5484D",
    "grey": "#64748B",
    "light": "#CBD5E1",
    "offwhite": "#F6F8FC",
    "negative": "#8C1D1D",
    "positive": "#0F7B3D",
}

# Semantic classes. Every primitive paints with these, never with raw hex, so
# that light mode, dark mode and single-ink are the same drawing.
#   ink     structure and type
#   body    instrument body — the grey that does most of the work
#   faint   construction, grids, inactive
#   active  the computational/directional stroke
#   mark    ONLY a genuine outlier

STYLE_LIGHT = {
    "ink": "#092052", "body": "#64748B", "faint": "#CBD5E1",
    "active": "#0F58E5", "mark": "#E5484D", "ground": "#F6F8FC",
}
STYLE_DARK = {
    "ink": "#F6F8FC", "body": "#94A3B8", "faint": "#1E3A6B",
    "active": "#4F86F7", "mark": "#F0696D", "ground": "#092052",
}

# ---------------------------------------------------------------------------
# 2. PRIMITIVE MATHS
# ---------------------------------------------------------------------------


def polar(cx: float, cy: float, r: float, deg: float) -> tuple[float, float]:
    """Point at radius r and angle deg from (cx, cy). Screen coords, y down."""
    a = math.radians(deg)
    return (cx + r * math.cos(a), cy + r * math.sin(a))


def f(v: float) -> str:
    """Format a number for SVG: 2dp, no trailing zeros."""
    return f"{v:.2f}".rstrip("0").rstrip(".")


def arc_path(cx: float, cy: float, r: float, a0: float, a1: float) -> str:
    """Arc path data from a0 to a1, sweeping clockwise (increasing angle)."""
    sweep = (a1 - a0) % 360
    x0, y0 = polar(cx, cy, r, a0)
    x1, y1 = polar(cx, cy, r, a1)
    large = 1 if sweep > 180 else 0
    return f"M{f(x0)} {f(y0)}A{f(r)} {f(r)} 0 {large} 1 {f(x1)} {f(y1)}"


# ---------------------------------------------------------------------------
# 3. SVG ELEMENT HELPERS
# ---------------------------------------------------------------------------


def _attrs(cls: str, w: float | None, fill: str, extra: dict | None) -> str:
    a = [f'class="{cls}"']
    if w is not None:
        a.append(f'stroke-width="{f(w)}"')
    a.append(f'fill="{fill}"')
    for k, v in (extra or {}).items():
        a.append(f'{k}="{v}"')
    return " ".join(a)


def path(d: str, cls="ink", w=W_MARK, fill="none", **extra) -> str:
    return f'<path d="{d}" {_attrs(cls, w, fill, extra)}/>'


def circle(cx, cy, r, cls="ink", w=W_MARK, fill="none", **extra) -> str:
    return (f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" '
            f'{_attrs(cls, w, fill, extra)}/>')


def dot(cx, cy, r=3.0, cls="ink", **extra) -> str:
    return (f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" '
            f'{_attrs(cls + " fill", None, "currentColor", extra)}/>')


def line(x0, y0, x1, y1, cls="ink", w=W_MARK, **extra) -> str:
    return path(f"M{f(x0)} {f(y0)}L{f(x1)} {f(y1)}", cls, w, **extra)


def text(x, y, s, cls="ink", size=9, anchor="start", mono=True, **extra) -> str:
    fam = "'IBM Plex Mono', ui-monospace, monospace" if mono else \
          "'IBM Plex Sans Arabic', system-ui, sans-serif"
    ex = " ".join(f'{k}="{v}"' for k, v in extra.items())
    return (f'<text x="{f(x)}" y="{f(y)}" class="{cls} fill" fill="currentColor" '
            f'font-size="{size}" font-family="{fam}" text-anchor="{anchor}" '
            f'letter-spacing="0.06em" {ex}>{s}</text>')


# ---------------------------------------------------------------------------
# 4. FAMILY A — ARCS
# ---------------------------------------------------------------------------


def ring_arc(cx=CX, cy=CY, r=R, a0=0.0, a1=90.0, cls="ink", w=W_RING) -> str:
    """A partial ring. The atom of the whole system."""
    return path(arc_path(cx, cy, r, a0, a1), cls, w, **{"stroke-linecap": "round"})


def broken_ring(cx=CX, cy=CY, r=R, gap=GAP, axis=THETA, cls="ink", w=W_RING) -> str:
    """The canonical ring: closed except for an aperture centred on the axis.

    The gap is not decoration — it is where the instrument is looking.
    """
    if gap <= 0:
        raise ValueError("a closed ring is not an instrument; use circle()")
    return ring_arc(cx, cy, r, axis + gap / 2, axis - gap / 2, cls, w)


def interrupted_ring(cx=CX, cy=CY, r=R, n=3, gap=10.0, axis=THETA,
                     cls="body", w=W_RING) -> str:
    """A ring broken into n unequal segments — asymmetric by construction."""
    out, spans, total = [], [], 360 - n * gap
    # deliberately unequal: segments follow 3:2:2:1... so it never reads as a dial
    weights = [3, 2, 2, 1, 1, 1][:n] or [1]
    s = sum(weights)
    a = axis + gap / 2
    for wt in weights:
        span = total * wt / s
        spans.append(span)
        out.append(ring_arc(cx, cy, r, a, a + span, cls, w))
        a += span + gap
    return "".join(out)


def nested_rings(cx=CX, cy=CY, r=R, n=3, ratio=KAPPA, gap=GAP, axis=THETA,
                 cls="body", w=W_HAIR) -> str:
    """Rings stepping inward by the tangent ratio. Each is broken on the axis."""
    out = []
    for i in range(n):
        rr = r * ratio ** i
        out.append(broken_ring(cx, cy, rr, gap * (1 + i * 0.6), axis,
                               cls if i else "ink", w if i else W_RING))
    return "".join(out)


def tangent_pair(cx=CX, cy=CY, r=R, ratio=KAPPA, axis=THETA,
                 show_proof=False) -> str:
    """The logo's core relation: inner circle internally tangent at -axis.

    This is the one construction every downstream asset can quote.
    """
    ri = r * ratio
    bx, by = polar(cx, cy, r - ri, axis + 180)
    tx, ty = polar(cx, cy, r, axis + 180)
    out = [broken_ring(cx, cy, r, GAP, axis),
           circle(bx, by, ri, "ink", W_RING)]
    if show_proof:
        out += [line(*polar(cx, cy, r, axis), *polar(cx, cy, r, axis + 180),
                     "faint", W_HAIR, **{"stroke-dasharray": "4 4"}),
                dot(cx, cy, 2.0, "faint")]
    out.append(dot(tx, ty, DOT_R, "ink"))
    return "".join(out)


def offset_arcs(cx=CX, cy=CY, r=R, n=5, step=0.13, axis=THETA,
                cls="faint", w=W_HAIR) -> str:
    """Concentric arcs whose sweep narrows as they approach the axis."""
    out = []
    for i in range(n):
        rr = r * (1 - i * step)
        span = 150 - i * 22
        out.append(ring_arc(cx, cy, rr, axis - span / 2, axis + span / 2,
                            "active" if i == n - 1 else cls,
                            W_MARK if i == n - 1 else w))
    return "".join(out)


# ---------------------------------------------------------------------------
# 5. FAMILY B — MEASUREMENT
# ---------------------------------------------------------------------------


def tick_row(x0, y0, length=100.0, count=21, major_every=5, minor=5.0,
             major=11.0, vertical=False, cls="body", w=W_HAIR) -> str:
    """A calibrated rule. Majors are ~2.2x minors, the logo's 4:1.8 ratio."""
    out = []
    for i in range(count):
        t = 0 if count == 1 else i / (count - 1)
        h = major if i % major_every == 0 else minor
        if vertical:
            y = y0 + t * length
            out.append(line(x0, y, x0 + h, y, cls, w))
        else:
            x = x0 + t * length
            out.append(line(x, y0, x, y0 - h, cls, w))
    return "".join(out)


def measuring_edge(x=26.0, y0=18.0, y1=182.0, count=17, major_every=4,
                   labels=None, cls="body") -> str:
    """THE recurring layout device: a vertical ticked rule at the margin.

    Headers and content align to it; it is the design spine.
    """
    out = [line(x, y0, x, y1, cls, W_HAIR)]
    out.append(tick_row(x, y0, y1 - y0, count, major_every, 4.0, 9.0,
                        vertical=True, cls=cls, w=W_HAIR))
    if labels:
        for i, lab in enumerate(labels):
            t = i / max(len(labels) - 1, 1)
            out.append(text(x + 14, y0 + t * (y1 - y0) + 3, lab, cls, 8))
    return "".join(out)


def radial_scale(cx=CX, cy=CY, r=R, a0=None, a1=None, step=3.0,
                 major_every=5, inward=True, cls="body", w=W_HAIR) -> str:
    """Graduation over a SECTOR only.

    Guarded: a scale that closes the full circle reads as a clock face, which
    the identity explicitly rejects. Asymmetry is what makes it an instrument.
    """
    a0 = THETA - 62 if a0 is None else a0
    a1 = THETA + 62 if a1 is None else a1
    if abs(a1 - a0) >= 330:
        raise ValueError(
            "radial_scale refuses a near-complete sweep: uniform graduation "
            "all the way round reads as a clock. Graduate a sector."
        )
    out, i, a = [], 0, a0
    while a <= a1 + 1e-9:
        h = 10.0 if i % major_every == 0 else 4.5
        d = -h if inward else h
        out.append(line(*polar(cx, cy, r, a), *polar(cx, cy, r + d, a), cls, w))
        a += step
        i += 1
    return "".join(out)


def index_mark(cx=CX, cy=CY, r=R, angle=THETA, cls="active") -> str:
    """A single graduation singled out: longer tick plus a seated dot."""
    x0, y0 = polar(cx, cy, r - 15, angle)
    x1, y1 = polar(cx, cy, r + 7, angle)
    return line(x0, y0, x1, y1, cls, W_MARK) + dot(*polar(cx, cy, r, angle), 4.0, cls)


def dimension(x0, y0, x1, y1, label="", cls="faint", off=9.0,
              label_cls="body") -> str:
    """A measured distance with end serifs and a mono label."""
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L * off / 2, dx / L * off / 2
    out = [line(x0, y0, x1, y1, cls, W_HAIR),
           line(x0 - nx, y0 - ny, x0 + nx, y0 + ny, cls, W_HAIR),
           line(x1 - nx, y1 - ny, x1 + nx, y1 + ny, cls, W_HAIR)]
    if label:
        # sit the label clear of the rule, on the perpendicular
        px, py = -dy / L, dx / L
        if py > 0:
            px, py = -px, -py
        out.append(text((x0 + x1) / 2 + px * 10, (y0 + y1) / 2 + py * 10 + 3,
                        label, label_cls, 8, anchor="middle"))
    return "".join(out)


# ---------------------------------------------------------------------------
# 6. FAMILY C — ORIENTATION
# ---------------------------------------------------------------------------


def crosshair(cx=CX, cy=CY, r=26.0, gap=8.0, cls="ink", w=W_MARK) -> str:
    """Sighting crosshair: four rules that stop short of the target point."""
    return "".join([
        line(cx - r, cy, cx - gap, cy, cls, w),
        line(cx + gap, cy, cx + r, cy, cls, w),
        line(cx, cy - r, cx, cy - gap, cls, w),
        line(cx, cy + gap, cx, cy + r, cls, w),
        dot(cx, cy, 2.4, cls),
    ])


def sight_line(cx=CX, cy=CY, r_in=0.0, r_out=R + 30, angle=THETA,
               cls="ink", w=W_MARK) -> str:
    """A radial rule that continues past the ring — the star's 30-unit ray."""
    return line(*polar(cx, cy, r_in, angle), *polar(cx, cy, r_out, angle), cls, w)


def radial_fan(cx=CX, cy=CY, r0=52.0, r1=R, a0=None, a1=None, n=9,
               cls="faint", w=W_HAIR) -> str:
    """Sighting lines across a sector."""
    a0 = THETA - 55 if a0 is None else a0
    a1 = THETA + 55 if a1 is None else a1
    return "".join(
        line(*polar(cx, cy, r0, a0 + (a1 - a0) * i / (n - 1)),
             *polar(cx, cy, r1, a0 + (a1 - a0) * i / (n - 1)), cls, w)
        for i in range(n))


def pointer(cx=CX, cy=CY, r=R, angle=THETA, length=26.0, cls="active") -> str:
    """A directional indicator: shaft plus an open V head, no filled arrow."""
    tipx, tipy = polar(cx, cy, r, angle)
    bx, by = polar(cx, cy, r - length, angle)
    h = 8.0
    l1 = polar(tipx, tipy, h, angle + 145)
    l2 = polar(tipx, tipy, h, angle - 145)
    return "".join([
        line(bx, by, tipx, tipy, cls, W_MARK),
        path(f"M{f(l1[0])} {f(l1[1])}L{f(tipx)} {f(tipy)}L{f(l2[0])} {f(l2[1])}",
             cls, W_MARK, **{"stroke-linejoin": "round", "stroke-linecap": "round"}),
    ])


def star(cx=None, cy=None, phase=None, sight=STAR_SIGHT, cls="ink") -> str:
    """The 5a asterisk, generalised. Eight arms; the sight-axis arm is long.

    Do NOT add a ninth arm, and do not let it collapse to a 4-point sparkle.
    """
    if cx is None or cy is None:
        cx, cy = polar(CX, CY, R, THETA)
    phase = THETA if phase is None else phase
    out = []
    for k in range(8):
        a = phase + 45 * k
        if k == 0:
            L = sight
        else:
            L = STAR_DIAG if k % 2 == 0 else STAR_ARM
        out.append(line(cx, cy, *polar(cx, cy, L, a), cls, W_MARK,
                        **{"stroke-linecap": "round"}))
    out.append(dot(cx, cy, 2.8, cls))
    return "".join(out)


# ---------------------------------------------------------------------------
# 7. FAMILY D — INSTRUMENT DETAILS
# ---------------------------------------------------------------------------


def pivot(cx=CX, cy=CY, r=16.0, cls="ink") -> str:
    """Where two plates turn against each other: collar, hole, seating ticks."""
    out = [circle(cx, cy, r, cls, W_RING),
           circle(cx, cy, r * KAPPA, "body", W_HAIR),
           dot(cx, cy, 2.2, cls)]
    for k in range(4):
        a = THETA + 90 * k
        out.append(line(*polar(cx, cy, r + 3, a), *polar(cx, cy, r + 9, a),
                        "body", W_HAIR))
    return "".join(out)


def aperture(cx=CX, cy=CY, r=R * 0.7, a0=None, a1=None, width=14.0,
             cls="body") -> str:
    """A slot cut through a plate: two arcs closed with round ends."""
    a0 = THETA - 40 if a0 is None else a0
    a1 = THETA + 40 if a1 is None else a1
    ro, ri = r + width / 2, r - width / 2
    p0, p1 = polar(cx, cy, ro, a0), polar(cx, cy, ro, a1)
    q1, q0 = polar(cx, cy, ri, a1), polar(cx, cy, ri, a0)
    large = 1 if (a1 - a0) % 360 > 180 else 0
    d = (f"M{f(p0[0])} {f(p0[1])}A{f(ro)} {f(ro)} 0 {large} 1 {f(p1[0])} {f(p1[1])}"
         f"A{f(width/2)} {f(width/2)} 0 0 1 {f(q1[0])} {f(q1[1])}"
         f"A{f(ri)} {f(ri)} 0 {large} 0 {f(q0[0])} {f(q0[1])}"
         f"A{f(width/2)} {f(width/2)} 0 0 1 {f(p0[0])} {f(p0[1])}Z")
    return path(d, cls, W_HAIR)


def tab(cx=CX, cy=CY, r=R, angle=None, size=15.0, cls="body") -> str:
    """A hinge tab seated on a ring: half-round lug plus rivet."""
    angle = THETA + 118 if angle is None else angle
    bx, by = polar(cx, cy, r, angle)
    return (circle(bx, by, size / 2, cls, W_HAIR)
            + dot(bx, by, 2.0, cls)
            + line(*polar(cx, cy, r - size / 2, angle),
                   *polar(cx, cy, r + size / 2, angle), cls, W_HAIR))


def bowl(cx=None, cy=None, r=R_BOWL, cls="ink") -> str:
    """The inner form with its own diameter rule and tangent stem, as in 5a."""
    if cx is None:
        cx, cy = polar(CX, CY, R - r, THETA + 180)
    return "".join([
        circle(cx, cy, r, cls, W_RING),
        line(cx - r, cy, cx + r, cy, cls, W_RING, **{"stroke-linecap": "round"}),
        line(cx + r, cy - r - 64.77, cx + r, cy + r, "active", W_STEM,
             **{"stroke-linecap": "round"}),
    ])


# ---------------------------------------------------------------------------
# 8. FAMILY E — CONSTRUCTION GEOMETRY
# ---------------------------------------------------------------------------


def construction_circle(cx=CX, cy=CY, r=R, cls="faint") -> str:
    return circle(cx, cy, r, cls, W_HAIR, **{"stroke-dasharray": "5 5"})


def centre_lines(cx=CX, cy=CY, r=R + 16, cls="faint") -> str:
    return (line(cx - r, cy, cx + r, cy, cls, W_HAIR, **{"stroke-dasharray": "10 4 2 4"})
            + line(cx, cy - r, cx, cy + r, cls, W_HAIR, **{"stroke-dasharray": "10 4 2 4"}))


def projection(x0, y0, x1, y1, cls="faint") -> str:
    return line(x0, y0, x1, y1, cls, W_HAIR, **{"stroke-dasharray": "3 4"})


def node(x, y, r=3.4, cls="ink") -> str:
    """An intersection point: open, so it never reads as data."""
    return circle(x, y, r, cls, W_HAIR, fill="var(--ground)")


def leader(x, y, dx, dy, label, cls="body", anchor=None) -> str:
    """Annotation leader: elbow, not a curve. Label sits on the horizontal."""
    mx, my = x + dx, y + dy
    ex = mx + (16 if dx >= 0 else -16)
    anchor = anchor or ("start" if dx >= 0 else "end")
    return "".join([
        dot(x, y, 2.0, cls),
        path(f"M{f(x)} {f(y)}L{f(mx)} {f(my)}L{f(ex)} {f(my)}", cls, W_HAIR),
        text(ex + (4 if dx >= 0 else -4), my + 3, label, cls, 8, anchor=anchor),
    ])


# ---------------------------------------------------------------------------
# 9. FAMILY F — DATA
# ---------------------------------------------------------------------------


def data_series(points, x0=36.0, y0=170.0, w=140.0, h=120.0,
                outliers=(), cls="ink") -> str:
    """Plot normalised points. Outliers — and only outliers — take the mark.

    `outliers` is an explicit index list. There is no automatic rule here on
    purpose: coral must always be a judgement someone made about the data.
    """
    out = []
    for i, (px, py) in enumerate(points):
        x, y = x0 + px * w, y0 - py * h
        if i in outliers:
            out.append(circle(x, y, 7.0, "mark", W_HAIR))
            out.append(dot(x, y, 3.2, "mark"))
        else:
            out.append(dot(x, y, 3.0, cls))
    return "".join(out)


def trajectory(points, x0=36.0, y0=170.0, w=140.0, h=120.0, cls="active") -> str:
    pts = [(x0 + px * w, y0 - py * h) for px, py in points]
    d = "M" + "L".join(f"{f(x)} {f(y)}" for x, y in pts)
    return path(d, cls, W_MARK, **{"stroke-linejoin": "round",
                                   "stroke-linecap": "round"})


def cell_field(x0=30.0, y0=30.0, size=140.0, n=9, gap_ratio=0.24,
               density=None, cls="active") -> str:
    """Flat cells: the texture reserved for measurable phenomena.

    `density(i, j) -> 0..1` drives opacity, so the pattern is always a
    rendering of something real rather than a decorative tile.
    """
    cell = size / n
    s = cell * (1 - gap_ratio)
    density = density or (lambda i, j: 0.5)
    out = []
    for j in range(n):
        for i in range(n):
            v = max(0.0, min(1.0, density(i, j)))
            if v <= 0.02:
                continue
            out.append(
                f'<rect x="{f(x0 + i * cell)}" y="{f(y0 + j * cell)}" '
                f'width="{f(s)}" height="{f(s)}" class="{cls} fill" '
                f'fill="currentColor" fill-opacity="{v:.2f}"/>')
    return "".join(out)


def stepped_field(values, x0=34.0, y0=168.0, w=132.0, h=116.0, cls="body") -> str:
    """A distribution as a stepped rule — a histogram stripped to its edge."""
    n = len(values)
    bw = w / n
    d = [f"M{f(x0)} {f(y0)}"]
    for i, v in enumerate(values):
        y = y0 - v * h
        d.append(f"L{f(x0 + i * bw)} {f(y)}L{f(x0 + (i + 1) * bw)} {f(y)}")
    d.append(f"L{f(x0 + w)} {f(y0)}")
    return path("".join(d), cls, W_MARK, **{"stroke-linejoin": "miter"})


def axes(x0=36.0, y0=170.0, w=140.0, h=130.0, nx=7, ny=5, cls="body") -> str:
    """Chart furniture in its smallest honest form: two rules and their ticks."""
    out = [line(x0, y0, x0 + w, y0, cls, W_HAIR),
           line(x0, y0, x0, y0 - h, cls, W_HAIR)]
    for i in range(nx):
        x = x0 + w * i / (nx - 1)
        out.append(line(x, y0, x, y0 + (6 if i % 2 == 0 else 3), cls, W_HAIR))
    for i in range(ny):
        y = y0 - h * i / (ny - 1)
        out.append(line(x0, y, x0 - (6 if i % 2 == 0 else 3), y, cls, W_HAIR))
    return "".join(out)


# ---------------------------------------------------------------------------
# 10. FAMILY G — TALLIES
# ---------------------------------------------------------------------------


def tally(n, x0=34.0, y0=90.0, height=26.0, pitch=7.0, group_gap=13.0,
          cls="ink", w=W_MARK) -> str:
    """Counting by fives: four uprights struck through by the fifth.

    Use for section index, carousel position, iteration and step counters.
    """
    out, x = [], x0
    full, rem = divmod(n, 5)
    for _ in range(full):
        for k in range(4):
            out.append(line(x + k * pitch, y0, x + k * pitch, y0 + height, cls, w))
        out.append(line(x - 2.5, y0 + height + 3, x + 3 * pitch + 2.5, y0 - 3, cls, w))
        x += 4 * pitch + group_gap
    for k in range(rem):
        out.append(line(x + k * pitch, y0, x + k * pitch, y0 + height, cls, w))
    return "".join(out)


def tally_progress(done, total, x0=30.0, y0=92.0, height=22.0, pitch=7.0,
                   group_gap=12.0) -> str:
    """The same counter, with completed steps in the active ink."""
    out, x = [], x0
    for i in range(total):
        cls = "active" if i < done else "faint"
        out.append(line(x, y0, x, y0 + height, cls, W_MARK))
        x += pitch
        if (i + 1) % 5 == 0:
            x += group_gap
    return "".join(out)


# ---------------------------------------------------------------------------
# 11. FAMILY H — THE ORBIT MOTIF
# ---------------------------------------------------------------------------


def orbit(cx=CX, cy=CY, r=R * 0.72, markers=(0, 96, 210), gap=GAP,
          axis=THETA, active=0) -> str:
    """Broken ring plus positional markers — the signature secondary motif.

    It echoes the logo's ring/dot relationship without reproducing the mark.
    """
    out = [broken_ring(cx, cy, r, gap, axis, "body", W_MARK)]
    for i, a in enumerate(markers):
        cls = "active" if i == active else "body"
        out.append(dot(*polar(cx, cy, r, axis + a), 5.0 if i == active else 3.4, cls))
    return "".join(out)


def orbit_frame(cx=CX, cy=CY, r=R * 0.8, axis=THETA) -> str:
    """Avatar / thumbnail frame: broken ring, one seated marker, one sight tick."""
    return "".join([
        broken_ring(cx, cy, r, GAP, axis, "body", W_MARK),
        dot(*polar(cx, cy, r, axis + 180), DOT_R * 0.8, "ink"),
        line(*polar(cx, cy, r + 4, axis), *polar(cx, cy, r + 13, axis),
             "active", W_MARK),
    ])


def calibration_loader(cx=CX, cy=CY, r=R * 0.66, progress=0.42, axis=THETA) -> str:
    """A loading state as an alignment, not a spinner.

    The ring progressively closes toward the sight axis as work completes.
    """
    span = (360 - GAP) * max(0.0, min(1.0, progress))
    out = [broken_ring(cx, cy, r, GAP, axis, "faint", W_MARK)]
    if span > 0.5:
        out.append(ring_arc(cx, cy, r, axis + GAP / 2, axis + GAP / 2 + span,
                            "active", W_MARK))
    out.append(radial_scale(cx, cy, r + 9, axis + 30, axis + 120, 6, 4, False,
                            "faint", W_HAIR))
    out.append(dot(*polar(cx, cy, r, axis + GAP / 2 + span), 4.2, "active"))
    return "".join(out)


# ---------------------------------------------------------------------------
# 12. THE MARK ITSELF — reference reconstruction
# ---------------------------------------------------------------------------


def mark_5a(construction=False) -> str:
    """Rebuild 5a from the constants. Proof that the canon is correct."""
    bx, by = polar(CX, CY, R - R_BOWL, THETA + 180)
    sx, sy = polar(CX, CY, R, THETA)
    dx_, dy_ = polar(CX, CY, R, THETA + 180)
    out = []
    if construction:
        out += [construction_circle(CX, CY, R),
                centre_lines(),
                projection(sx, sy, dx_, dy_),
                construction_circle(bx, by, R_BOWL),
                node(CX, CY), node(bx, by), node(dx_, dy_),
                dimension(CX, CY, bx, by, "R−r"),
                leader(sx, sy, -28, -38, "θ = −40.6°", anchor="end"),
                leader(dx_, dy_, 18, 44, "tangency"),
                radial_scale(CX, CY, R, THETA - 62, THETA + 62, 4, 5, True,
                             "faint", W_HAIR)]
    out += [
        broken_ring(CX, CY, R, GAP, THETA, "ink", W_RING),
        circle(bx, by, R_BOWL, "ink", W_RING),
        line(bx - R_BOWL, by, bx + R_BOWL, by, "ink", W_RING,
             **{"stroke-linecap": "round"}),
        line(bx + R_BOWL, by - R_BOWL - 64.77, bx + R_BOWL, by + R_BOWL,
             "active", W_STEM, **{"stroke-linecap": "round"}),
        star(sx, sy),
        dot(dx_, dy_, DOT_R, "ink"),
    ]
    return "".join(out)


# ---------------------------------------------------------------------------
# 13. WRAPPING AND OUTPUT
# ---------------------------------------------------------------------------

_STYLE = """
svg.dsc{--ink:#092052;--body:#64748B;--faint:#CBD5E1;--active:#0F58E5;
--mark:#E5484D;--ground:#F6F8FC}
@media (prefers-color-scheme:dark){svg.dsc{--ink:#F6F8FC;--body:#94A3B8;
--faint:#1E3A6B;--active:#4F86F7;--mark:#F0696D;--ground:#092052}}
svg.dsc .ink{stroke:var(--ink);color:var(--ink)}
svg.dsc .body{stroke:var(--body);color:var(--body)}
svg.dsc .faint{stroke:var(--faint);color:var(--faint)}
svg.dsc .active{stroke:var(--active);color:var(--active)}
svg.dsc .mark{stroke:var(--mark);color:var(--mark)}
svg.dsc .fill{stroke:none}
"""


def svg_doc(body: str, size=200, bleed=BLEED, standalone=True) -> str:
    vb = f"{-bleed} {-bleed} {size + 2 * bleed} {size + 2 * bleed}"
    style = f"<style>{_STYLE}</style>" if standalone else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" '
            f'class="dsc" width="{size * 2}" height="{size * 2}" '
            f'fill="none">{style}{body}</svg>')


# ---------------------------------------------------------------------------
# 14. THE PLATES — one demonstration per primitive
# ---------------------------------------------------------------------------


def _rng(seed):
    r = random.Random(seed)
    return r


def plates() -> list[dict]:
    r = _rng(4006)
    scatter = [(r.random(), 0.18 + 0.64 * r.random()) for _ in range(26)]
    scatter[11] = (0.62, 0.96)
    traj = [(i / 8, 0.22 + 0.6 * (i / 8) ** 1.6 + 0.06 * math.sin(i)) for i in range(9)]
    hist = [0.12, 0.3, 0.52, 0.78, 0.94, 0.71, 0.44, 0.26, 0.14, 0.07]

    P = [
        # ---- A. ARCS
        ("a01-quarter", "A", "Quarter arc",
         "90° of the ring. The smallest fragment that still reads as an instrument.",
         ring_arc(a0=THETA - 45, a1=THETA + 45)),
        ("a02-half", "A", "Half arc",
         "180°, cut on the sight axis so the opening is never arbitrary.",
         ring_arc(a0=THETA + 90, a1=THETA - 90)),
        ("a03-broken-ring", "A", "Broken ring",
         "The canonical form: 332° closed, 28° open, aperture centred on θ.",
         broken_ring()),
        ("a04-nested", "A", "Nested rings",
         "Radii stepping by κ = 0.4884. Gaps widen inward so they never align.",
         nested_rings(n=3)),
        ("a05-tangent-pair", "A", "Tangent pair",
         "Inner circle internally tangent at −θ. The logo's core relation.",
         tangent_pair(show_proof=True)),
        ("a06-interrupted", "A", "Interrupted ring",
         "Unequal segments, 3:2:2 — deliberately not a dial.",
         interrupted_ring(n=3, gap=12)),
        ("a07-offset-arcs", "A", "Offset arcs",
         "Sweep narrows as radius falls; the innermost arc takes the active ink.",
         offset_arcs()),

        # ---- B. MEASUREMENT
        ("b01-tick-row", "B", "Tick row",
         "Linear graduation. Majors every fifth, 2.2× the minor length.",
         tick_row(50, 120, 100, 21, 5)),
        ("b02-measuring-edge", "B", "Measuring edge",
         "The design spine. A vertical ticked rule content aligns to.",
         measuring_edge(labels=["01", "02", "03", "04", "05"])),
        ("b03-radial-scale", "B", "Radial scale",
         "Graduation over a sector only. A full sweep is refused in code.",
         broken_ring(cls="body", w=W_HAIR) + radial_scale()),
        ("b04-index-mark", "B", "Index mark",
         "One graduation singled out — a longer rule and a seated dot.",
         broken_ring(cls="faint", w=W_HAIR) + radial_scale(step=4, cls="faint")
         + index_mark()),
        ("b05-dimension", "B", "Dimension",
         "A measured distance with end serifs and its value in mono.",
         construction_circle() + dimension(CX, CY, *polar(CX, CY, R, THETA), "R = 86")
         + dimension(CX, CY, *polar(CX, CY, R - R_BOWL, THETA + 180), "R−r = 44")),
        ("b06-scale-labels", "B", "Numeric scale",
         "Ticks carrying units. Metadata is always mono, always small.",
         tick_row(40, 128, 120, 13, 3) + "".join(
             text(40 + 120 * i / 4, 146, ["0", "25", "50", "75", "100"][i],
                  "body", 9, anchor="middle") for i in range(5))
         + text(40, 64, "n = 1 284", "body", 9)),

        # ---- C. ORIENTATION
        ("c01-crosshair", "C", "Crosshair",
         "Four rules stopping short of the point. The target stays readable.",
         crosshair()),
        ("c02-sight-line", "C", "Sight line",
         "A radial rule continuing past the ring — the star's long arm, generalised.",
         broken_ring(cls="body", w=W_HAIR) + sight_line(r_in=18)),
        ("c03-radial-fan", "C", "Radial fan",
         "Sighting lines across the observed sector.",
         broken_ring(cls="faint", w=W_HAIR) + radial_fan()),
        ("c04-pointer", "C", "Pointer",
         "Open V head, never a filled arrow. Direction without weight.",
         broken_ring(cls="body", w=W_MARK) + pointer(r=R - 6, length=54)),
        ("c05-star", "C", "Sight star",
         "Eight arms at 45°, phased so one lies on θ. Never a four-point sparkle.",
         star(CX, CY, sight=52)),
        ("c06-axis-cross", "C", "Coordinate cross",
         "Horizontal and vertical rules forming the page's coordinate system.",
         centre_lines(r=96) + node(CX, CY) + text(CX + 8, CY - 8, "0,0", "faint", 8)),

        # ---- D. INSTRUMENT DETAILS
        ("d01-pivot", "D", "Pivot",
         "Collar, hole and seating ticks — where two plates turn on each other.",
         pivot(r=30)),
        ("d02-aperture", "D", "Aperture",
         "A slot cut through a plate, closed with round ends.",
         broken_ring(cls="faint", w=W_HAIR) + aperture(width=18, a0=THETA - 58,
                                                      a1=THETA + 58)),
        ("d03-tab", "D", "Hinge tab",
         "A lug seated on the ring, with its rivet.",
         broken_ring(cls="body", w=W_MARK) + tab() + tab(angle=THETA + 168)),
        ("d04-bowl", "D", "Bowl and stem",
         "Inner circle, its diameter rule, and the vertical tangent at the right edge.",
         bowl(100, 108, 46)),
        ("d05-pivot-stack", "D", "Pivot stack",
         "Two pivots on one axis at the tangent ratio — a plate assembly.",
         pivot(CX, CY, 26) + pivot(*polar(CX, CY, 52, THETA), 26 * KAPPA)
         + projection(CX, CY, *polar(CX, CY, 52, THETA))),
        ("d06-limb", "D", "Graduated limb",
         "The instrument's outer edge: ring, sector graduation and one index.",
         broken_ring() + radial_scale(r=R - 4, a0=THETA + 40, a1=THETA + 150,
                                      step=3.5) + index_mark(angle=THETA + 95)),

        # ---- E. CONSTRUCTION GEOMETRY
        ("e01-construction", "E", "Construction circle",
         "Dashed: the geometry that generated the form, left visible.",
         construction_circle() + construction_circle(
             *polar(CX, CY, R - R_BOWL, THETA + 180), R_BOWL)),
        ("e02-centre-lines", "E", "Centre lines",
         "Dash-dot rules declaring the origin.",
         centre_lines() + construction_circle(r=R * 0.5)),
        ("e03-projection", "E", "Projection",
         "A dashed line carrying a point from one view to another.",
         circle(CX, CY, 40, "ink", W_RING)
         + projection(CX - 40, CY, CX - 40, CY + 62)
         + projection(CX + 40, CY, CX + 40, CY + 62)
         + dimension(CX - 40, CY + 56, CX + 40, CY + 56, "2r")),
        ("e04-node", "E", "Intersection node",
         "Open circles, so a construction point never reads as data.",
         centre_lines(r=70) + construction_circle(r=58)
         + "".join(node(*polar(CX, CY, 58, 90 * k)) for k in range(4))),
        ("e05-leader", "E", "Leader and label",
         "Elbowed, never curved. The label sits on the horizontal run.",
         broken_ring(cls="body", w=W_MARK)
         + leader(*polar(CX, CY, R, THETA + 150), -16, 18, "limb", anchor="end")
         + leader(*polar(CX, CY, R, THETA + 180), 28, -22, "tangency")),
        ("e06-proof", "E", "Tangency proof",
         "The whole derivation on one plate: θ, R, κ and the aperture.",
         mark_5a(construction=True)),

        # ---- F. DATA
        ("f01-axes", "F", "Axes",
         "Two rules and their ticks. Everything else on a chart is optional.",
         axes()),
        ("f02-scatter", "F", "Distribution",
         "26 points. One is circled — the only thing coral is ever for.",
         axes() + data_series(scatter, outliers={11})
         + text(48, 44, "n = 26", "body", 9)),
        ("f03-trajectory", "F", "Trajectory",
         "A path through the field, in the active ink.",
         axes() + trajectory(traj) + data_series(traj, cls="body")),
        ("f04-stepped", "F", "Stepped field",
         "A histogram reduced to its edge.",
         axes(ny=4) + stepped_field(hist)),
        ("f05-cells", "F", "Cell field",
         "90-cell grid, 24% gap. Density driven by data, never decorative.",
         cell_field(n=9, density=lambda i, j: 0.15 + 0.85 * math.exp(
             -((i - 5.5) ** 2 + (j - 3.2) ** 2) / 12))),
        ("f06-cluster", "F", "Cluster and outlier",
         "The same field, read: a body of points and the one that isn't in it.",
         construction_circle(CX - 14, CY + 8, 44)
         + data_series([(0.30 + 0.22 * r.random(), 0.36 + 0.26 * r.random())
                        for _ in range(22)] + [(0.86, 0.84)],
                       outliers={22})
         + leader(36 + 0.86 * 140, 170 - 0.84 * 120, -20, -26, "outlier", "mark",
                  anchor="end")),

        # ---- G. TALLIES
        ("g01-tally", "G", "Tally",
         "Counting by fives. Section index, carousel position, step counter.",
         tally(12, 40, 84)),
        ("g02-tally-progress", "G", "Tally progress",
         "The same counter with completed steps in the active ink.",
         tally_progress(7, 12, 36, 88)
         + text(36, 142, "07 / 12", "body", 9)),
        ("g03-tally-index", "G", "Tally index",
         "A section number that has to be read as a quantity, not a label.",
         tally(3, 44, 60, 30, 9, 16)
         + line(40, 116, 160, 116, "faint", W_HAIR)
         + text(40, 138, "SECTION", "body", 9)),

        # ---- H. ORBIT
        ("h01-orbit", "H", "Orbit",
         "Broken ring plus positional markers. The signature secondary motif.",
         orbit()),
        ("h02-orbit-frame", "H", "Orbit frame",
         "Avatar and thumbnail frame. Echoes the mark without reproducing it.",
         orbit_frame()),
        ("h03-loader-30", "H", "Calibration · 30%",
         "Loading as alignment. The ring closes toward the sight axis.",
         calibration_loader(progress=0.3)),
        ("h04-loader-80", "H", "Calibration · 80%",
         "Same state, later. No spinner, no indeterminate motion.",
         calibration_loader(progress=0.8)),
        ("h05-orbit-pattern", "H", "Orbit field",
         "Tiled orbits at three scales — a pattern built from primitives.",
         "".join(orbit(40 + 60 * i, 40 + 60 * j, 22 * (0.7 + 0.3 * ((i + j) % 2)),
                       (0, 110, 235), GAP, THETA + 40 * (i - j),
                       active=(i + j) % 3)
                 for i in range(3) for j in range(3))),

        # ---- MARK
        ("z01-mark", "Z", "The 5a mark",
         "Reconstructed from the constants alone — the canon verifies itself.",
         mark_5a()),
    ]
    return [{"id": i, "family": fam, "title": t, "note": n, "body": b}
            for i, fam, t, n, b in P]


FAMILIES = {
    "A": ("Arcs", "Partial circles, broken rings and the tangency that holds them together."),
    "B": ("Measurement", "Ticks, scales and the measuring edge. How the system states a quantity."),
    "C": ("Orientation", "Crosshairs, sight lines and pointers. How the system states a direction."),
    "D": ("Instrument details", "Pivots, apertures, tabs. The parts that make it read as a made object."),
    "E": ("Construction", "The generating geometry, left visible rather than cleaned away."),
    "F": ("Data", "Axes, points, trajectories and fields — where the identity meets real numbers."),
    "G": ("Tallies", "Counting as a functional device: index, position, progress."),
    "H": ("Orbit", "The secondary motif. Broken ring plus markers, at every scale."),
    "Z": ("The mark", "Rebuilt from the constants."),
}


def main(outdir="svg"):
    os.makedirs(outdir, exist_ok=True)
    pl = plates()
    for p in pl:
        with open(os.path.join(outdir, p["id"] + ".svg"), "w", encoding="utf-8") as fh:
            fh.write(svg_doc(p["body"]))
    manifest = {
        "canon": {"R": R, "theta": THETA, "gap": GAP, "kappa": round(KAPPA, 5),
                  "r_bowl": R_BOWL, "centre": [CX, CY], "unit": U,
                  "strokes": {"ring": W_RING, "stem": W_STEM, "mark": W_MARK,
                              "hair": W_HAIR}},
        "palette": PALETTE,
        "families": {k: {"name": v[0], "note": v[1]} for k, v in FAMILIES.items()},
        "plates": pl,
    }
    with open("manifest.json", "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=1)
    print(f"{len(pl)} plates written to {outdir}/")


if __name__ == "__main__":
    main()
