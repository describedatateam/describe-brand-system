"""hero_field.py — the hero background: the Milky Way plate as a light
ordered dither. No cut, no figure: atmosphere only, kept faint enough for
text to sit on it. Output is one mask; the page colours it with --faint.

    python3 hero_field.py   → bitmaps/hero-sky/hero-sky_field.png (+ previews)
"""
import os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import bitmap as B
import export_bitmaps as E

U = '/mnt/user-data/uploads/arabia/'
W, H = 2400, 1200
sky = Image.open(U + '11241855653_071d71380a_o.jpg').crop((0, 100, 1425, 855)).convert('L')
s = max(W / sky.width, H / sky.height)
sky = sky.resize((int(sky.width * s) + 1, int(sky.height * s) + 1), Image.LANCZOS)
x0 = (sky.width - W) // 2
sky = sky.crop((x0, (sky.height - H) // 2, x0 + W, (sky.height - H) // 2 + H))
g = ndi.gaussian_filter(np.asarray(sky, np.float32) / 255, 1.5)
dark = 1 - g
lo, hi = np.quantile(dark, [.02, .98])
t = np.clip((dark - lo) / (hi - lo), 0, 1)
# the light version: a screen between 3% and 34% ink, never heavier
t = 0.03 + 0.31 * t
# stars stay as clean paper dots: the brightest points are forced to zero ink
stars = (g - ndi.grey_opening(g, size=(9, 9))) > 0.12
t[ndi.binary_dilation(stars, iterations=2)] = 0
field = B.ordered(t, gamma=1.1, scale=2)
d = 'bitmaps/hero-sky'
os.makedirs(d, exist_ok=True)
E.save_mask(field, f'{d}/hero-sky_field.png')
for pal, tag in [(E.LIGHT, 'paper'), (E.DARK, 'navy')]:
    E.flat({'field': field}, [('field', 'faint')], pal, f'{d}/hero-sky_preview-{tag}.png')
print(field.mean())
