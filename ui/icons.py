"""
icons.py — the .describe( icon set.

Icons are miniature instruments, not SaaS glyphs. Each one is built from the
same vocabulary as the mark — rings broken on the sight axis, rules, ticks,
pointers, dots — on a 24-unit grid with a single stroke weight.

    python3 icons.py        writes icons/*.svg and icons.json

The eight named in the identity brief (§16):

    search      ring broken on θ, sighting line out through the gap
    data        measured grid — ticks on two edges
    report      a field with a measuring edge down its side
    automation  a tally, then a directional rule
    decision    two paths converging on a marked point
    research    a body under observation, the sight line reaching a target
    dataset     nested cells
    error       an interrupted measurement rule, out of alignment

plus the interface essentials. θ is imported from the geometry library so the
icons rotate with the mark if the canon ever changes.
"""

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "geometry"))
try:
    from astrolabe import THETA, GAP   # the canon
except Exception:                     # standalone fallback — keep in sync
    THETA, GAP = -40.6, 28.0

SW = 1.5          # the one stroke weight
GRID = 24


def P(cx, cy, r, deg):
    a = math.radians(deg)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def line(x0, y0, x1, y1):
    return f'<path d="M{f(x0)} {f(y0)}L{f(x1)} {f(y1)}"/>'


def poly(*pts):
    d = "M" + "L".join(f"{f(x)} {f(y)}" for x, y in pts)
    return f'<path d="{d}"/>'


def arc(cx, cy, r, a0, a1):
    sw = (a1 - a0) % 360
    x0, y0 = P(cx, cy, r, a0)
    x1, y1 = P(cx, cy, r, a1)
    return (f'<path d="M{f(x0)} {f(y0)}A{f(r)} {f(r)} 0 {1 if sw > 180 else 0} 1 '
            f'{f(x1)} {f(y1)}"/>')


def broken_ring(cx, cy, r, gap=GAP, axis=THETA):
    return arc(cx, cy, r, axis + gap / 2, axis - gap / 2)


def dot(cx, cy, r=1.6):
    return (f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" '
            f'fill="currentColor" stroke="none"/>')


def rect(x, y, w, h):
    return f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}"/>'


# ---------------------------------------------------------------------------
# The eight instrument icons
# ---------------------------------------------------------------------------

def search():
    cx, cy, r = 10.5, 10.5, 6.5
    sx, sy = P(cx, cy, 2.4, THETA)
    ex, ey = P(cx, cy, 12.5, THETA)
    # centre is a dot, not a cross: at 20px a cross inside a ring reads as
    # "plus in a circle", i.e. ADD — the opposite of search.
    return (broken_ring(cx, cy, r) + dot(cx, cy, 1.4) + line(sx, sy, ex, ey))


def data():
    out = [rect(7, 4, 13, 13), line(7, 8.33, 20, 8.33), line(7, 12.67, 20, 12.67),
           line(11.33, 4, 11.33, 17), line(15.67, 4, 15.67, 17)]
    for y in (4, 8.33, 12.67, 17):                 # measuring edge, left
        out.append(line(3.5, y, 5, y))
    for x in (7, 11.33, 15.67, 20):                # and along the base
        out.append(line(x, 19, x, 20.5))
    return "".join(out)


def report():
    out = [rect(7, 3, 13, 18)]
    for i, y in enumerate((5, 8, 11, 14, 17, 20)):  # the measuring edge
        out.append(line(3 if i % 3 == 0 else 4.2, y, 5.2, y))
    out += [line(10, 8, 17, 8), line(10, 12, 17, 12), line(10, 16, 14.5, 16)]
    return "".join(out)


def automation():
    out = [line(x, 7, x, 17) for x in (3.5, 6.5, 9.5)]
    out += [line(12.5, 12, 20.5, 12), poly((17, 8.5), (20.5, 12), (17, 15.5))]
    return "".join(out)


def decision():
    return (line(3, 5, 16, 12) + line(3, 19, 16, 12) + line(16, 12, 19, 12) +
            dot(20, 12, 2.1))


def research():
    cx, cy, r = 9, 15, 5
    sx, sy = P(cx, cy, r, THETA)
    ex, ey = P(cx, cy, r + 10, THETA)
    return (f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}"/>' +
            line(sx, sy, ex, ey) + dot(ex, ey, 1.7))


def dataset():
    return (rect(4, 4, 16, 16) + line(12, 4, 12, 20) + line(4, 12, 20, 12) +
            line(16, 4, 16, 12) + line(12, 8, 20, 8))


def error():
    # A ruler, broken — and the right half no longer lines up with the left.
    # Ticks hang below the rule so it reads as a scale, not as brackets.
    out = [line(2.5, 9, 10, 9), line(14, 15, 21.5, 15)]
    out += [line(x, 9, x, 12.5 if i % 2 == 0 else 11)
            for i, x in enumerate((2.5, 6.25, 10))]
    out += [line(x, 15, x, 18.5 if i % 2 == 0 else 17)
            for i, x in enumerate((14, 17.75, 21.5))]
    return "".join(out)


# ---------------------------------------------------------------------------
# Interface essentials
# ---------------------------------------------------------------------------

def arrow():            # directional — mirrors in RTL
    return line(4, 12, 19.5, 12) + poly((14.5, 7), (19.5, 12), (14.5, 17))


def check():
    return poly((5, 12.5), (10, 17.5), (19.5, 6.5))


def close():
    return line(6, 6, 18, 18) + line(18, 6, 6, 18)


def chevron():          # down
    return poly((6.5, 9.5), (12, 15), (17.5, 9.5))


def plus():
    return line(12, 5, 12, 19) + line(5, 12, 19, 12)


def info():
    ix, iy = P(12, 12, 8.5, THETA + 180)
    return (broken_ring(12, 12, 8.5) + line(12, 11, 12, 16.5) + dot(12, 7.8, 1.2))


def warning():
    # a pointer arriving at a limit — you are near the edge of what's allowed
    return (line(18, 4.5, 18, 19.5) + line(3.5, 12, 14, 12) +
            poly((10.5, 8.5), (14, 12), (10.5, 15.5)))


def orbit():
    dx, dy = P(12, 12, 8.5, THETA + 180)
    return broken_ring(12, 12, 8.5) + dot(dx, dy, 2)


def menu():
    return line(4, 7, 20, 7) + line(4, 12, 20, 12) + line(4, 17, 14, 17)


ICONS = {
    # instruments
    "search": search, "data": data, "report": report, "automation": automation,
    "decision": decision, "research": research, "dataset": dataset,
    "error": error,
    # interface
    "arrow": arrow, "check": check, "close": close, "chevron": chevron,
    "plus": plus, "info": info, "warning": warning, "orbit": orbit,
    "menu": menu,
}

# Icons that describe a direction and must flip in right-to-left layouts.
DIRECTIONAL = {"arrow", "automation", "decision", "warning", "research",
               "search"}


def svg(body, size=24):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {GRID} {GRID}" '
            f'width="{size}" height="{size}" fill="none" stroke="currentColor" '
            f'stroke-width="{SW}" stroke-linecap="round" stroke-linejoin="round" '
            f'aria-hidden="true">{body}</svg>')


def main():
    out = os.path.join(HERE, "icons")
    os.makedirs(out, exist_ok=True)
    manifest = {}
    for name, fn in ICONS.items():
        body = fn()
        manifest[name] = {"body": body, "directional": name in DIRECTIONAL}
        with open(os.path.join(out, f"{name}.svg"), "w", encoding="utf-8") as fh:
            fh.write(svg(body))
    with open(os.path.join(HERE, "icons.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=1)
    print(f"{len(ICONS)} icons → icons/  ({len(DIRECTIONAL)} directional)")


if __name__ == "__main__":
    main()
