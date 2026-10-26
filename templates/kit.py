"""
kit.py — the shared layer behind the slide and social templates.

    import sys; sys.path.insert(0, "templates")
    import kit as K

Everything here is either a page shell (fonts, tokens, the enrichment CSS) or
one of the enrichment elements in templates/ENRICHMENT.md, returned as an HTML
or SVG string. The elements paint with the geometry library's semantic classes
(ink, body, faint, active, mark) and those classes read the design tokens, so
one template renders correctly on paper, on navy and in a single ink.

Rules carried into code, as in geometry/astrolabe.py:

  * the decorative layer is `faint` only; delete it and the page still reads
    (design test 7). construction(), orbit_fill() and dither() never take
    another colour.
  * data_cells() needs real values. There is no default pattern.
  * index markers and the outlier ring are for the data, not for decoration;
    the outlier ring requires the rule that flagged the point.
"""

from __future__ import annotations

import base64
import json
import math
import os
import re
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "geometry"))

import astrolabe as A  # noqa: E402

TOKENS = json.load(open(os.path.join(ROOT, "tokens", "dist", "tokens.json"), encoding="utf-8"))["tokens"]
FONT_DIR = os.path.join(ROOT, "decisions", "fonts")
BITMAPS = os.path.join(ROOT, "illustrations", "bitmaps")
THETA = A.THETA
KAPPA = A.KAPPA
GAP = A.GAP

# Illustrations whose rights are confirmed public domain (ILLUSTRATION.md §4).
# The astrolabe plate, comet, orbit, moon, eclipse and Scorpio are left out
# until their sources are confirmed.
CLEARED = {"cygnus", "cygnus-outside", "libra", "cancer-globe", "cancer-sky", "hero-night"}


def tok(key: str, mode: str = "light") -> str:
    return TOKENS[key][mode]


# ---------------------------------------------------------------------------
# Page shell
# ---------------------------------------------------------------------------
def _rel(path: str, out_dir: str) -> str:
    return os.path.relpath(path, out_dir).replace(os.sep, "/")


def font_css(out_dir: str) -> str:
    """@font-face rules for the brand faces in decisions/fonts, relative to
    the page being written. local() first, so an installed face wins."""
    def url(name):
        # The files are named with a literal %5B; a URL needs the % escaped.
        return _rel(os.path.join(FONT_DIR, name), out_dir).replace("%", "%25")
    fr = url("Fraunces%5BSOFT,WONK,opsz,wght%5D.ttf")
    rx = url("ReadexPro%5BHEXP,wght%5D.ttf")
    return f"""
@font-face{{font-family:Fraunces;src:local('Fraunces'),url('{fr}');font-weight:100 900}}
@font-face{{font-family:'Readex Pro';src:local('Readex Pro'),url('{rx}');font-weight:160 700}}
@font-face{{font-family:'IBM Plex Mono';src:local('IBM Plex Mono'),url('{url("IBMPlexMono-Regular.ttf")}');font-weight:400}}
@font-face{{font-family:'IBM Plex Mono';src:local('IBM Plex Mono Medium'),url('{url("IBMPlexMono-Medium.ttf")}');font-weight:500}}
@font-face{{font-family:Amiri;src:local('Amiri'),url('{url("Amiri-Regular.ttf")}');font-weight:400}}
@font-face{{font-family:Vazirmatn;src:local('Vazirmatn'),url('{url("Vazirmatn%5Bwght%5D.ttf")}');font-weight:100 900}}
"""


def lockup(kind: str = "compact") -> str:
    """The approved wordmark lockup, inline, coloured by the page
    (--wm-ink follows --ink, --wm-accent follows --active)."""
    s = open(os.path.join(ROOT, "wordmark", "web", f"lockup-{kind}.svg"), encoding="utf-8").read()
    s = re.sub(r"<metadata>.*?</metadata>", "", s, flags=re.S)
    s = re.sub(r"<\?xml[^>]*>", "", s)
    return s.replace("<svg ", '<svg class="lockup" ', 1)


def page_doc(pages: list[str], out_dir: str, width: int, height: int, medium: str, title: str) -> str:
    css = open(os.path.join(HERE, "enrich.css"), encoding="utf-8").read()
    tokens_css = _rel(os.path.join(ROOT, "tokens", "dist", "tokens.css"), out_dir)
    return f"""<!doctype html>
<html lang="en" data-medium="{medium}"><head><meta charset="utf-8">
<title>{title}</title>
<link rel="stylesheet" href="{tokens_css}">
<style>{font_css(out_dir)}
:root{{--page-w:{width}px;--page-h:{height}px}}
@page{{size:{width}px {height}px;margin:0}}
{css}</style></head>
<body>{''.join(pages)}</body></html>"""


def page(body: str, theme: str = "light", cls: str = "", style: str = "") -> str:
    """One page. theme: light (paper), dark (navy) or brass (the editorial ground)."""
    data_theme = "dark" if theme == "dark" else "light"
    return (f'<section class="pg pg--{theme} {cls}" data-theme="{data_theme}" style="{style}">'
            f'{body}</section>')


# ---------------------------------------------------------------------------
# SVG helpers — page coordinates, token colours
# ---------------------------------------------------------------------------
def svg(w: float, h: float, body: str, cls: str = "layer", style: str = "") -> str:
    return (f'<svg class="geo {cls}" viewBox="0 0 {A.f(w)} {A.f(h)}" width="{A.f(w)}" '
            f'height="{A.f(h)}" fill="none" aria-hidden="true" style="{style}">{body}</svg>')


# 1 · Construction backdrop (geometry families A and E) ----------------------
def construction(w: float, h: float, cx: float, cy: float, r: float, hair: float = 1.5,
                 scale_from: float | None = None) -> str:
    """The generating geometry, left visible: nested broken rings stepping in
    by the tangent ratio, the inner tangent circle, the sight axis and the
    centre lines, and one graduated sector. faint only, cropped by the page.

    Place it so the composition's headline number or title sits inside the
    ring, never across a stroke."""
    out = []
    for i in range(4):
        rr = r * KAPPA ** (i * 0.5)
        out.append(A.broken_ring(cx, cy, rr, GAP * (1 + i * 0.35), THETA, "faint", hair * (1.6 if i == 0 else 1)))
    ri = r * KAPPA
    bx, by = A.polar(cx, cy, r - ri, THETA + 180)
    out.append(A.circle(bx, by, ri, "faint", hair))
    out.append(A.line(*A.polar(cx, cy, r * 1.35, THETA), *A.polar(cx, cy, r * 1.35, THETA + 180), "faint", hair,
                      **{"stroke-dasharray": f"{hair * 4} {hair * 4}"}))
    out.append(A.line(cx - r * 1.2, cy, cx + r * 1.2, cy, "faint", hair))
    out.append(A.line(cx, cy - r * 1.2, cx, cy + r * 1.2, "faint", hair))
    a0 = scale_from if scale_from is not None else THETA + 120
    out.append(_radial_scale(cx, cy, r, a0, a0 + 96, 2.0, 5, r * 0.035, r * 0.016, "faint", hair))
    out.append(A.dot(*A.polar(cx, cy, r, THETA + 180), max(hair * 2.4, 3), "faint"))
    return svg(w, h, "".join(out))


def _radial_scale(cx, cy, r, a0, a1, step, major_every, major, minor, cls, w):
    if abs(a1 - a0) >= 330:
        raise ValueError("Graduate a sector, never the full circle (it reads as a clock).")
    out, i, a = [], 0, a0
    while a <= a1 + 1e-9:
        h = major if i % major_every == 0 else minor
        out.append(A.line(*A.polar(cx, cy, r, a), *A.polar(cx, cy, r - h, a), cls, w))
        a += step
        i += 1
    return "".join(out)


# 2 · Measuring edge (B02) -----------------------------------------------------
def measuring_edge(h: float, x: float = 0, y0: float = 0, y1: float | None = None, count: int = 41,
                   major_every: int = 5, major: float = 18, minor: float = 8, hair: float = 1.5,
                   side: str = "left", labels: list[str] | None = None, label_size: float = 15,
                   active_at: float | None = None) -> str:
    """The design spine: a ticked rule down the margin. Content aligns to it.
    `active_at` (0..1) seats one index tick in active blue, e.g. the section
    position in a deck. side='right' mirrors it for RTL pages."""
    y1 = h if y1 is None else y1
    width = major + (label_size * 4 if labels else 4) + 8
    sgn = 1 if side == "left" else -1
    x0 = x if side == "left" else width - x
    out = [A.line(x0, y0, x0, y1, "body", hair)]
    for i in range(count):
        y = y0 + (y1 - y0) * i / (count - 1)
        L = major if i % major_every == 0 else minor
        out.append(A.line(x0, y, x0 + sgn * L, y, "body", hair))
    if labels:
        n = len(labels)
        for i, lab in enumerate(labels):
            y = y0 + (y1 - y0) * i / max(n - 1, 1)
            out.append(f'<text x="{A.f(x0 + sgn * (major + 8))}" y="{A.f(y + label_size * 0.35)}" '
                       f'class="body fill" fill="currentColor" font-size="{label_size}" '
                       f'font-family="IBM Plex Mono, monospace" text-anchor="{"start" if sgn > 0 else "end"}" '
                       f'letter-spacing="0.12em">{lab}</text>')
    if active_at is not None:
        y = y0 + (y1 - y0) * active_at
        out.append(A.line(x0 - sgn * 4, y, x0 + sgn * (major + 10), y, "active", hair * 2.2))
        out.append(A.dot(x0, y, hair * 2.6, "active"))
    return svg(width, h, "".join(out), cls="edge", style=f"width:{A.f(width)}px;height:{A.f(h)}px")


# 3 · Tally position (G02) -----------------------------------------------------
def tally(done: int, total: int, height: float = 26, pitch: float = 9, gap: float = 14,
          w: float = 3.0) -> str:
    """'Page 3 of 8' as a tally: done in active, to come in faint. Groups of five."""
    out, x = [], w
    for i in range(total):
        out.append(A.line(x, 2, x, 2 + height, "active" if i < done else "faint", w,
                          **{"stroke-linecap": "round"}))
        x += pitch
        if (i + 1) % 5 == 0:
            x += gap - pitch + pitch * 0.5
    width = x + w
    return svg(width, height + 4, "".join(out), cls="tally",
               style=f"width:{A.f(width)}px;height:{A.f(height + 4)}px")


# 4 · Orbit fill (H05) ---------------------------------------------------------
def orbit_fill(w: float, h: float, pitch: float = 120, r: float = 30, hair: float = 1.5) -> str:
    """The orbit motif as a field: broken rings with one seated marker, on a
    staggered grid, faint only. For large empty areas, never behind text."""
    out = []
    rows = int(h / (pitch * 0.866)) + 2
    cols = int(w / pitch) + 2
    for j in range(rows):
        for i in range(cols):
            cx = i * pitch + (pitch / 2 if j % 2 else 0)
            cy = j * pitch * 0.866
            # the marker walks round the ring, so the field reads as a sequence
            a = THETA + 180 + ((i * 37 + j * 61) % 360)
            out.append(A.broken_ring(cx, cy, r, GAP, THETA, "faint", hair))
            out.append(A.dot(*A.polar(cx, cy, r, a), hair * 2, "faint"))
    return svg(w, h, "".join(out))


# 5 · Data as texture (F05) ----------------------------------------------------
def data_cells(values: list[float], w: float, h: float, rows: int = 12, gap_ratio: float = 0.24,
               cls: str = "faint", highlight: tuple[int, ...] = (), cols_per: int = 1) -> str:
    """A column of cells per value, filled to its share of the maximum: the
    piece's own data as a texture. `highlight` columns take active."""
    if not values:
        raise ValueError("data_cells() renders real values; pass them.")
    n = len(values) * cols_per + (len(values) - 1)   # one empty column between values
    cw = w / n
    ch = h / rows
    s = min(cw, ch) * (1 - gap_ratio)
    mx = max(values)
    out = []
    for i, v in enumerate(values):
        filled = round(rows * v / mx)
        c = "active" if i in highlight else cls
        for q in range(cols_per):
            col = i * (cols_per + 1) + q
            for k in range(filled):
                x = col * cw + (cw - s) / 2
                y = h - (k + 1) * ch + (ch - s) / 2
                out.append(f'<rect x="{A.f(x)}" y="{A.f(y)}" width="{A.f(s)}" height="{A.f(s)}" '
                           f'class="{c} fill" fill="currentColor"/>')
    return svg(w, h, "".join(out), cls="cells")


# 6 · Graduated sector, for one share (B03 + B04) -----------------------------
def gauge(share: float, size: float = 520, hair: float = 2, label: str = "") -> str:
    """One share as an instrument reading, not a donut: a 240° graduated
    sector, the share swept in active, an index mark where it lands."""
    if not 0 <= share <= 1:
        raise ValueError("gauge() takes a share between 0 and 1.")
    cx = cy = size / 2
    r = size * 0.40
    a0, sweep = 150.0, 240.0
    a1 = a0 + sweep * share
    out = [A.ring_arc(cx, cy, r, a0, a0 + sweep, "faint", hair * 3),
           _radial_scale(cx, cy, r - hair * 6, a0, a0 + sweep, 6, 5, size * 0.04, size * 0.018, "body", hair * 0.75)]
    if share > 0:
        out.append(A.ring_arc(cx, cy, r, a0, a1, "active", hair * 3))
    out.append(A.line(*A.polar(cx, cy, r - size * 0.07, a1), *A.polar(cx, cy, r + size * 0.035, a1),
                      "active", hair * 1.6))
    out.append(A.dot(*A.polar(cx, cy, r, a1), hair * 3.4, "active"))
    if label:
        out.append(f'<text x="{A.f(cx)}" y="{A.f(cy + r * 0.62)}" class="body fill" fill="currentColor" '
                   f'font-size="{A.f(size * 0.036)}" font-family="IBM Plex Mono, monospace" '
                   f'text-anchor="middle" letter-spacing="0.12em">{label}</text>')
    return svg(size, size, "".join(out), cls="gauge", style=f"width:{A.f(size)}px;height:{A.f(size)}px")


# 7 · Outlier marker (the only coral) -----------------------------------------
def outlier_ring(size: float = 44, rule: str = "") -> str:
    """Coral ring and dot, as on a chart. Requires the rule that flagged it."""
    if not rule:
        raise ValueError("An outlier states its test: pass rule=, e.g. 'robust z > 7'.")
    c = size / 2
    body = A.circle(c, c, size * 0.40, "mark", size * 0.06) + A.dot(c, c, size * 0.15, "mark")
    return svg(size, size, body, cls="outlier", style=f"width:{A.f(size)}px;height:{A.f(size)}px") \
        .replace('aria-hidden="true"', f'role="img" aria-label="Outlier: {rule}"')


# 8 · Process line (E04 nodes + E05 leaders) ----------------------------------
def process(steps: list[tuple[str, str]], w: float, h: float = 150, hair: float = 1.5,
            active: int | None = None, value_size: float = 34, label_size: float = 22) -> str:
    """Steps as nodes on one construction line. Each step is (value, label).
    Open nodes are steps, the one `active` node is the result."""
    n = len(steps)
    y = 28
    out = [A.line(0, y, w, y, "body", hair)]
    for i, (val, lab) in enumerate(steps):
        x = 14 + (w - 28) * i / (n - 1)
        cls = "active" if i == active else "ink"
        if i == active:
            out.append(A.dot(x, y, 9, "active"))
        else:
            out.append(A.circle(x, y, 9, "ink", hair * 1.6, fill="var(--pg-ground)"))
        out.append(A.line(x, y + 14, x, y + 44, "faint", hair))
        anchor = "start" if i == 0 else ("end" if i == n - 1 else "middle")
        out.append(f'<text x="{A.f(x)}" y="{A.f(y + 44 + value_size * 1.12)}" class="{cls} fill" fill="currentColor" '
                   f'font-size="{A.f(value_size)}" font-family="IBM Plex Mono, monospace" font-weight="500" '
                   f'text-anchor="{anchor}">{val}</text>')
        out.append(f'<text x="{A.f(x)}" y="{A.f(y + 44 + value_size * 1.12 + label_size * 1.5)}" class="body fill" fill="currentColor" '
                   f'font-size="{A.f(label_size)}" font-family="Readex Pro, sans-serif" font-weight="300" '
                   f'text-anchor="{anchor}">{lab}</text>')
    return svg(w, h, "".join(out), cls="process", style=f"width:{A.f(w)}px;height:{A.f(h)}px;overflow:visible")


# 9 · Dither (the illustration layer's treatment, as a tone) ------------------
_BAYER8 = [
    [0, 32, 8, 40, 2, 34, 10, 42], [48, 16, 56, 24, 50, 18, 58, 26],
    [12, 44, 4, 36, 14, 46, 6, 38], [60, 28, 52, 20, 62, 30, 54, 22],
    [3, 35, 11, 43, 1, 33, 9, 41], [51, 19, 59, 27, 49, 17, 57, 25],
    [15, 47, 7, 39, 13, 45, 5, 37], [63, 31, 55, 23, 61, 29, 53, 21],
]


def _png(w: int, h: int, rows: list[bytes]) -> bytes:
    """A 1-bit-in-alpha greyscale+alpha PNG, written without Pillow."""
    def chunk(t, d):
        c = t + d
        return len(d).to_bytes(4, "big") + c + zlib.crc32(c).to_bytes(4, "big")
    raw = b"".join(b"\x00" + r for r in rows)
    ihdr = w.to_bytes(4, "big") + h.to_bytes(4, "big") + bytes([8, 4, 0, 0, 0])
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")


def dither(w: int, h: int, kind: str = "rise", cell: int = 3, lo: float = 0.0, hi: float = 0.34,
           cx: float = 0.85, cy: float = 0.15) -> str:
    """An ordered-dither tone field as a data: URI mask, coloured by the page.

    kind='rise'   ink gathers toward the bottom edge
    kind='glow'   ink gathers round (cx, cy), as fractions of the page
    Ink is capped at `hi` (34%, the hero sky's ceiling, ILLUSTRATION.md §2.7)
    so text can sit on it. Never scale the result: one cell is `cell` px."""
    gw, gh = math.ceil(w / cell), math.ceil(h / cell)
    rows = []
    for j in range(gh):
        row = bytearray()
        for i in range(gw):
            u, v = i / max(gw - 1, 1), j / max(gh - 1, 1)
            if kind == "rise":
                t = v ** 2.2
            elif kind == "glow":
                d = math.hypot((u - cx) * w / h, v - cy)
                t = max(0.0, 1 - d / 0.9) ** 1.8
            else:
                raise ValueError("kind is 'rise' or 'glow'")
            level = lo + (hi - lo) * t
            on = level * 64 > _BAYER8[j % 8][i % 8]
            px = b"\x00\xff" if on else b"\x00\x00"
            row += px * cell
        for _ in range(cell):
            rows.append(bytes(row[: w * 2]))
    data = _png(w, h, rows[:h])
    return "data:image/png;base64," + base64.b64encode(data).decode()


def dither_layer(w: int, h: int, **kw) -> str:
    uri = dither(w, h, **kw)
    return f'<div class="dither" style="--m:url({uri})"></div>'


# 10 · Illustration (one-bit masks, coloured by meaning) ----------------------
def art(name: str, out_dir: str, layers: dict[str, str], style: str = "") -> str:
    """An illustration from illustrations/bitmaps as stacked masks. `layers`
    maps layer → colour token, e.g. {"lines": "ink", "stars": "active"}.
    Only illustrations with confirmed rights are allowed (ILLUSTRATION.md §4)."""
    if name not in CLEARED:
        raise ValueError(f"{name}: rights not confirmed for publishing (ILLUSTRATION.md §4).")
    man = {m["name"]: m for m in json.load(open(os.path.join(BITMAPS, "manifest.json"), encoding="utf-8"))}
    m = man[name]
    W, H = m["size"]
    spans = []
    for layer, colour in layers.items():
        if colour == "mark" and layer != "outside":
            raise ValueError("Coral appears in the illustration layer only on 'outside' stars.")
        # Inlined: browsers refuse a CSS mask from file:// (masks need CORS),
        # and an inlined page travels as one file. The masks are 10–100 KB.
        raw = open(os.path.join(BITMAPS, name, m["layers"][layer]), "rb").read()
        src = "data:image/png;base64," + base64.b64encode(raw).decode()
        spans.append(f'<span style="--c:var(--{colour});--m:url({src})"></span>')
    return f'<div class="art" style="--ar:{W}/{H};{style}">{"".join(spans)}</div>'


# 11 · Callout marker (numbered, joined to the data) --------------------------
def callout(n: int, text: str) -> str:
    return f'<div class="callout"><span class="callout__n">{n:02d}</span><span class="callout__t">{text}</span></div>'
