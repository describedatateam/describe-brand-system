"""
textures.py — the .describe( texture set: five fields that are not clean lines.

    python3 geometry/textures.py     writes geometry/textures/ (SVGs, textures.css, textures.html)

    import sys; sys.path.insert(0, "geometry")
    import textures as TX
    TX.signal([3, 5, 9, 14, 8, 4, 6, 11, 7, 3], 1200, 360, label="Weekly orders")

Five textures, each one a measurement drawn as a field:

    signal     one-bit dither: solid where the data is dense, dissolving where
               it thins. One column per period. (Signal and noise.)
    halftone   dots sized by a measure, bent toward the largest value.
    rings      two ring sets, one per dataset; where they overlap is the finding.
    waves      one line per series, stepped greys, one line in the active blue.
    crescent   a bitmap crescent in cells: the Eid and occasion motif.

Every function returns an inline <svg class="tx"> string. Colours are never
typed here. The elements carry semantic classes (ink, body, dim, faint, active,
s1..s5) and textures.css maps them to the tokens, so one drawing renders on
paper, on navy and on the cobalt ground. Standalone files (`standalone()`)
embed the light tokens instead, for tools that cannot read CSS variables.

Rules, enforced by templates/check.py:

  * a texture is bound to a measurement. signal() refuses empty or flat values;
    halftone() needs `measure`; rings() needs both dataset names; waves() and
    crescent() need a `label`. The label becomes the SVG's accessible name.
  * ONE marked thing: a single star, a single active line, a single active
    ring, a single focus disc. Never more.
  * ink, body, dim and faint paint the field. Coral never appears (a tone of
    `mark` raises). No gradient, no glow, no opacity ramps: tone steps are
    discrete (s1..s5) and the dissolve is a one-bit Bayer dither.
  * textures go on covers, dividers, hero bands and social backgrounds, never
    behind a chart, a table or body text.
"""

from __future__ import annotations

import json
import math
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import astrolabe as A  # noqa: E402

TOKENS = json.load(open(os.path.join(ROOT, "tokens", "dist", "tokens.json"), encoding="utf-8"))["tokens"]
THETA = A.THETA
FIELD_TONES = ("ink", "body", "dim", "faint")
STEPS = (16, 30, 46, 62, 80)          # s1..s5: % of body over the ground

_uid = [0]


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _n(v: float) -> str:
    return f"{v:.1f}".rstrip("0").rstrip(".")


def _bayer(n: int = 8) -> list[list[float]]:
    m = [[0, 2], [3, 1]]
    while len(m) < n:
        k = len(m)
        m = ([[4 * v for v in row] + [4 * v + 2 for v in row] for row in m]
             + [[4 * v + 3 for v in row] + [4 * v + 1 for v in row] for row in m])
    t = len(m) ** 2
    return [[v / t for v in row] for row in m]


B8 = _bayer(8)


def _sstep(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def _tone(t: str) -> str:
    if t == "mark":
        raise ValueError("Coral is for genuine outliers only; a texture never wears it.")
    if t not in FIELD_TONES:
        raise ValueError(f"tone must be one of {FIELD_TONES}, not {t!r}")
    return t


def _need(text: str, what: str) -> str:
    if not (text or "").strip():
        raise ValueError(f"{what}: a texture is bound to a measurement; say what it measures.")
    return text.strip()


def _squares(pts: list[tuple[float, float]], s: float) -> str:
    return "".join(f"M{_n(x)} {_n(y)}h{_n(s)}v{_n(s)}h-{_n(s)}z" for x, y in pts)


def _star(x: float, y: float, k: float) -> str:
    """The star, scaled about its centre. The only marked thing in most textures."""
    return (f'<g data-star transform="translate({_n(x)} {_n(y)}) scale({_n(k)})">'
            f'{A.star(0, 0, cls="active")}</g>')


def _svg(w: float, h: float, body: str, kind: str, label: str, extra_cls: str = "", style: str = "",
         par: str = "xMidYMid slice") -> str:
    return (f'<svg class="tx tx--{kind}{(" " + extra_cls) if extra_cls else ""}" viewBox="0 0 {_n(w)} {_n(h)}" '
            f'width="{_n(w)}" height="{_n(h)}" fill="none" overflow="hidden" preserveAspectRatio="{par}" '
            f'role="img" aria-label="{label}"{(" style=" + chr(34) + style + chr(34)) if style else ""}>{body}</svg>')


# ---------------------------------------------------------------------------
# 1 · signal — one-bit dither dissolve
# ---------------------------------------------------------------------------
def signal(values: list[float], w: float = 1080, h: float = 560, *, label: str, tone: str = "body",
           dissolve: int | None = None, star: bool = True, reveal: bool = False, extra_cls: str = "") -> str:
    """One column per value. Columns are solid cells up to the value; above
    them the cells thin out by an 8x8 Bayer dither (the noise). The tallest
    column's top cell is active and the star sits above it: the one finding."""
    tone = _tone(tone)
    label = _need(label, "signal()")
    vals = [float(v) for v in values]
    if len(vals) < 8 or min(vals) < 0 or max(vals) <= 0 or max(vals) == min(vals):
        raise ValueError("signal() needs at least 8 real, non-negative, non-flat values; there is no default pattern.")
    cols = len(vals)
    pitch = w / cols
    cell = round(pitch * 0.8, 1)
    rows = int(h // pitch)
    room = 4                                   # rows kept clear above the peak for the star
    dissolve = dissolve or max(6, round(rows * 0.32))
    top_rows = rows - dissolve - room
    if top_rows < 3:
        raise ValueError("signal(): too short for this many columns; give it more height or fewer columns.")
    vmax = max(vals)
    hts = [max(1, round(v / vmax * top_rows)) for v in vals]
    peak = hts.index(max(hts))
    sx = peak * pitch + cell / 2
    sy = h - hts[peak] * pitch + cell / 2 - 2.6 * pitch
    out = []
    for c in range(cols):
        solid, mid, low = [], [], []
        x = c * pitch
        for r in range(hts[c] + dissolve):
            y = h - (r + 1) * pitch
            if y < 0:
                break
            if r < hts[c]:
                if not (c == peak and r == hts[c] - 1):
                    solid.append((x, y))
                continue
            t = (r - hts[c]) / dissolve
            if star and math.hypot(x + cell / 2 - sx, y + cell / 2 - sy) < 2.2 * pitch:
                continue
            if B8[r % 8][c % 8] < (1 - t) ** 1.15:
                (mid if t < 0.5 else low).append((x, y))
        g = []
        if solid:
            g.append(f'<path class="{tone} fill" d="{_squares(solid, cell)}"/>')
        if c == peak:
            g.append(f'<path class="active fill" d="{_squares([(x, h - hts[c] * pitch)], cell)}"/>')
        if mid:
            g.append(f'<path class="dim fill" d="{_squares(mid, cell)}"/>')
        if low:
            g.append(f'<path class="faint fill" d="{_squares(low, cell)}"/>')
        out.append(f'<g class="tx-col" style="--i:{c}">{"".join(g)}</g>')
    if star:
        out.append(_star(sx, sy, pitch * 0.12))
    return _svg(w, h, "".join(out), "signal", label, ("tx--reveal " if reveal else "") + extra_cls)


# ---------------------------------------------------------------------------
# 2 · halftone — dots sized by a measure, bent toward the largest value
# ---------------------------------------------------------------------------
def halftone(w: float = 1080, h: float = 820, *, measure: str, focus: tuple[float, float] | None = None,
             pitch: float = 26, angle: float = 18, rmax: float = 12, hole: float = 98, reach: float | None = None,
             fade: tuple[float, float] = (70, 150), tone: str = "ink", extra_cls: str = "") -> str:
    """Dot radius falls off with distance from the focus (the largest value);
    the grid is pushed outward around it so the dots bend toward the focus and
    leave a clean round hole for the one active disc. The edges taper
    (`fade` = top, bottom) so the field never touches the type above or below."""
    tone = _tone(tone)
    measure = _need(measure, "halftone(measure=)")
    fx, fy = focus or (w * 0.64, h * 0.5)
    reach = reach or 0.72 * max(w, h)
    s = hole / 98.0
    ca, sa = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    span = int(max(w, h) / pitch) + 4
    dots = []
    for u in range(-span, span):
        for v in range(-span, span):
            x = fx + (u * ca - v * sa) * pitch
            y = fy + (u * sa + v * ca) * pitch
            if not (-20 < x < w + 20 and 0 < y < h):
                continue
            d0 = math.hypot(x - fx, y - fy)
            if d0 < 1:
                continue
            dn = d0 + 22 * s * math.exp(-max(d0 - 90 * s, 0) / (70 * s))
            if dn < hole:
                continue
            x = fx + (x - fx) * dn / d0
            y = fy + (y - fy) * dn / d0
            t = max(0.0, 1 - dn / reach)
            r = rmax * t ** 1.2 * _sstep((dn - hole) / (90 * s)) * _sstep((h - y) / fade[1]) * _sstep(y / fade[0])
            if r < 1.0:
                continue
            dots.append((x, y, r))
    d = "".join(f"M{_n(x - r)} {_n(y)}a{_n(r)} {_n(r)} 0 1 0 {_n(2 * r)} 0a{_n(r)} {_n(r)} 0 1 0 {_n(-2 * r)} 0"
                for x, y, r in dots)
    body = (f'<path class="{tone} fill" d="{d}"/>'
            f'<circle data-focus class="active fill" cx="{_n(fx)}" cy="{_n(fy)}" r="{_n(hole * 0.84)}" fill="currentColor"/>')
    return _svg(w, h, body, "halftone", f"Dot size shows {measure}; the active disc is the largest value", extra_cls)


# ---------------------------------------------------------------------------
# 3 · rings — two sets, and where they overlap
# ---------------------------------------------------------------------------
def rings(w: float = 1080, h: float = 780, *, a: str, b: str, n: int = 55, pitch_a: float = 14.0,
          pitch_b: float = 14.7, extra_cls: str = "") -> str:
    """One ring set per dataset (a: ink, b: body). One ring of b is active and
    graduated; the star sits where it crosses a ring of a. Crosshairs mark
    the two centres. The moire between the sets is the overlap."""
    a, b = _need(a, "rings(a=)"), _need(b, "rings(b=)")
    A_, B_ = (w * 0.343, h * 0.55), (w * 0.648, h * 0.55)
    dist = B_[0] - A_[0]
    jb = round((0.71 * dist - 14) / pitch_b)
    ka = round((0.933 * dist - 14) / pitch_a)
    ra, rb = 14 + pitch_a * ka, 14 + pitch_b * jb
    out = [f'<g opacity=".72">']
    for k in range(1, n + 1):
        out.append(f'<circle class="ink" cx="{_n(A_[0])}" cy="{_n(A_[1])}" r="{_n(14 + pitch_a * k)}" stroke-width="1.7"/>')
    for j in range(1, n + 1):
        out.append(f'<circle class="body" cx="{_n(B_[0])}" cy="{_n(B_[1])}" r="{_n(14 + pitch_b * j)}" stroke-width="1.7"/>')
    out.append("</g>")
    out.append(f'<circle data-active-ring class="active" cx="{_n(B_[0])}" cy="{_n(B_[1])}" r="{_n(rb)}" stroke-width="3.6"/>')
    q = (ra * ra - rb * rb + dist * dist) / (2 * dist)
    hh = math.sqrt(max(ra * ra - q * q, 0))
    px, py = A_[0] + q, A_[1] - hh
    phi = math.degrees(math.atan2(py - B_[1], px - B_[0]))
    for i in range(-24, 25):
        ang = phi + i * 2.5
        L = 20 if i % 5 == 0 else 10
        x1, y1 = A.polar(B_[0], B_[1], rb, ang)
        x2, y2 = A.polar(B_[0], B_[1], rb - L - 2, ang)
        out.append(A.line(x1, y1, x2, y2, "active", 2.2))
    for c, cls in ((A_, "ink"), (B_, "body")):
        for ang in (0, 90, 180, 270):
            x1, y1 = A.polar(c[0], c[1], 7, ang)
            x2, y2 = A.polar(c[0], c[1], 26, ang)
            out.append(A.line(x1, y1, x2, y2, cls, 2.4))
    out.append(_star(px, py, 2.4))
    return _svg(w, h, "".join(out), "rings", f"Two ring sets: {a} and {b}. The star marks where they overlap", extra_cls)


# ---------------------------------------------------------------------------
# 4 · waves — one series among many
# ---------------------------------------------------------------------------
def waves(w: float = 1080, h: float = 760, *, label: str, n: int = 64, story: int | None = None,
          margin: float = 77, amp: tuple[float, float] = (4, 34), reveal: bool = False,
          extra_cls: str = "") -> str:
    """One line per series, displaced by a slow wave; the lines step through
    five greys (s1 faintest, s5 strongest). One line is active: the story.
    A measuring edge at the left has one tick per series and a long active
    tick for the story; the star sits at the story's crest."""
    label = _need(label, "waves()")
    if n < 12:
        raise ValueError("waves() needs at least 12 series to read as a field.")
    story = round(0.6 * (n - 1)) if story is None else story
    if not 0 <= story < n:
        raise ValueError("waves(): the story series must be one of the lines.")
    x0, x1 = margin + 33, w - margin + 1
    a0, a1 = amp
    y0 = 8 + a0
    dy = (h - 8 - a1 - y0) / (n - 1)
    xs = []
    x = x0
    while x < x1:
        xs.append(x)
        x += 12
    xs.append(x1)
    out, edge_y, crest = [], [], None
    for i in range(n):
        t = i / (n - 1)
        am = a0 + (a1 - a0) * t ** 1.5
        ys = [y0 + i * dy + am * (0.62 * math.sin(x * 0.0105 + i * 0.062) + 0.38 * math.sin(x * 0.026 - i * 0.047 + 1.3))
              for x in xs]
        edge_y.append(ys[0])
        pts = list(zip(xs, ys))
        d = f"M{_n(pts[0][0])} {_n(pts[0][1])}"
        for k in range(1, len(pts) - 1):
            mx, my = (pts[k][0] + pts[k + 1][0]) / 2, (pts[k][1] + pts[k + 1][1]) / 2
            d += f"Q{_n(pts[k][0])} {_n(pts[k][1])} {_n(mx)} {_n(my)}"
        d += f"L{_n(pts[-1][0])} {_n(pts[-1][1])}"
        if i == story:
            lo, hi = x0 + 0.28 * (x1 - x0), x0 + 0.76 * (x1 - x0)
            k = min((j for j, x in enumerate(xs) if lo < x < hi), key=lambda j: ys[j])
            crest = (xs[k], ys[k])
            continue                         # drawn last, on top
        band = min(int(t * 5), 4)
        out.append(f'<path class="tx-line s{band + 1}" pathLength="1" style="--i:{i}" d="{d}" stroke-width="2.1" stroke-linecap="round"/>')
    # the story line, last
    ys = [y0 + story * dy + (a0 + (a1 - a0) * (story / (n - 1)) ** 1.5)
          * (0.62 * math.sin(x * 0.0105 + story * 0.062) + 0.38 * math.sin(x * 0.026 - story * 0.047 + 1.3)) for x in xs]
    pts = list(zip(xs, ys))
    d = f"M{_n(pts[0][0])} {_n(pts[0][1])}"
    for k in range(1, len(pts) - 1):
        mx, my = (pts[k][0] + pts[k + 1][0]) / 2, (pts[k][1] + pts[k + 1][1]) / 2
        d += f"Q{_n(pts[k][0])} {_n(pts[k][1])} {_n(mx)} {_n(my)}"
    d += f"L{_n(pts[-1][0])} {_n(pts[-1][1])}"
    out.append(f'<path data-story class="tx-line active" pathLength="1" style="--i:{story}" d="{d}" stroke-width="4.2" stroke-linecap="round"/>')
    # measuring edge
    e = [A.line(margin, edge_y[0] - 6, margin, edge_y[-1] + 6, "body", 1.6)]
    for i, y in enumerate(edge_y):
        if i == story:
            e.append(A.line(margin, y, margin + 30, y, "active", 3.6))
        else:
            e.append(A.line(margin, y, margin + (16 if i % 8 == 0 else 7), y, "body", 1.6))
    out.append(f'<g class="tx-edge">{"".join(e)}</g>')
    out.append(_star(crest[0], crest[1] - 0.0, 2.4))
    return _svg(w, h, "".join(out), "waves", label, ("tx--reveal " if reveal else "") + extra_cls)


# ---------------------------------------------------------------------------
# 5 · crescent — a bitmap crescent in cells
# ---------------------------------------------------------------------------
def crescent(w: float = 1080, h: float = 1080, *, label: str, cx: float | None = None, cy: float | None = None,
             R: float | None = None, pitch: float = 16, cell: float = 13, seed: int = 7, extra_cls: str = "") -> str:
    """The ring minus a circle pushed along the sight axis, built from cells
    and dissolving toward its thin tip by a Bayer dither (a few dust cells fall
    away beyond it). The star sits in the opening, facing the sight axis."""
    label = _need(label, "crescent()")
    cx = w / 2 if cx is None else cx
    cy = h / 2 if cy is None else cy
    R = R or 0.305 * min(w, h)
    c, s = math.cos(math.radians(THETA)), math.sin(math.radians(THETA))
    d_, rho = 0.40 * R, 0.86 * R
    rng = random.Random(seed)
    ink, body, dust = [], [], []
    for gy in range(int((cy - R - 30) // pitch), int((cy + R + 30) // pitch) + 1):
        for gx in range(int((cx - R - 30) // pitch), int((cx + R + 30) // pitch) + 1):
            x, y = gx * pitch, gy * pitch
            dx, dy = x + cell / 2 - cx, y + cell / 2 - cy
            u, v = dx * c + dy * s, -dx * s + dy * c
            inside = (u * u + v * v <= R * R) and ((u - d_) ** 2 + v * v > rho * rho)
            sn = (u + R) / (2 * R)
            if inside:
                keep = min(max((sn - 0.02) / 0.34, 0), 1) ** 0.85
                if B8[gy % 8][gx % 8] < keep:
                    (ink if keep > 0.97 else body).append((x, y))
            else:
                dist = math.sqrt(max(0.0, u * u + v * v)) - R
                if sn < 0.5 and 0 < dist < 70 and rng.random() < 0.05 * (1 - dist / 70):
                    dust.append((x, y))
    sx, sy = A.polar(cx, cy, 0.62 * R, THETA)
    body_ = (f'<path class="ink fill" d="{_squares(ink, cell)}"/>'
             f'<path class="body fill" d="{_squares(body + dust, cell)}"/>' + _star(sx, sy, 2.6))
    return _svg(w, h, body_, "crescent", label, extra_cls)


def star_xy(svg: str) -> tuple[float, float]:
    """Where a texture's star sits, in the SVG's own coordinates, so a page can
    hang a leader or a label from it."""
    m = re.search(r'data-star transform="translate\(([\d.\-]+) ([\d.\-]+)\)', svg)
    if not m:
        raise ValueError("this texture has no star")
    return float(m.group(1)), float(m.group(2))


# ---------------------------------------------------------------------------
# CSS: tokens for the web, literal tokens for standalone files
# ---------------------------------------------------------------------------
def _rules(c: dict[str, str]) -> str:
    lines = [
        ".tx{display:block;width:100%;height:auto;overflow:hidden}",
        ".tx--bg{position:absolute;inset:0;width:100%;height:100%}",
    ]
    for k in ("ink", "body", "dim", "faint", "active", "s1", "s2", "s3", "s4", "s5"):
        lines.append(f".tx .{k}{{color:{c[k]};stroke:currentColor}}")
    lines.append(".tx .fill{fill:currentColor;stroke:none}")
    lines.append(".tx line,.tx path:not(.fill){stroke-linecap:round}")
    return "\n".join(lines)


def _mix(body: str, ground: str, pct: int) -> str:
    h = lambda s: tuple(int(s.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    a, g = h(body), h(ground)
    return "#" + "".join(f"{round(a[i] * pct / 100 + g[i] * (1 - pct / 100)):02X}" for i in range(3))


def _literal(theme: str) -> dict[str, str]:
    t = lambda k: TOKENS[k][theme]
    c = {"ink": t("color.text.ink"), "body": t("color.text.body"), "dim": t("color.text.dim"),
         "faint": t("color.line.faint"), "active": t("color.role.active")}
    for i, p in enumerate(STEPS, 1):
        c[f"s{i}"] = _mix(c["body"], t("color.surface.ground"), p)
    return c


def css() -> str:
    """textures.css: the classes read the tokens, never a typed colour."""
    c = {"ink": "var(--ink)", "body": "var(--body)", "dim": "var(--dim)", "faint": "var(--faint)",
         "active": "var(--accent,var(--active))"}
    for i, p in enumerate(STEPS, 1):
        c[f"s{i}"] = f"color-mix(in srgb,var(--body) {p}%,var(--ground))"
    return f"""/* textures.css — the .describe( texture set. GENERATED by geometry/textures.py.
   Reads tokens/dist/tokens.css; never types a colour. Use with inline <svg class="tx">
   from geometry/textures.py (see geometry/TEXTURES.md). */

{_rules(c)}

/* the cobalt ground: brand blue behind paper-white ink, everything else is the
   paper colour stepped back toward the blue; the marker is paper at full strength */
.on-cobalt{{--ground:var(--brand-blue);--ink:var(--brand-off-white);--active:var(--brand-off-white);--accent:var(--brand-off-white);
  --body:color-mix(in srgb,var(--brand-off-white) 88%,var(--brand-blue));
  --dim:color-mix(in srgb,var(--brand-off-white) 88%,var(--brand-blue));
  --faint:color-mix(in srgb,var(--brand-off-white) 34%,var(--brand-blue));
  --rule:color-mix(in srgb,var(--brand-off-white) 44%,var(--brand-blue));
  background:var(--ground);color:var(--ink)}}

/* a field that clears out under the type (stepped mask, not a glow) */
.tx-clear-left{{-webkit-mask:linear-gradient(90deg,transparent 40%,#000 70%);mask:linear-gradient(90deg,transparent 40%,#000 70%)}}
.tx-clear-up{{-webkit-mask:linear-gradient(180deg,transparent 30%,#000 75%);mask:linear-gradient(180deg,transparent 30%,#000 75%)}}

/* optional reveal: orientation, measurement, resolution. One curve, no overshoot.
   Every state has a resting frame under prefers-reduced-motion. */
@media (prefers-reduced-motion:no-preference){{
  .tx--reveal .tx-col{{animation:tx-in var(--t3,420ms) var(--ease,cubic-bezier(.2,.7,.2,1)) both;animation-delay:calc(var(--i) * 14ms)}}
  .tx--reveal .tx-line{{stroke-dasharray:1;animation:tx-draw 900ms var(--ease,cubic-bezier(.2,.7,.2,1)) both;animation-delay:calc(var(--i) * 10ms)}}
  .tx--reveal [data-star]{{animation:tx-in var(--t3,420ms) var(--ease,cubic-bezier(.2,.7,.2,1)) 900ms both}}
}}
@keyframes tx-in{{from{{opacity:0}}to{{opacity:1}}}}
@keyframes tx-draw{{from{{stroke-dashoffset:1}}to{{stroke-dashoffset:0}}}}
"""


def standalone(svg: str, theme: str = "light") -> str:
    """A texture as a self-contained file: the theme's literal token values
    embedded as a <style>, ground included, for tools that cannot read CSS vars."""
    c = _literal(theme)
    ground = TOKENS["color.surface.ground"][theme]
    style = f"<style>{_rules(c)}</style>"
    m = re.match(r'(<svg )(.*?>)', svg, flags=re.S)
    out = m.group(1) + 'xmlns="http://www.w3.org/2000/svg" ' + m.group(2) + style + svg[m.end():]
    w, h = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg).groups()
    return out.replace(style, f'{style}<rect width="{w}" height="{h}" fill="{ground}"/>', 1)


# ---------------------------------------------------------------------------
# sample data (placeholder: replace with real values; the guards need real ones)
# ---------------------------------------------------------------------------
def sample_values(n: int = 46) -> list[float]:
    return [6 + 11 * math.exp(-(((i - 30) / 9) ** 2)) + 5 * math.exp(-(((i - 12) / 6) ** 2)) + 1.6 * math.sin(i * 1.7)
            for i in range(n)]


def build() -> list[str]:
    out = os.path.join(HERE, "textures")
    os.makedirs(out, exist_ok=True)
    set_ = {
        "signal": signal(sample_values(), 1200, 520, label="Sample values, one column per period"),
        "halftone": halftone(1200, 700, measure="a sample measure"),
        "rings": rings(1200, 700, a="set A", b="set B"),
        "waves": waves(1200, 700, label="64 sample series; the blue line is the story"),
        "crescent": crescent(900, 900, label="A crescent built from cells, for Eid and occasions"),
    }
    open(os.path.join(out, "textures.css"), "w", encoding="utf-8").write(css())
    paths = []
    for name, svg in set_.items():
        for theme in ("light", "dark"):
            p = os.path.join(out, f"texture-{name}-{theme}.svg")
            open(p, "w", encoding="utf-8").write(standalone(svg, theme))
            paths.append(p)
    page = _specimen(set_)
    p = os.path.join(out, "textures.html")
    open(p, "w", encoding="utf-8").write(page)
    return paths + [p]


def _specimen(set_: dict[str, str]) -> str:
    hero = signal(sample_values(72), 1440, 360, label="Sample values, one column per period", reveal=True)
    def card(name: str, title: str, use: str, cls: str = "") -> str:
        return (f'<figure class="card {cls}"><div class="plate">{set_[name]}</div>'
                f'<figcaption><b>{title}</b><span>{use}</span></figcaption></figure>')
    cards = lambda cls: "".join([
        card("signal", "Signal", "Divider or hero band. One column per period.", cls),
        card("halftone", "Halftone", "Cover or section background. Dot size is the measure.", cls),
        card("rings", "Rings", "Card header or feature image. One set per dataset.", cls),
        card("waves", "Waves", "Page header. One line per series, one is the story.", cls),
        card("crescent", "Crescent", "Eid and occasion banner. Cells, not curves.", "card--sq"),
    ])
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>.describe( textures</title>
<link rel="stylesheet" href="../../tokens/dist/tokens.css">
<link rel="stylesheet" href="textures.css">
<style>
*{{box-sizing:border-box}}
body{{margin:0;background:var(--ground);color:var(--ink);font-family:var(--font-sans);font-weight:300}}
.band{{padding:clamp(24px,5vw,64px) clamp(16px,4vw,48px)}}
.band h2{{font-family:var(--font-serif);font-weight:300;font-variation-settings:'SOFT' 0,'WONK' 0;font-size:clamp(28px,4vw,40px);margin:0 0 24px;letter-spacing:-.02em}}
.band p.k{{font-family:var(--font-mono);font-weight:500;font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--dim);margin:0 0 12px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,420px),1fr));gap:32px}}
.card{{margin:0}}
.plate{{border:1px solid var(--rule);background:var(--ground);overflow:hidden}}
.grid{{align-items:start}}
.card--sq{{max-width:420px}}
figcaption{{display:flex;flex-direction:column;gap:2px;margin-top:12px;font-size:14px;color:var(--body)}}
figcaption b{{font-weight:500;color:var(--ink)}}
[data-theme=dark]{{background:var(--ground);color:var(--ink)}}
.hero{{padding:clamp(32px,6vw,72px) 0 0;border-bottom:1px solid var(--rule);overflow:hidden}}
.hero h1{{padding:0 clamp(16px,4vw,48px) clamp(24px,4vw,48px);font-family:var(--font-serif);font-weight:300;font-variation-settings:'SOFT' 0,'WONK' 0;font-size:clamp(40px,7vw,88px);line-height:1;letter-spacing:-.028em;margin:0;max-width:18ch}}
.hero h1 em{{font-style:normal;color:var(--accent,var(--active))}}
</style></head>
<body>
<header class="hero"><h1>Signal, <em>then noise.</em></h1>{hero}</header>
<section class="band"><p class="k">Paper</p><h2>Five textures</h2><div class="grid">{cards("")}</div></section>
<section class="band" data-theme="dark"><p class="k">Navy</p><h2>The same drawings, dark</h2><div class="grid">{cards("")}</div></section>
<section class="band on-cobalt"><p class="k">Cobalt</p><h2>On the brand blue</h2><div class="grid">{cards("")}</div></section>
</body></html>"""


if __name__ == "__main__":
    print("\n".join(build()))
