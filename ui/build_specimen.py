"""
build_specimen.py — assemble the single-file component library.

    python3 icons.py && python3 build_specimen.py

Inlines ../type/typography.css and ui.css (so the published page is
self-contained), builds an SVG sprite from icons.json, and draws the loaders
and the empty-state figure from the same θ as the mark.
"""

import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "geometry"))
try:
    from astrolabe import THETA, GAP
except Exception:
    THETA, GAP = -40.6, 28.0


def P(cx, cy, r, d):
    a = math.radians(d)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def arc(cx, cy, r, a0, a1):
    sw = (a1 - a0) % 360
    x0, y0 = P(cx, cy, r, a0)
    x1, y1 = P(cx, cy, r, a1)
    return (f"M{f(x0)} {f(y0)}A{f(r)} {f(r)} 0 {1 if sw > 180 else 0} 1 "
            f"{f(x1)} {f(y1)}")


def read(p):
    with open(os.path.join(HERE, p), encoding="utf-8") as fh:
        return fh.read()


# ---------------------------------------------------------------- CSS ----
type_css = read("../type/typography.css")
ui_css = re.sub(r"@import url\('\.\./type/typography\.css'\);\s*", "", read("ui.css"))

# ---------------------------------------------------------------- icons --
icons = json.loads(read("icons.json"))
sprite = ('<svg aria-hidden="true" style="position:absolute;width:0;height:0;overflow:hidden">'
          "<defs>" +
          "".join(f'<symbol id="i-{k}" viewBox="0 0 24 24">{v["body"]}</symbol>'
                  for k, v in icons.items()) +
          "</defs></svg>")

INSTRUMENTS = ["search", "data", "report", "automation", "decision",
               "research", "dataset", "error"]
grid = []
for k, v in icons.items():
    d = " d-icon--dir" if v["directional"] else ""
    cls = ' class="inst"' if k in INSTRUMENTS else ""
    grid.append(f'<figure{cls}><svg class="d-icon d-icon--lg{d}"><use href="#i-{k}"/></svg>'
                f'<figcaption>{k}{" ⇄" if v["directional"] else ""}</figcaption></figure>')

# ---------------------------------------------------------------- loaders
C = 28
ix0, iy0 = P(C, C, 22.5, THETA)
ix1, iy1 = P(C, C, 27.5, THETA)
cal = (f'<svg viewBox="0 0 56 56" aria-hidden="true">'
       f'<circle class="faint" cx="{C}" cy="{C}" r="19" stroke-width="1" stroke-dasharray="1.5 3"/>'
       f'<path class="idx active" d="M{f(ix0)} {f(iy0)}L{f(ix1)} {f(iy1)}" stroke-width="2"/>'
       f'<g class="ring"><path class="active" d="{arc(C, C, 19, THETA + GAP/2, THETA - GAP/2)}" '
       f'stroke-width="2.4"/></g></svg>')

ticks = []
for i in range(13):
    x = 4 + i * 4
    h = 8 if i % 3 == 0 else 4
    delay = (x - 4) / 48 * 1.44
    ticks.append(f'<path class="tk faint" d="M{x} 40V{40 - h}" stroke-width="1.2" '
                 f'style="animation-delay:{delay:.2f}s"/>')
sweep = ('<svg viewBox="0 0 56 56" aria-hidden="true">'
         '<path class="faint" d="M4 40H52" stroke-width="1"/>' + "".join(ticks) +
         '<g class="cursor"><path class="active" d="M4 14V46" stroke-width="2"/></g></svg>')

tally = ('<svg viewBox="0 0 56 56" aria-hidden="true">' +
         "".join(f'<path class="t t{i+1} active" d="M{x} 16V40" stroke-width="2.2"/>'
                 for i, x in enumerate((15, 21, 27, 33))) +
         '<path class="t t5 active" d="M10 37L38 19" stroke-width="2.2"/></svg>')

tx, ty = 34, 22
lock = ('<svg viewBox="0 0 56 56" aria-hidden="true">'
        '<path class="faint" d="M6 48H52M8 6V50" stroke-width="1"/>' +
        "".join(f'<circle cx="{x}" cy="{y}" r="1.8" fill="var(--faint)" stroke="none"/>'
                for x, y in ((16, 36), (24, 42), (44, 38), (20, 27), (46, 14))) +
        f'<g class="xh active">'
        f'<path d="M{tx-11} {ty}H{tx-4}M{tx+4} {ty}H{tx+11}M{tx} {ty-11}V{ty-4}M{tx} {ty+4}V{ty+11}" '
        f'stroke-width="1.8"/></g>'
        f'<circle class="pt active fillc" cx="{tx}" cy="{ty}" r="2.6"/></svg>')

cells = []
for j in range(5):
    for i in range(5):
        cells.append(f'<rect x="{2 + i*11}" y="{2 + j*11}" width="8" height="8" '
                     f'style="animation-delay:{(i + j) * 0.11:.2f}s"/>')
field = '<svg viewBox="0 0 56 56" aria-hidden="true">' + "".join(cells) + "</svg>"

LOADERS = [
    ("d-load-cal",   cal,   "Calibrating",       "معايرة"),
    ("d-load-sweep", sweep, "Measuring",         "قياس"),
    ("d-load-tally", tally, "Counting records",  "عدّ السجلات"),
    ("d-load-lock",  lock,  "Locating",          "تحديد الموقع"),
    ("d-load-field", field, "Resolving",         "استخلاص"),
]
loaders_html = "".join(
    f'<div class="d-loader {cls}" role="status">{svg}'
    f'<span class="d-loader__label" data-ar="{ar}">{en}</span></div>'
    for cls, svg, en, ar in LOADERS)

# ------------------------------------------------------- empty figure ----
E = 44
gr = []
for k in range(-10, 11):
    a = THETA + 180 + k * 5
    h = 5 if k % 5 == 0 else 2.5
    x0, y0 = P(E, E, 32, a)
    x1, y1 = P(E, E, 32 - h, a)
    gr.append(f"M{f(x0)} {f(y0)}L{f(x1)} {f(y1)}")
empty_fig = (f'<svg viewBox="0 0 88 88" aria-hidden="true">'
             f'<circle cx="{E}" cy="{E}" r="32" stroke="var(--faint)" stroke-width="1" '
             f'stroke-dasharray="3 4"/>'
             f'<path d="M6 {E}H82M{E} 6V82" stroke="var(--faint)" stroke-width="1" '
             f'stroke-dasharray="8 3 1.5 3"/>'
             f'<path d="{"".join(gr)}" stroke="var(--body)" stroke-width="1"/>'
             f'<circle cx="{E}" cy="{E}" r="3.4" stroke="var(--body)" stroke-width="1.2" '
             f'fill="var(--panel)"/></svg>')

# ---------------------------------------------------------------- write --
page = read("template.html")
for token, value in [("/*CSS*/", type_css + "\n" + ui_css),
                     ("<!--SPRITE-->", sprite),
                     ("<!--LOADERS-->", loaders_html),
                     ("<!--EMPTYFIG-->", empty_fig),
                     ("<!--ICONGRID-->", "".join(grid))]:
    assert page.count(token) == 1, token
    page = page.replace(token, value)

with open(os.path.join(HERE, "specimen.html"), "w", encoding="utf-8") as fh:
    fh.write(page)
print(f"specimen.html — {len(page)/1024:.0f} KB · {len(icons)} icons · "
      f"{len(LOADERS)} loaders")
