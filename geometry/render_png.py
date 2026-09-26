"""
render_png.py — raster the plate library.

Writes png/light/ and png/dark/ at 1200x1200 with a transparent background, so
every plate drops onto any surface without carrying a white box with it.

    python3 render_png.py            # both themes, 1200px
    python3 render_png.py 2048       # both themes, 2048px

Needs playwright + chromium. Everything else in the folder is dependency-free.
"""

import json
import os
import sys

from astrolabe import STYLE_DARK, STYLE_LIGHT

SIZE = int(sys.argv[1]) if len(sys.argv) > 1 else 1200
CHROME = os.environ.get(
    "CHROME_PATH", "/opt/pw-browsers/chromium-1194/chrome-linux/chrome")


def sheet(plates, style, size):
    """One page holding every plate, so we pay for browser start-up once."""
    vars_ = ";".join(f"--{k}:{v}" for k, v in style.items())
    cells = "".join(
        f'<div class="cell" id="c-{p["id"]}">'
        f'<svg class="dsc" viewBox="-20 -20 240 240">{p["body"]}</svg></div>'
        for p in plates)
    return f"""<!doctype html><meta charset="utf-8"><style>
:root{{{vars_}}}
html,body{{margin:0;background:transparent}}
.cell{{width:{size}px;height:{size}px;background:transparent}}
svg{{width:100%;height:100%;display:block;fill:none}}
.dsc .ink{{stroke:var(--ink);color:var(--ink)}}
.dsc .body{{stroke:var(--body);color:var(--body)}}
.dsc .faint{{stroke:var(--faint);color:var(--faint)}}
.dsc .active{{stroke:var(--active);color:var(--active)}}
.dsc .mark{{stroke:var(--mark);color:var(--mark)}}
.dsc .fill{{stroke:none}}
/* construction nodes read as holes, not as filled data points */
.dsc [fill="var(--ground)"]{{fill:{style['ground']}}}
text{{font-family:'IBM Plex Mono',ui-monospace,monospace}}
</style>{cells}"""


def main():
    from playwright.sync_api import sync_playwright

    plates = json.load(open("manifest.json", encoding="utf-8"))["plates"]
    jobs = [("light", STYLE_LIGHT), ("dark", STYLE_DARK)]

    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=CHROME)
        page = browser.new_page(viewport={"width": SIZE + 40, "height": 900},
                                device_scale_factor=1)
        for theme, style in jobs:
            outdir = os.path.join("png", theme)
            os.makedirs(outdir, exist_ok=True)
            page.set_content(sheet(plates, style, SIZE))
            page.wait_for_timeout(400)
            for p in plates:
                page.locator("#c-" + p["id"]).screenshot(
                    path=os.path.join(outdir, p["id"] + ".png"),
                    omit_background=True)
            print(f"{len(plates)} plates → {outdir}/ at {SIZE}px")
        browser.close()


if __name__ == "__main__":
    main()
