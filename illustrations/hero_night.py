"""hero_night.py — the founder's night-sky treatment of the hero, rebuilt clean.

Her reference (a blue, diagonal line-screen version of the Milky Way plate) was a
1600px JPEG: its screen is blurred by compression, so it can't be upscaled into
a crisp 1-bit image. This rebuilds the same look from the original scan at the
exact output size, so every pixel is either lit or not:

  - dark sky, light stars and Milky Way (the plate as printed, not inverted);
  - a 45° line screen whose line width follows the tone, like her version;
  - stars, and the dotted constellation boundaries, forced fully lit so they
    stay sharp instead of breaking up in the screen.

Output is one mask (lit pixels). The page paints it with a light token on a navy
panel, so there are no baked-in colours. Shown at natural size, never scaled.

    python3 hero_night.py   → bitmaps/hero-night/hero-night_lit.png (+ previews)
"""
import os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import export_bitmaps as E

import sys
U = '/mnt/user-data/uploads/arabia/'
K = int(sys.argv[1]) if len(sys.argv) > 1 else 1   # 1 = 1x screens, 2 = retina (swap by resolution media query)
W, H = 2400 * K, 1200 * K
PERIOD = 4 * K                  # line-screen pitch: 4 CSS px at either density

sky = Image.open(U + '11241855653_071d71380a_o.jpg').crop((0, 100, 1425, 855)).convert('L')
s = max(W / sky.width, H / sky.height)
sky = sky.resize((int(sky.width * s) + 1, int(sky.height * s) + 1), Image.LANCZOS)
x0 = (sky.width - W) // 2
sky = sky.crop((x0, (sky.height - H) // 2, x0 + W, (sky.height - H) // 2 + H))
g0 = np.asarray(sky, np.float32) / 255
g = ndi.gaussian_filter(g0, 1.6 * K)

# tone: the brightness of the plate, stretched; the sky keeps a faint screen
lo, hi = np.quantile(g, [.03, .995])
t = np.clip((g - lo) / (hi - lo), 0, 1) ** 1.7
t = 0.04 + 0.93 * t          # the empty sky keeps a faint broken line, as in her version

# the 45° line screen: lit where tone beats a diagonal ramp
yy, xx = np.mgrid[0:H, 0:W]
# 4 positions across the line x 4 along it = 16 tone levels, so the edges of the
# Milky Way grade smoothly instead of banding, while the screen still reads as lines
along = np.array([0, 2, 1, 3])[((xx - yy) // K) % 4] / 4
ramp = (((xx + yy) % PERIOD) + along + 0.125) / PERIOD
lit = t > ramp

# stars: bright points above their neighbourhood, redrawn solid
star = (g - ndi.grey_opening(g, size=(11 * K, 11 * K))) > 0.13
star = ndi.binary_opening(star, iterations=1)
lit |= ndi.binary_dilation(star, iterations=K)
# dotted boundaries and constellation lines: thin bright strokes
thin = (ndi.gaussian_filter(g0, 0.8 * K) - ndi.grey_opening(ndi.gaussian_filter(g0, 0.8 * K), size=(5 * K, 5 * K))) > 0.16
thin = ndi.binary_opening(thin, structure=np.ones((1, 1)))
lit |= thin

d = 'bitmaps/hero-night'
os.makedirs(d, exist_ok=True)
sfx = '' if K == 1 else f'@{K}x'
E.save_mask(lit, f'{d}/hero-night_lit{sfx}.png')
NAVY, LIGHT = (9, 32, 82), (246, 248, 252)
for tag, bg, fg in [('navy', NAVY, LIGHT), ('blue', (15, 88, 229), LIGHT)]:
    out = np.zeros((H, W, 3), np.uint8)
    out[:] = bg
    out[lit] = fg
    Image.fromarray(out).save(f'{d}/hero-night_preview-{tag}{sfx}.png', optimize=True)
print('lit share', round(lit.mean(), 3))
