"""Render tokens/palette.png: every colour token on its own surface, for
people picking colours in Canva, Slides or Figma rather than in code.

  python3 tokens/render_palette.py      (needs Pillow; not part of CI)
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from colour import contrast  # noqa: E402

FONTS = HERE.parent / "decisions" / "fonts"
mono = ImageFont.truetype(str(FONTS / "IBMPlexMono-Regular.ttf"), 15)
label = ImageFont.truetype(str(FONTS / "IBMPlexMono-Medium.ttf"), 13)
flat = json.loads((HERE / "dist" / "tokens.json").read_text())["tokens"]

ROWS = [
    ("SURFACE · TEXT · ROLES", ["color.surface.ground", "color.surface.panel", "color.text.ink", "color.text.body",
                                "color.text.dim", "color.role.active", "color.role.mark", "color.role.neg", "color.role.pos"]),
    ("STORY · CONTEXT", ["color.viz.story", "color.viz.context"]),
    ("CATEGORICAL, IN ORDER", [f"color.viz.cat.{i}" for i in range(1, 7)]),
    ("SEQUENTIAL · BLUE", [f"color.viz.seq-step.{i}" for i in range(1, 8)]),
    ("SEQUENTIAL · BRASS", [f"color.viz.seq-alt-step.{i}" for i in range(1, 8)]),
    ("DIVERGING", [f"color.viz.div.n{i}" for i in range(5, 0, -1)] + ["color.viz.div.0"]
     + [f"color.viz.div.p{i}" for i in range(1, 6)]),
]
SW, GAP, PAD = 96, 8, 40
W = PAD * 2 + 11 * SW + 10 * GAP
H = PAD + len(ROWS) * (SW + 70)
img = Image.new("RGB", (W * 2, H), "white")
d = ImageDraw.Draw(img)
for col, mode in enumerate(("light", "dark")):
    x0 = col * W
    ground, ink = flat["color.surface.ground"][mode], flat["color.text.ink"][mode]
    dim = flat["color.text.dim"][mode]
    d.rectangle([x0, 0, x0 + W, H], fill=ground)
    y = PAD
    for title, keys in ROWS:
        d.text((x0 + PAD, y), f"{title} · {mode.upper()}", font=label, fill=dim)
        y += 22
        for i, k in enumerate(keys):
            h = flat[k][mode]
            x = x0 + PAD + i * (SW + GAP)
            d.rectangle([x, y, x + SW, y + SW], fill=h, outline=flat["color.line.rule"][mode])
            d.text((x, y + SW + 6), h, font=mono, fill=ink)
            d.text((x, y + SW + 24), f"{contrast(h, ground):.1f}:1", font=mono, fill=dim)
        y += SW + 48
img.save(HERE / "palette.png", optimize=True)
print("wrote tokens/palette.png")
