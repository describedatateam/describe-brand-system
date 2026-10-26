"""
render.py — HTML page sets to PNG (one per page) and PDF, with headless Chromium.

    python3 templates/render.py slides/out/deck.html --pdf

Needs Playwright for Python and a Chromium. If Playwright's own browser is not
installed, set CHROMIUM to an executable (e.g. CHROMIUM=/opt/pw-browsers/chromium).
"""

from __future__ import annotations

import os
import sys


def render(html: str, png_dir: str | None = None, pdf: str | None = None, prefix: str = "",
           viewport: tuple[int, int] = (2200, 2200)) -> list[str]:
    from playwright.sync_api import sync_playwright

    html = os.path.abspath(html)
    png_dir = png_dir or os.path.dirname(html)
    os.makedirs(png_dir, exist_ok=True)
    out = []
    with sync_playwright() as p:
        exe = os.environ.get("CHROMIUM")
        b = p.chromium.launch(executable_path=exe) if exe else p.chromium.launch()
        pg = b.new_page(viewport={"width": viewport[0], "height": viewport[1]}, device_scale_factor=1)
        pg.goto("file://" + html)
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(400)
        missing = pg.evaluate("""() => ['Fraunces','Readex Pro','IBM Plex Mono']
            .filter(f => ![...document.fonts].some(x => x.family.replace(/"/g,'') === f && x.status === 'loaded'))""")
        if missing:
            print("warning: fonts not loaded:", ", ".join(missing), file=sys.stderr)
        pages = pg.locator("section.pg")
        for i in range(pages.count()):
            path = os.path.join(png_dir, f"{prefix}{i + 1:02d}.png")
            pages.nth(i).screenshot(path=path)
            out.append(path)
        if pdf:
            w, h = pg.evaluate("""() => { const s = getComputedStyle(document.documentElement);
                return [s.getPropertyValue('--page-w').trim(), s.getPropertyValue('--page-h').trim()] }""")
            pg.emulate_media(media="print")
            pg.pdf(path=pdf, width=w, height=h, print_background=True)
            out.append(pdf)
        b.close()
    return out


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    src = args[0]
    pdf = os.path.splitext(src)[0] + ".pdf" if "--pdf" in sys.argv else None
    for p in render(src, pdf=pdf):
        print(p)
