"""
occasions.py — the .describe( social templates for posts that are not about data.

    python3 social/templates/occasions.py            writes social/templates/out/occasions-4x5.html
    python3 social/templates/occasions.py --render   also one PNG per post

Greeting, first client, milestone, announcement, hiring, tagline.

The rule that carries over from the data posts: every post is a measured field
with ONE marked thing. Without data there is no outlier, so the marker is the
active colour, never coral (coral stays on the outlier ring; templates/check.py
enforces it). Every element comes from geometry/astrolabe.py or templates/kit.py,
every colour from the tokens, every face from decisions/fonts.

Copy here is placeholder. Replace it per post; keep the geometry's meaning.
"""

from __future__ import annotations

import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "templates"))
sys.path.insert(0, os.path.join(ROOT, "geometry"))

import astrolabe as A  # noqa: E402
import kit as K  # noqa: E402

OUT = os.path.join(HERE, "out")
W, H = 1080, 1350
PAD = 77                      # social pad: 2.75 x the 28px body size


def label(text: str) -> str:
    return f'<div class="top" style="display:flex;justify-content:space-between"><span class="label">{text}</span></div>'


def foot() -> str:
    return f'<div class="foot"><div class="src"></div>{K.lockup("compact")}</div>'


def edge(side: str = "left") -> str:
    slot = "edge-slot" if side == "left" else "edge-slot edge-slot--right"
    return f'<div class="{slot}">{K.measuring_edge(H - 2 * PAD, count=36, side=side)}</div>'


def scaled(svg_body: str, cx: float, cy: float, k: float) -> str:
    return f'<g transform="translate({A.f(cx)} {A.f(cy)}) scale({k}) translate({A.f(-cx)} {A.f(-cy)})">{svg_body}</g>'


# 1 · Greeting: a crescent cut from the ring, over a faint lattice ----------
def crescent(cx: float, cy: float, R: float, cls: str = "active") -> str:
    """The ring minus a second circle pushed along the sight axis. The opening
    faces θ, where the star sits: the mark's own grammar, not a stock symbol."""
    d, rho = 0.40 * R, 0.86 * R
    a = (d * d + R * R - rho * rho) / (2 * d)
    h = math.sqrt(R * R - a * a)
    span = 2 * math.degrees(math.atan2(h, a - d))            # angle of C2 inside C1
    large2 = 1 if (360 - span) > 180 else 0
    path = (f"M{A.f(a)} {A.f(h)} A{A.f(R)} {A.f(R)} 0 1 1 {A.f(a)} {A.f(-h)} "
            f"A{A.f(rho)} {A.f(rho)} 0 {large2} 0 {A.f(a)} {A.f(h)}Z")
    return (f'<g transform="translate({A.f(cx)} {A.f(cy)}) rotate({A.f(A.THETA)})">'
            f'<path d="{path}" class="{cls} fill" fill="currentColor"/></g>')


def lattice(w: float, h: float, a: float = 96, hair: float = 1.5) -> str:
    """An eight-point lattice as notation: each cell is a square and the same
    square turned 45 degrees (the star's own eight arms), tiled so the points
    touch. faint only; fade it out under the type."""
    p = a * math.sqrt(2)
    out = []
    rows = int(h / (p / 2)) + 3
    cols = int(w / p) + 3
    for j in range(-1, rows):
        for i in range(-1, cols):
            cx = i * p + (p / 2 if j % 2 else 0)
            cy = j * p / 2
            hh = a / 2
            r = a / math.sqrt(2)
            sq = [(cx - hh, cy - hh), (cx + hh, cy - hh), (cx + hh, cy + hh), (cx - hh, cy + hh)]
            dm = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
            for poly in (sq, dm):
                pts = " ".join(f"{A.f(x)},{A.f(y)}" for x, y in poly)
                out.append(f'<polygon points="{pts}" class="faint" stroke-width="{hair}"/>')
    return K.svg(w, h, "".join(out))


def greeting(W, H):
    cx, cy, R = 540, 700, 250
    sx, sy = A.polar(cx, cy, R * 0.62, A.THETA)
    art = A.circle(cx, cy, R * 1.28, "faint", 1.5, **{"stroke-dasharray": "3 9"})
    art += crescent(cx, cy, R, "ink") + scaled(A.star(sx, sy, cls="active"), sx, sy, 2.6)
    art = K.svg(W, H, art)
    return K.page(
        lattice(W, H).replace('class="geo layer"', 'class="geo layer fade-up"', 1) + art
        + label("تهنئة")
        + '<div style="margin-top:40px;text-align:right;direction:rtl">'
          '<div style="font-family:var(--font-ar-display);font-size:176px;line-height:1.05;color:var(--ink)">عيد مبارك</div>'
          '<div class="lede" style="font-family:var(--font-ar-sans);margin-top:16px">كل عام وأنتم بخير</div></div>'
        + foot(),
        theme="brass").replace('<section ', '<section dir="rtl" lang="ar" ', 1)


# 2 · First client: an empty field, one cell taken ---------------------------
def first_client(W, H):
    cols, rows, pitch, cell = 12, 6, 78, 60
    x0, y0 = 77, 640
    cells = []
    for r in range(rows):
        for c in range(cols):
            on = (c, r) == (7, 2)
            cells.append(f'<rect x="{x0 + c * pitch}" y="{y0 + r * pitch}" width="{cell}" height="{cell}" '
                         f'class="{"active" if on else "faint"} fill" fill="currentColor"/>')
    tx, ty = x0 + 7 * pitch + cell / 2, y0 + 2 * pitch
    cells.append(A.line(tx, ty - 14, tx, ty - 80, "active", 3))
    cells.append(A.text(tx + 14, ty - 74, "1", "active", 30, "start"))
    return K.page(
        K.svg(W, H, "".join(cells)) + edge()
        + label("Announcement · template")
        + '<div class="opener" style="margin-top:64px">Our first<br><span class="em">client.</span></div>'
        + foot())


# 3 · Milestone: five is one complete tally group ----------------------------
def milestone(W, H):
    art = K.svg(W, H, A.tally(5, x0=170, y0=520, height=330, pitch=86, group_gap=0, cls="ink", w=16))
    return K.page(
        art + edge()
        + label("Milestone · template")
        + '<div class="opener" style="margin-top:64px">Five months<br><span class="em">in.</span></div>'
        + '<div class="lede" style="position:absolute;left:77px;right:77px;bottom:190px">One full group. Counted, not rounded.</div>'
        + foot())


# 4 · Announcement: the crosshair settles on the thing -----------------------
def announcement(W, H):
    cx, cy = 700, 760
    art = K.construction(W, H, cx, cy, 420) + K.svg(W, H, A.crosshair(cx, cy, 78, 24, "active", 4) + A.dot(cx, cy, 9, "active"))
    return K.page(
        art + label("Announcement · template")
        + '<div class="opener" style="margin-top:64px">Discovery calls<br><span class="em">are open.</span></div>'
        + '<div class="h3" style="margin-top:auto;margin-bottom:40px">describe.team</div>'
        + foot(), theme="dark")


# 5 · Hiring: the aperture is the open seat ----------------------------------
def hiring(W, H):
    cx, cy, R = 540, 840, 280
    art = scaled(A.orbit(cx, cy, 62, markers=(0, 120, 240), active=0), cx, cy, R / 62)
    return K.page(
        K.svg(W, H, art) + edge()
        + label("Hiring · template")
        + '<div class="opener" style="margin-top:64px">We&#8217;re hiring.<br><span class="em">[ role ]</span></div>'
        + foot())


# 6 · Tagline: a rule from data to decision, one index mark at the end --------------------
def tagline(W, H):
    """From data to decision: a measured rule with its two ends named and one
    index mark at the far end (the decision), over the faint dither glow."""
    x0, x1, y, n = 77, 1003, 930, 61
    art = [A.line(x0, y, x1, y, "body", 2)]
    for i in range(n):
        x = x0 + (x1 - x0) * i / (n - 1)
        L = 40 if i % 10 == 0 else 16
        art.append(A.line(x, y, x, y - L, "body" if i < n - 1 else "active", 2))
    art.append(A.line(x1, y + 6, x1, y - 84, "active", 5))
    art.append(A.dot(x1, y - 84, 11, "active"))
    art.append(A.text(x0, y + 62, "data", "body", 26, "start"))
    art.append(A.text(x1, y + 62, "decision", "active", 26, "end"))
    return K.page(
        K.dither_layer(W, H, kind="glow", cx=0.72, cy=0.70, hi=0.30)
        + K.svg(W, H, "".join(art))
        + label("Tagline")
        + '<div class="opener" style="margin-top:64px">From data<br><span class="em">to decision.</span></div>'
        + foot(), theme="dark")


POSTS = [greeting, first_client, milestone, announcement, hiring, tagline]


def build() -> list[str]:
    os.makedirs(OUT, exist_ok=True)
    pages = [f(W, H) for f in POSTS]
    html = K.page_doc(pages, OUT, W, H, "social", ".describe( social · occasions")
    p = os.path.join(OUT, "occasions-4x5.html")
    open(p, "w", encoding="utf-8").write(html)
    return [p]


if __name__ == "__main__":
    ps = build()
    print("\n".join(ps))
    if "--render" in sys.argv:
        sys.path.insert(0, os.path.join(ROOT, "templates"))
        from render import render
        for p in ps:
            for f in render(p, os.path.join(OUT, "png"), None, prefix="occasion-"):
                print(f)
