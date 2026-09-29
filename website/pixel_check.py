"""
pixel_check.py — the hero night plate must be pixel-perfect.

    python3 /home/claude/website/pixel_check.py      (run shoot.py first: it writes _preview.html)

Exact cases (must pass), in light and dark:
    1280 px at 1x and 2x; 390 px at 1x, 2x and 3x; 375 px at 3x; 2560 and 3840 px at 1x (window 1020 px max)
  - on desktop the window's right edge must meet the band's right edge (no navy gap on wide screens);
  - the sky window's edges must land on whole CSS pixels;
  - a screenshot of exactly the window must contain only TWO colours: lit
    (#F6F8FC) and the navy behind it (#092052). Any third colour is a grey or
    blurred edge pixel, i.e. the mask was scaled or offset by a fraction.
Reported, not required — best-effort BY DESIGN, never treat these "(info)" lines as failures:
412 px at 2.625x and 1280 px at 3x. No bitmap can be exact at a
fractional density or on a 3x desktop (which falls back to the 2x file); with
image-rendering: pixelated they should still show only two colours.
Saves a zoomed crop of each case to shots/pixel-<w>-<dsf>x.png (light only).
Exit status 1 on any failure.
"""
import asyncio
import io
import sys

from PIL import Image
from playwright.async_api import async_playwright

LIT, NAVY = (0xF6, 0xF8, 0xFC), (0x09, 0x20, 0x52)
OUT = '/home/claude/website/shots/'


async def main():
    bad = 0
    async with async_playwright() as p:
        b = await p.chromium.launch()
        cases = [(1280, 900, 1, True), (1280, 900, 2, True), (390, 844, 1, True), (390, 844, 2, True),
                 (390, 844, 3, True), (375, 812, 3, True), (2560, 1200, 1, True), (3840, 1600, 1, True),
                 (412, 915, 2.625, False), (1280, 900, 3, False)]
        for w, h, dsf, exact in cases:
                for theme in ('light', 'dark'):
                    pg = await b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=dsf)
                    await pg.goto('file:///home/claude/website/_preview.html')
                    await pg.evaluate(f"document.documentElement.setAttribute('data-theme','{theme}')")
                    await pg.wait_for_timeout(600)
                    r = await pg.evaluate("(() => { const r = document.querySelector('.hero__sky').getBoundingClientRect();"
                                          " const band = document.querySelector('.hero__sky').parentElement.getBoundingClientRect();"
                                          " return {x:r.left, y:r.top, w:r.width, h:r.height, gap: band.right - r.right}; })()")
                    gap = r.pop('gap')
                    whole = all(abs(v - round(v)) < 1e-6 for v in r.values())
                    if w >= 1000 and abs(gap) > 0.01:
                        print(f'{w:>5}px @{dsf:g}x {theme:<5} window stops {gap:g}px short of the band edge: FAIL')
                        bad += 1
                    png = await pg.screenshot(clip={'x': r['x'], 'y': r['y'], 'width': r['w'], 'height': r['h']})
                    im = Image.open(io.BytesIO(png)).convert('RGB')
                    cset = {c for _, c in im.getcolors(maxcolors=1 << 24)}
                    ok = whole and cset == {LIT, NAVY}
                    if exact:
                        bad += not ok
                    print(f'{w:>5}px @{dsf:g}x {theme:<5} window x={r["x"]:g} y={r["y"]:g} {r["w"]:g}×{r["h"]:g} '
                          f'(whole px: {whole}) → {len(cset)} colours '
                          f'{("OK" if ok else "FAIL " + str(sorted(cset)[:4])) if exact else ("binary, not exact (info)" if ok else "NOT binary (info)")}')
                    if theme == 'light' and exact and w < 2560:
                        k = int(dsf)
                        c = im.crop((0, 0, min(im.width, 120 * k), min(im.height, 90 * k)))
                        c.resize((c.width * 8 // k, c.height * 8 // k), Image.NEAREST).save(f'{OUT}pixel-{w}-{k}x.png')
                    await pg.close()
        await b.close()
    print('pixel_check:', 'PASS' if not bad else f'FAIL ({bad})')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    asyncio.run(main())
