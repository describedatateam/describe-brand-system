"""
chartkit.py — the .describe( chart furniture.

Every chart is assembled from the components in this file; nothing is drawn
ad hoc. The component list is brief §15, in full:

    x-axis · y-axis · tick sets · numeric scale · radial scale (see geometry)
    legend · annotation leader · outlier marker · data dot · confidence
    interval · comparison bracket · measurement label · unit label
    n= / source / timestamp (the provenance line) · null indicator ·
    missing-data indicator · not-applicable start · reference rule ·
    selected-state indicator

COLOUR IS EMPHASIS, NOT CATEGORY. Measured, not assumed: the brief's navy /
blue / grey fails the categorical checks in both modes — navy is too dark to
read as a data colour and the grey too desaturated to carry identity. So the
palette is used for what it actually is:

    story    blue   — the one series the finding is about
    context  grey   — everything else, deliberately recessive
    ink      navy   — axes, text. Never data.
    mark     coral  — an outlier marker, always with the test that flagged it
    pos/neg         — a value that moved the good / bad way (meaning, not sign)

In dark mode the context grey is a NEUTRAL grey: every blue-grey tested
shares the story blue's hue and fails the normal-vision separation floor.

Text never wears a data colour: labels are ink or body, and identity comes
from a swatch beside the text.
"""

from __future__ import annotations

import html
import json
import math
from datetime import datetime

# ---------------------------------------------------------------------------
# Tokens — the chart subset of ui.css, validated (see CHARTS.md §2)
# ---------------------------------------------------------------------------
LIGHT = {"ink": "#092052", "body": "#5A6B85", "dim": "#63738D", "rule": "#D8E1EF",
         "faint": "#CBD5E1", "panel": "#FFFFFF", "story": "#0F58E5",
         "context": "#64748B", "mark": "#E5484D", "pos": "#0F7B3D", "neg": "#8C1D1D"}
DARK = {"ink": "#F6F8FC", "body": "#9FB0CC", "dim": "#7285A6", "rule": "#16346E",
        "faint": "#1C3566", "panel": "#081A40", "story": "#5B8DF0",
        "context": "#676A70", "mark": "#F0696D", "pos": "#3FBE77", "neg": "#E0736F"}

MONO = "'IBM Plex Mono', ui-monospace, monospace"
SANS = "'Readex Pro', 'Vazirmatn', system-ui, sans-serif"

W_DATA = 2.0      # data line
W_HAIR = 1.0      # axes, grid, leaders
R_DOT = 4.0       # marker radius (>= 8px diameter)
RING = 2.0        # surface ring around dots


def f(v: float) -> str:
    return f"{v:.2f}".rstrip("0").rstrip(".")


def esc(s) -> str:
    return html.escape(str(s), quote=True)


# ---------------------------------------------------------------------------
# Scales
# ---------------------------------------------------------------------------
def nice_step(span: float, target: int = 5) -> float:
    raw = span / max(target, 1)
    mag = 10 ** math.floor(math.log10(raw))
    for m in (1, 2, 2.5, 5, 10):
        if raw <= m * mag:
            return m * mag
    return 10 * mag


def nice_cover(lo: float, hi: float, target: int = 5):
    """Ticks that COVER [lo, hi] — the last tick is >= hi, so no mark is
    ever drawn past the top gridline."""
    step = nice_step(hi - lo, target)
    return [round(v * step, 10) for v in range(math.floor(lo / step), math.ceil(hi / step) + 1)]


def nice_ticks(lo: float, hi: float, target: int = 5):
    step = nice_step(hi - lo, target)
    start = math.floor(lo / step) * step
    ticks, v = [], start
    while v <= hi + step * 1e-9:
        ticks.append(round(v, 10))
        v += step
    return ticks


class Linear:
    def __init__(self, d0, d1, r0, r1):
        self.d0, self.d1, self.r0, self.r1 = d0, d1, r0, r1

    def __call__(self, v):
        return self.r0 + (v - self.d0) / (self.d1 - self.d0) * (self.r1 - self.r0)


class Log:
    def __init__(self, d0, d1, r0, r1):
        self.l0, self.l1, self.r0, self.r1 = math.log10(d0), math.log10(d1), r0, r1

    def __call__(self, v):
        return self.r0 + (math.log10(v) - self.l0) / (self.l1 - self.l0) * (self.r1 - self.r0)


def log_ticks(lo, hi):
    """1-2-5 ticks for a log axis."""
    out, e = [], math.floor(math.log10(lo))
    while 10 ** e <= hi * 1.0001:
        for m in (1, 2, 5):
            v = m * 10 ** e
            if lo * 0.9999 <= v <= hi * 1.0001:
                out.append(v)
        e += 1
    return out


class Time(Linear):
    def __init__(self, t0: datetime, t1: datetime, r0, r1):
        super().__init__(t0.timestamp(), t1.timestamp(), r0, r1)

    def __call__(self, t):
        return super().__call__(t.timestamp())


# ---------------------------------------------------------------------------
# Primitive SVG
# ---------------------------------------------------------------------------
def line(x0, y0, x1, y1, cls="c-axis", w=W_HAIR, extra=""):
    return (f'<path class="{cls}" d="M{f(x0)} {f(y0)}L{f(x1)} {f(y1)}" '
            f'stroke-width="{f(w)}" {extra}/>')


def text(x, y, s, cls="c-body", size=12, anchor="start", font="sans", weight=400,
         extra=""):
    fam = MONO if font == "mono" else SANS
    ls = ' letter-spacing="0.08em"' if font == "mono" else ""
    return (f'<text class="{cls}" x="{f(x)}" y="{f(y)}" font-size="{size}" '
            f'font-family="{fam}" font-weight="{weight}" text-anchor="{anchor}"{ls} '
            f'{extra}>{esc(s)}</text>')


# ---------------------------------------------------------------------------
# Furniture
# ---------------------------------------------------------------------------
def x_axis(scale, y, ticks, fmt=str, label_every=1, minor=None):
    """Baseline, measured ticks below it, mono tick labels. Numerals → mono."""
    out = [line(scale.r0, y, scale.r1, y, "c-axis")]
    for i, t in enumerate(ticks):
        x = scale(t)
        out.append(line(x, y, x, y + 6, "c-axis"))
        if i % label_every == 0:
            out.append(text(x, y + 19, fmt(t), "c-body", 10.5, "middle", "mono"))
    for t in (minor or []):
        x = scale(t)
        out.append(line(x, y, x, y + 3, "c-axis"))
    return "".join(out)


def y_axis(scale, x0, x1, ticks, fmt=str, grid=True):
    """Solid hairline gridlines (never dashed — dashed means threshold), and
    mono tick labels. No vertical rule: the gridlines are the measurement."""
    out = []
    for t in ticks:
        y = scale(t)
        if grid:
            out.append(line(x0, y, x1, y, "c-grid"))
        out.append(text(x0 - 8, y + 3.5, fmt(t), "c-body", 10.5, "end", "mono"))
    return "".join(out)


def unit_label(x, y, s, anchor="start"):
    """Units and axis titles: mono, ≤11px, uppercase, ≤4 words (mono budget 02)."""
    return text(x, y, s.upper(), "c-dim", 10, anchor, "mono", 500)


def data_dot(x, y, cls="c-story", r=R_DOT, tip=None, opacity=1.0, focus=True):
    """focus=False for dense scatter: hundreds of tab stops is worse than none;
    the nearest-point layer serves the pointer, the table serves the keyboard."""
    t = (f' data-tip="{esc(tip)}"' + (' tabindex="0"' if focus else "")) if tip else ""
    o = f' fill-opacity="{opacity}"' if opacity < 1 else ""
    return (f'<circle class="{cls} c-fill c-dot" cx="{f(x)}" cy="{f(y)}" r="{f(r)}" '
            f'stroke="var(--c-panel)" stroke-width="{f(RING)}"{o}{t}/>')


def series_line(points, cls="c-story", w=W_DATA):
    """2px line, round joins. `None` in points breaks the line — a gap in the
    data is drawn as a gap, never interpolated across."""
    segs, cur = [], []
    for p in points:
        if p is None:
            if len(cur) > 1:
                segs.append(cur)
            cur = []
        else:
            cur.append(p)
    if len(cur) > 1:
        segs.append(cur)
    d = "".join("M" + "L".join(f"{f(x)} {f(y)}" for x, y in s) for s in segs)
    return (f'<path class="{cls}" d="{d}" fill="none" stroke-width="{f(w)}" '
            f'stroke-linejoin="round" stroke-linecap="round"/>')


def ci_band(upper, lower, cls="c-story"):
    """Confidence band: the series hue as a ~12% wash, no edge stroke."""
    pts = upper + list(reversed(lower))
    d = "M" + "L".join(f"{f(x)} {f(y)}" for x, y in pts) + "Z"
    return f'<path class="{cls} c-fill c-wash" d="{d}"/>'


def interval(x0, x1, y, cls="c-story", cap=6):
    """A horizontal CI whisker with measured end caps."""
    return (line(x0, y, x1, y, cls, 1.5) +
            line(x0, y - cap / 2, x0, y + cap / 2, cls, 1.5) +
            line(x1, y - cap / 2, x1, y + cap / 2, cls, 1.5))


def comparison_bracket(x, y0, y1, label, sub=None, side=1):
    """A bracket joining two compared rows, with the measured difference."""
    k = 8 * side
    d = f"M{f(x)} {f(y0)}H{f(x + k)}V{f(y1)}H{f(x)}"
    out = [f'<path class="c-ink" d="{d}" fill="none" stroke-width="1.25"/>']
    ym = (y0 + y1) / 2
    anchor = "start" if side > 0 else "end"
    out.append(text(x + k + 6 * side, ym - 2, label, "c-ink", 12.5, anchor, "sans", 500))
    if sub:
        out.append(text(x + k + 6 * side, ym + 14, sub, "c-body", 10.5, anchor, "mono"))
    return "".join(out)


def outlier_marker(x, y, label=None, rule=None, dx=18, dy=-18, tip=None):
    """Coral ring + dot. The TEXT stays in ink — coral as text fails contrast
    (3.9:1) and text never wears a data colour. The marker states its rule."""
    t = f' data-tip="{esc(tip)}" tabindex="0"' if tip else ""
    out = [f'<circle class="c-mark" cx="{f(x)}" cy="{f(y)}" r="8" fill="none" '
           f'stroke-width="1.5"{t}/>',
           f'<circle class="c-mark c-fill" cx="{f(x)}" cy="{f(y)}" r="3.2"/>']
    if label:
        out.append(leader(x, y, dx, dy, label, sub=rule, r_off=9))
    return "".join(out)


def leader(x, y, dx, dy, label, sub=None, r_off=4):
    """Annotation leader: elbowed, never curved. Sans text — annotations are
    sentences, and sentences are never mono."""
    ang = math.atan2(dy, dx)
    sx, sy = x + r_off * math.cos(ang), y + r_off * math.sin(ang)
    mx, my = x + dx, y + dy
    run = 14 if dx >= 0 else -14
    ex = mx + run
    anchor = "start" if dx >= 0 else "end"
    tx = ex + (5 if dx >= 0 else -5)
    out = [f'<path class="c-lead" d="M{f(sx)} {f(sy)}L{f(mx)} {f(my)}H{f(ex)}" '
           f'fill="none" stroke-width="{W_HAIR}"/>',
           text(tx, my + 4, label, "c-ink c-halo", 12.5, anchor, "sans", 500)]
    if sub:
        out.append(text(tx, my + 19, sub, "c-body c-halo", 10.5, anchor, "mono"))
    return "".join(out)


def measurement_label(x, y, s, anchor="start", cls="c-ink"):
    """A value readout at a mark: mono numerals (budget 01)."""
    return text(x, y, s, cls + " c-halo", 12, anchor, "mono", 500)


def direct_label(x, y, s, value=None, swatch="c-context", anchor="start"):
    """End-of-line identity: a short swatch, the name in sans, the value in mono.
    The value is a tspan, so it follows the name at its real width in any font."""
    sw = 10
    if anchor == "start":
        sx, tx = x, x + sw + 5
    else:
        sx, tx = x - sw, x - sw - 5
    v = (f'<tspan dx="6" font-family="{MONO}" font-weight="400" font-size="11" '
         f'class="c-body" letter-spacing="0.04em">{esc(value)}</tspan>') if value else ""
    return (line(sx, y, sx + sw, y, swatch, 2.5, 'stroke-linecap="round"') +
            f'<text class="c-ink c-halo" x="{f(tx)}" y="{f(y + 4)}" font-size="12" '
            f'font-family="{SANS}" font-weight="500" text-anchor="{anchor}">{esc(s)}{v}</text>')


def legend(items, x, y):
    """Present for ≥2 series. Swatch + sans label; the swatch carries identity."""
    out, cx = [], x
    for cls, lab in items:
        out.append(line(cx, y, cx + 16, y, cls, 2.5, 'stroke-linecap="round"'))
        out.append(text(cx + 22, y + 4, lab, "c-body", 12, "start", "sans"))
        cx += 22 + len(lab) * 6.6 + 22
    return "".join(out)


def reference_rule(x=None, y=None, extent=(0, 0), label=None, horizontal=False):
    """DASHED means threshold, benchmark or projection — and nothing else."""
    if horizontal:
        out = [line(extent[0], y, extent[1], y, "c-ink", 1.25, 'stroke-dasharray="4 4"')]
        if label:
            out.append(text(extent[1], y - 6, label, "c-ink", 11.5, "end", "sans", 500))
    else:
        out = [line(x, extent[0], x, extent[1], "c-ink", 1.25, 'stroke-dasharray="4 4"')]
        if label:
            out.append(text(x + 6, extent[0] + 11, label, "c-ink", 11.5, "start", "sans", 500))
    return "".join(out)


def missing_band(x0, x1, y0, y1, label="Missing"):
    """Should exist, doesn't. A 45° hatch over the gap, the line broken under it,
    and the word — never an interpolated line bridging it."""
    pid = f"hatch{abs(hash((x0, x1, y0))) % 10**6}"
    return (f'<defs><pattern id="{pid}" width="6" height="6" patternUnits="userSpaceOnUse" '
            f'patternTransform="rotate(45)"><path d="M0 0V6" class="c-grid" '
            f'stroke-width="1.5"/></pattern></defs>'
            f'<rect x="{f(x0)}" y="{f(y0)}" width="{f(x1 - x0)}" height="{f(y1 - y0)}" '
            f'fill="url(#{pid})"/>' +
            text((x0 + x1) / 2, y0 + 14, label.upper(), "c-dim", 10, "middle", "mono", 500))


def na_start(x, y, label):
    """Not applicable: the series did not exist yet. Nothing is drawn before it
    — not a zero, not a gap — and the start is capped and labelled."""
    return (line(x, y - 6, x, y + 6, "c-ink", 1.5) +
            text(x - 6, y + 4, label, "c-body", 11, "end", "sans"))


def null_mark(x, y, tip="No baseline"):
    """Null: the value can't be computed (e.g. no prior period). An em dash in
    the dim ink — never a zero, which would be a finding."""
    return text(x, y, "—", "c-dim", 13, "middle", "mono",
                extra=f'data-tip="{esc(tip)}"')


def selected_state(x, y, r=11):
    """Selection / keyboard focus on a mark: a sighting ring, not a glow."""
    return (f'<circle class="c-story" cx="{f(x)}" cy="{f(y)}" r="{r}" fill="none" '
            f'stroke-width="1.5" stroke-dasharray="3 2"/>')


# ---------------------------------------------------------------------------
# Figure wrapper
# ---------------------------------------------------------------------------
STYLE = """
svg.dsc-chart{--c-ink:%(ink)s;--c-body:%(body)s;--c-dim:%(dim)s;--c-rule:%(rule)s;
--c-faint:%(faint)s;--c-panel:%(panel)s;--c-story:%(story)s;--c-context:%(context)s;
--c-mark:%(mark)s;--c-pos:%(pos)s;--c-neg:%(neg)s}
@media (prefers-color-scheme:dark){svg.dsc-chart{--c-ink:%(d_ink)s;--c-body:%(d_body)s;
--c-dim:%(d_dim)s;--c-rule:%(d_rule)s;--c-faint:%(d_faint)s;--c-panel:%(d_panel)s;
--c-story:%(d_story)s;--c-context:%(d_context)s;--c-mark:%(d_mark)s;--c-pos:%(d_pos)s;
--c-neg:%(d_neg)s}}
"""
CLASSES = """
svg.dsc-chart .c-axis{stroke:var(--c-body)} svg.dsc-chart .c-grid{stroke:var(--c-rule)}
svg.dsc-chart .c-lead{stroke:var(--c-body)}
svg.dsc-chart .c-ink{stroke:var(--c-ink);fill:var(--c-ink)}
svg.dsc-chart path.c-ink{fill:none}
svg.dsc-chart .c-body{fill:var(--c-body)} svg.dsc-chart .c-dim{fill:var(--c-dim)}
svg.dsc-chart .c-story{stroke:var(--c-story)} svg.dsc-chart .c-context{stroke:var(--c-context)}
svg.dsc-chart .c-mark{stroke:var(--c-mark)} svg.dsc-chart .c-pos{stroke:var(--c-pos)}
svg.dsc-chart .c-neg{stroke:var(--c-neg)}
svg.dsc-chart .c-fill.c-story{fill:var(--c-story);stroke:none}
svg.dsc-chart .c-fill.c-context{fill:var(--c-context);stroke:none}
svg.dsc-chart .c-fill.c-mark{fill:var(--c-mark);stroke:none}
svg.dsc-chart .c-fill.c-pos{fill:var(--c-pos);stroke:none}
svg.dsc-chart .c-fill.c-neg{fill:var(--c-neg);stroke:none}
svg.dsc-chart .c-dot{stroke:var(--c-panel)}
svg.dsc-chart .c-wash{fill-opacity:.12}
svg.dsc-chart text[class]{stroke:none}
svg.dsc-chart text.c-halo{stroke:var(--c-panel);stroke-width:4px;stroke-linejoin:round;paint-order:stroke}
svg.dsc-chart text.c-halo tspan{stroke:var(--c-panel)}
svg.dsc-chart .c-hit{fill:transparent;stroke:none;cursor:crosshair}
svg.dsc-chart [data-tip]:focus{outline:none}
svg.dsc-chart [data-tip]:focus-visible{stroke:var(--c-ink);stroke-width:2}
svg.dsc-chart .c-bar.c-story{fill:var(--c-story)} svg.dsc-chart .c-bar.c-context{fill:var(--c-context)}
svg.dsc-chart .c-bar.c-neg{fill:var(--c-neg)} svg.dsc-chart .c-bar.c-pos{fill:var(--c-pos)}
svg.dsc-chart .c-bar.c-mark{fill:var(--c-mark)} svg.dsc-chart .c-bar{stroke:none}
"""


def style_block(tokens=True):
    """tokens=False: the host page defines --c-* itself (e.g. with a theme
    switch); only the classes are emitted."""
    d = {**LIGHT, **{"d_" + k: v for k, v in DARK.items()}}
    return ((STYLE % d) if tokens else "") + CLASSES


def page_tokens():
    """--c-* for a page with a light/dark switch: bare :root, OS dark, and
    explicit [data-theme]."""
    lt = ";".join(f"--c-{k}:{v}" for k, v in LIGHT.items())
    dk = ";".join(f"--c-{k}:{v}" for k, v in DARK.items())
    return (f":root{{{lt}}}\n@media (prefers-color-scheme:dark){{:root:not([data-theme=light]){{{dk}}}}}\n"
            f":root[data-theme=dark]{{{dk}}}\n:root[data-theme=light]{{{lt}}}\n")


def bar(x0, x1, y_base, y_top, cls="c-story", r=4, tip=None, horizontal=False):
    """Bar ≤24px thick, 4px rounded data-end, square at the baseline.
    horizontal=True: x0 is the baseline x, x1 the data end; y_base/y_top the band."""
    t = f' data-tip="{esc(tip)}" tabindex="0"' if tip else ""
    if horizontal:
        b, e, y0, y1 = x0, x1, y_base, y_top
        s = 1 if e >= b else -1
        rr = min(r, abs(e - b))
        d = (f"M{f(b)} {f(y0)}H{f(e - s*rr)}Q{f(e)} {f(y0)} {f(e)} {f(y0+rr)}"
             f"V{f(y1-rr)}Q{f(e)} {f(y1)} {f(e - s*rr)} {f(y1)}H{f(b)}Z")
    else:
        b, e = y_base, y_top
        s = -1 if e <= b else 1
        rr = min(r, abs(e - b))
        d = (f"M{f(x0)} {f(b)}V{f(e - s*rr)}Q{f(x0)} {f(e)} {f(x0+rr)} {f(e)}"
             f"H{f(x1-rr)}Q{f(x1)} {f(e)} {f(x1)} {f(e - s*rr)}V{f(b)}Z")
    return f'<path class="c-bar {cls}" d="{d}"{t}/>'


def hit(x, y, w, h, tip):
    """Invisible hover/focus target, larger than the mark (≥24px)."""
    return (f'<rect class="c-hit" x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" '
            f'data-tip="{esc(tip)}" tabindex="0"/>')


def svg(body, w, h, label, standalone=False):
    st = f"<style>{style_block()}</style>" if standalone else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" class="dsc-chart" '
            f'viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
            f'aria-label="{esc(label)}" fill="none">{st}{body}</svg>')


class Figure(dict):
    """What every chart returns. The title states the finding; the dek says how
    to read it; the provenance line carries n, source and date; the table is
    the accessible twin and always holds every value."""

    def __init__(self, **kw):
        super().__init__(**kw)

    def to_json(self):
        return json.dumps({k: v for k, v in self.items() if k != "svg"})
