#!/usr/bin/env python3
"""Build the images the Brief uses. PNG, because Gmail does not render SVG.

    python3 email/build_assets.py                       defaults (5 weeks, Friday 27 November)
    python3 email/build_assets.py --num 4 --unit "weeks to" --event "White Friday" --date "Friday 27 November"

Writes, next to this file:
    brief-hero.png    1200 x 520 (shown at 600 x 260): the countdown figure, a tally
                      of five, and the ring with the star seated on it
    brief-rule.png    1200 x 24  (shown at 600 x 12): the ticked rule under the masthead

Colours come from tokens/tokens.json, the ring and star from geometry/astrolabe.py,
faces from decisions/fonts. Needs Playwright and Chromium.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "geometry"))
import astrolabe as A  # noqa: E402

T = json.load(open(os.path.join(ROOT, "tokens", "tokens.json"), encoding="utf-8"))


def tok(path: str, mode: str | None = None) -> str:
    node = T["color"]
    for p in path.split("."):
        node = node[p]
    if mode:
        return node["$extensions"]["mode"][mode]
    return node["$value"]


NAVY = tok("brand.navy")
INK = tok("brand.navy")
ACTIVE_DARK = tok("role.active", "dark")
TEXT_DARK = tok("text.ink", "dark")
DIM_DARK = tok("text.dim", "dark")
RING = tok("line.faint", "dark")
RULE_DARK = tok("line.rule", "dark")
BLUE = tok("brand.blue")


def fonts() -> str:
    d = os.path.join(ROOT, "decisions", "fonts")
    fr = os.path.join(d, "Fraunces%5BSOFT,WONK,opsz,wght%5D.ttf").replace("%", "%25")
    mono = os.path.join(d, "IBMPlexMono-Regular.ttf")
    return (f"@font-face{{font-family:Fraunces;src:url('file://{fr}');font-weight:100 900}}"
            f"@font-face{{font-family:'IBM Plex Mono';src:url('file://{mono}');font-weight:400}}")


def hero_html(num: str, unit: str, event: str, date: str) -> str:
    W, H = 600, 260
    cx, cy, R = 408, 178, 190
    rings = A.nested_rings(cx, cy, R, n=3, cls="ring", w=2)
    sx, sy = A.polar(cx, cy, R, A.THETA)
    star = f'<g transform="translate({A.f(sx)} {A.f(sy)}) scale(1.25) translate({A.f(-sx)} {A.f(-sy)})">{A.star(sx, sy, cls="star")}</g>'
    # five weeks: four struck strokes and the diagonal, the last one in active
    x0, y0, h, pitch = 440, 34, 62, 17
    t = "".join(f'<line x1="{x0 + i * pitch}" y1="{y0}" x2="{x0 + i * pitch}" y2="{y0 + h}" class="week"/>' for i in range(4))
    t += f'<line x1="{x0 - 8}" y1="{y0 + h - 8}" x2="{x0 + 3 * pitch + 8}" y2="{y0 + 8}" class="wf"/>'
    return f"""<!doctype html><meta charset="utf-8"><style>{fonts()}
html,body{{margin:0;background:{NAVY}}}
.hero{{position:relative;width:{W}px;height:{H}px;overflow:hidden;background:{NAVY}}}
svg{{position:absolute;inset:0}}
.ring{{stroke:{RING};fill:none}} .star{{stroke:{ACTIVE_DARK};fill:{ACTIVE_DARK}}}
.week{{stroke:{DIM_DARK};stroke-width:4;stroke-linecap:round}} .wf{{stroke:{ACTIVE_DARK};stroke-width:4;stroke-linecap:round}}
.num{{position:absolute;left:34px;top:-6px;font:300 238px/1 Fraunces;color:{TEXT_DARK};font-variation-settings:'SOFT' 0,'WONK' 0,'opsz' 144;letter-spacing:-0.04em}}
.unit{{position:absolute;left:176px;top:96px;font:italic 400 30px/1.1 Fraunces;color:{ACTIVE_DARK}}}
.event{{position:absolute;left:176px;top:128px;font:400 44px/1.05 Fraunces;color:{TEXT_DARK};font-variation-settings:'SOFT' 0,'WONK' 0,'opsz' 72}}
.date{{position:absolute;left:36px;bottom:26px;font:400 12px/1 'IBM Plex Mono';letter-spacing:.16em;text-transform:uppercase;color:{DIM_DARK}}}
</style><div class="hero"><svg width="{W}" height="{H}" viewBox="0 0 {W} {H}">{rings}{t}{star}</svg>
<div class="num">{num}</div><div class="unit">{unit}</div><div class="event">{event}</div><div class="date">{date}</div></div>"""


def build(args) -> list[str]:
    from playwright.sync_api import sync_playwright
    out = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 600, "height": 260}, device_scale_factor=2)
        pg.set_content(hero_html(args.num, args.unit, args.event, args.date))
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(500)
        path = os.path.join(HERE, "brief-hero.png")
        pg.locator(".hero").screenshot(path=path)
        out.append(path)
        # the ticked rule: minor and major ticks from a baseline, one active index tick
        W, H, n = 600, 12, 121
        ticks = []
        for i in range(n):
            x = 1 + (W - 2) * i / (n - 1)
            L = 11 if i % 10 == 0 else (6 if i % 5 == 0 else 3)
            col = BLUE if i == 100 else INK
            Lh = 12 if i == 100 else L
            ticks.append(f'<line x1="{x:.2f}" y1="{H}" x2="{x:.2f}" y2="{H - Lh}" stroke="{col}" stroke-width="{1.6 if i == 100 else 1}"/>')
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
               f'<line x1="0" y1="{H - 0.5}" x2="{W}" y2="{H - 0.5}" stroke="{INK}" stroke-width="1"/>{"".join(ticks)}</svg>')
        pg2 = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=2)
        pg2.set_content(f"<style>html,body{{margin:0;background:#fff}}</style>{svg}")
        path = os.path.join(HERE, "brief-rule.png")
        pg2.screenshot(path=path, clip={"x": 0, "y": 0, "width": W, "height": H})
        out.append(path)
        b.close()
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--num", default="5")
    ap.add_argument("--unit", default="weeks to")
    ap.add_argument("--event", default="White Friday")
    ap.add_argument("--date", default="Friday 27 November")
    for f in build(ap.parse_args()):
        print(f)
