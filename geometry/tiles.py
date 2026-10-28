"""
tiles.py — the .describe( tile set: 36 square stamps built only from astrolabe.py.

    python3 geometry/tiles.py            writes geometry/tiles/tile-01.svg .. tile-36.svg and tiles.html

A tile is one idea from the mark's grammar on a 200-unit square: a ring, a
sighting, a count, a field, a scale or a seated star. Rules, same as the rest
of the system:

  * every tile has exactly ONE active element (the thing being pointed at);
  * ink, body and faint do the rest, no other colour, coral never;
  * no new shapes: each tile is a composition of existing primitives, so the
    set can only ever look like the mark.

Use a tile as an icon, an avatar, a section marker, a bullet, or in a grid where
one tile is singled out (templates/kit.py tile_grid()). The classes are the
semantic ones (ink, body, faint, active), so a tile recolours with its ground.
"""

from __future__ import annotations

import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import astrolabe as A  # noqa: E402

C = 100.0
T = A.THETA
K = A.KAPPA


def _star_at(x, y, k=1.5, cls="active"):
    return (f'<g transform="translate({A.f(x)} {A.f(y)}) scale({k}) translate({A.f(-x)} {A.f(-y)})">'
            f'{A.star(x, y, cls=cls)}</g>')


def _on_ring(r, a=None):
    return A.polar(C, C, r, T if a is None else a)


def _uprights(n, struck=False, active_last=True):
    pitch, h = 22.0, 84.0
    total = 4 * pitch if struck else (n - 1) * pitch
    x0, y0 = C - total / 2, C - h / 2
    out = []
    for k in range(min(n, 4)):
        last = (not struck) and k == n - 1 and active_last
        out.append(A.line(x0 + k * pitch, y0, x0 + k * pitch, y0 + h, "active" if last else "ink", A.W_MARK * 1.4))
    if struck:
        out.append(A.line(x0 - 8, y0 + h - 12, x0 + 3 * pitch + 8, y0 + 12, "active", A.W_MARK * 1.4))
    return "".join(out)


def _cells(n, taken, shape="plain"):
    size = 120.0
    cell = size / n
    s = cell * 0.76
    x0 = y0 = C - size / 2
    out = []
    for j in range(n):
        for i in range(n):
            x, y = x0 + i * cell, y0 + j * cell
            if (i, j) == taken:
                cls, extra = "active", ""
            else:
                if shape == "ramp" and (i + j) < n - 1:
                    continue
                cls = "faint"
            out.append(f'<rect x="{A.f(x)}" y="{A.f(y)}" width="{A.f(s)}" height="{A.f(s)}" class="{cls} fill" fill="currentColor"/>')
    return "".join(out)


def _vernier():
    """Two graduated rules at slightly different pitch: one tick lines up."""
    x0, x1 = 28.0, 172.0
    out = [A.line(x0, 88, x1, 88, "body", A.W_HAIR), A.line(x0, 112, x1, 112, "body", A.W_HAIR)]
    for i in range(0, 21):
        x = x0 + (x1 - x0) * i / 20
        out.append(A.line(x, 88, x, 88 - (12 if i % 5 == 0 else 6), "body", A.W_HAIR))
    for i in range(0, 20):
        x = x0 + (x1 - x0) * i / 19
        on = i == 14
        out.append(A.line(x, 112, x, 112 + (16 if on else (12 if i % 5 == 0 else 6)), "active" if on else "body",
                          A.W_MARK if on else A.W_HAIR))
    return "".join(out)


def _tick_with_index():
    out = [A.tick_row(30, 112, 140, 29, 4, 7, 15, cls="body")]
    out.append(A.line(30, 112, 170, 112, "body", A.W_HAIR))
    x = 30 + 140 * 19 / 28
    out.append(A.line(x, 112, x, 80, "active", A.W_MARK) + A.dot(x, 76, 5, "active"))
    return "".join(out)


def _edge_with_index():
    out = [A.measuring_edge(62, 30, 170, 21, 5, cls="body")]
    y = 30 + 140 * 7 / 20
    out.append(A.line(62, y, 142, y, "active", A.W_MARK) + A.dot(146, y, 5, "active"))
    return "".join(out)


def _dim():
    return (A.dimension(36, 112, 164, 112, "", "body", 14, "body")
            + A.line(164, 112, 164, 52, "faint", A.W_HAIR) + A.dot(164, 52, 5.5, "active"))


def _hist():
    vals = [0.16, 0.34, 0.58, 0.86, 1.0, 0.74, 0.46, 0.26, 0.12]
    out = [A.stepped_field(vals, 30, 158, 140, 100, "body")]
    x = 30 + 140 * 4.5 / 9
    out.append(A.line(x, 158, x, 58, "active", A.W_MARK) + A.dot(x, 58, 5, "active"))
    return "".join(out)


TILES = [
    # --- rings
    ("broken-ring", "Ring", lambda: A.broken_ring(C, C, 64, cls="ink") + A.dot(*_on_ring(64), 6, "active")),
    ("nested", "Nested", lambda: A.nested_rings(C, C, 72, 3, cls="body", w=A.W_MARK)
        + A.dot(*A.polar(C, C, 72 * K * K, T + 180), 5, "active")),
    ("tangent", "Tangent", lambda: A.tangent_pair(C, C, 66) + _star_at(*_on_ring(66), 1.2)),
    ("interrupted", "Interrupted", lambda: A.interrupted_ring(C, C, 66, 3, 12, cls="body", w=A.W_MARK)
        + A.dot(*A.polar(C, C, 66, T + 150), 6, "active")),
    ("offset", "Offset", lambda: A.offset_arcs(56, 142, 100, 5, 0.12)),
    ("orbit", "Orbit", lambda: A.orbit(C, C, 66, (0, 96, 210), active=0)),
    # --- sighting
    ("sight", "Sight line", lambda: A.broken_ring(C, C, 40, cls="body", w=A.W_MARK)
        + A.sight_line(C, C, 0, 84, cls="active", w=A.W_MARK) + A.dot(C, C, 4, "ink")),
    ("fan", "Fan", lambda: A.radial_fan(54, 146, 36, 124, T - 55, T + 55, 9, "body", A.W_HAIR)
        + A.sight_line(54, 146, 36, 124, cls="active", w=A.W_MARK) + A.dot(54, 146, 4, "ink")),
    ("pointer", "Pointer", lambda: A.broken_ring(C, C, 66, cls="body", w=A.W_MARK) + A.pointer(C, C, 62, T, 46)),
    ("crosshair", "Crosshair", lambda: A.crosshair(C, C, 50, 16, "ink", A.W_MARK) + A.dot(C, C, 6, "active")),
    ("axis", "Axis cross", lambda: A.circle(C, C, 60, "faint", A.W_HAIR) + A.crosshair(C, C, 76, 0, "body", A.W_HAIR)
        + A.dot(*_on_ring(60), 6, "active")),
    ("pivot", "Pivot", lambda: A.pivot(C, C, 56, "ink") + A.dot(*A.polar(C, C, 56, T), 7, "active")),
    # --- counting
    ("tally-1", "One", lambda: _uprights(1)),
    ("tally-2", "Two", lambda: _uprights(2)),
    ("tally-3", "Three", lambda: _uprights(3)),
    ("tally-4", "Four", lambda: _uprights(4)),
    ("tally-5", "Five", lambda: _uprights(4, struck=True)),
    ("tally-6", "Six", lambda: A.line(60, 60, 60, 140, "ink", A.W_MARK * 1.4) * 0 + _uprights(4, struck=True).replace(
        'class="active"', 'class="ink"') + A.line(154, 58, 154, 142, "active", A.W_MARK * 1.4)),
    # --- fields
    ("cells-3", "Cells 3", lambda: _cells(3, (2, 0))),
    ("cells-4", "Cells 4", lambda: _cells(4, (1, 2))),
    ("cells-5", "Cells 5", lambda: _cells(5, (3, 1))),
    ("cells-ramp", "Ramp", lambda: _cells(6, (5, 0), "ramp")),
    ("histogram", "Distribution", _hist),
    ("axes", "Axes", lambda: A.axes(34, 160, 132, 110, 7, 5, "body") + A.dot(128, 76, 6, "active")),
    # --- scales
    ("ticks", "Ticks", _tick_with_index),
    ("edge", "Edge", _edge_with_index),
    ("radial", "Radial", lambda: A.radial_scale(56, 134, 112, T - 50, T + 50, 3.2, 5, True, "body", A.W_HAIR)
        + A.index_mark(56, 134, 112, T) + A.dot(56, 134, 3, "faint")),
    ("dimension", "Dimension", _dim),
    ("vernier", "Vernier", _vernier),
    ("radial-wide", "Sector", lambda: A.radial_scale(46, 80, 112, T + 30, T + 150, 5, 5, False, "body", A.W_HAIR)
        + A.ring_arc(46, 80, 112, T + 30, T + 150, "body", A.W_HAIR)
        + A.dot(*A.polar(46, 80, 112, T + 105), 6, "active")),
    # --- marks
    ("star", "Star", lambda: _star_at(78, 124, 2.3, "ink")
        + A.line(78, 124, *A.polar(78, 124, 30 * 2.3, T), "active", A.W_MARK)),
    ("seated", "Seated", lambda: A.broken_ring(C, C, 62, cls="ink") + _star_at(*_on_ring(62), 1.5)),
    ("frame", "Frame", lambda: A.orbit_frame(C, C, 66)),
    ("aperture", "Aperture", lambda: A.broken_ring(C, C, 60, cls="body", w=A.W_MARK)
        + A.aperture(C, C, 42, cls="ink") + A.dot(*_on_ring(60), 6, "active")),
    ("loader", "Calibration", lambda: A.calibration_loader(C, C, 56, 0.62)),
    ("bowl", "Bowl", lambda: A.circle(C, C, 64, "faint", A.W_HAIR) + A.bowl(C, C, 42, "ink")),
]

assert len(TILES) == 36, len(TILES)


def tile(i: int) -> str:
    """The inside of tile i (0-based) in a 200-unit square."""
    return TILES[i][2]()


def tile_svg(i: int, size: float = 200, frame: bool = True) -> str:
    fr = (f'<rect x="1" y="1" width="198" height="198" class="faint" stroke-width="1.2"/>') if frame else ""
    return (f'<svg class="geo" viewBox="0 0 200 200" width="{A.f(size)}" height="{A.f(size)}" fill="none" '
            f'aria-label="{TILES[i][1]}">{fr}{tile(i)}</svg>')


def build():
    out = os.path.join(HERE, "tiles")
    os.makedirs(out, exist_ok=True)
    sys.path.insert(0, os.path.join(os.path.dirname(HERE), "templates"))
    import kit as Kit
    for i, (name, _, _) in enumerate(TILES):
        # standalone SVGs paint with the light palette; the classes map to it
        def paint(m):
            col = A.STYLE_LIGHT[m.group(1)]
            return f'color="{col}"' if m.group(2) else f'stroke="{col}" color="{col}"'
        inner = re.sub(r'class="(ink|body|faint|active)( fill)?"', paint, tile(i))
        svg = ("<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"-8 -8 216 216\" width=\"216\" height=\"216\" fill=\"none\">"
               f"<rect x=\"-8\" y=\"-8\" width=\"216\" height=\"216\" fill=\"{A.STYLE_LIGHT['ground']}\"/>{inner}</svg>")
        open(os.path.join(out, f"tile-{i + 1:02d}-{name}.svg"), "w", encoding="utf-8").write(svg)

    def cell(i, ground):
        return f'<figure style="margin:0">{tile_svg(i, 180)}<figcaption class="label" style="margin-top:8px;font-size:12px;letter-spacing:.08em">{i + 1:02d} {TILES[i][1]}</figcaption></figure>'

    def panel(theme, title):
        grid = "".join(cell(i, theme) for i in range(36))
        return Kit.page(
            f'<div class="label">{title}</div>'
            f'<div class="tiles" style="display:grid;grid-template-columns:repeat(6,180px);gap:36px 40px;margin-top:40px;justify-content:center">{grid}</div>',
            theme=theme)

    html = Kit.page_doc([panel("light", "Tile set · paper"), panel("dark", "Tile set · navy"), panel("cobalt", "Tile set · cobalt")],
                        out, 1600, 1780, "social", ".describe( tile set")
    p = os.path.join(out, "tiles.html")
    open(p, "w", encoding="utf-8").write(html)
    return [p]


if __name__ == "__main__":
    print("\n".join(build()))
