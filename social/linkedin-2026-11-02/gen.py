# Images for the LinkedIn posts of 3-5 Nov 2026. Follows social/atmosphere/ATMOSPHERE.md:
# one subject rebuilt from one unit on a grid, highlight = the image's own units recoloured,
# no star, no glow/grain, no pattern. Photo source: studies-2026-10-29/src/earth_hd.png.
import numpy as np, os
from PIL import Image, ImageDraw, ImageFont
from atmos import *
B = '/home/claude/describe-brand-system'; F = B + '/decisions/fonts/'
NAVY, BLUE, LBLUE, BRASS = '#092052', '#0F58E5', '#4F86F7', '#D9AE62'

def bars_tone(W, H, vals, x0, x1, base, top, gapf=0.28):
    t = np.zeros((H, W)); n = len(vals); step = (x1 - x0) / n; boxes = []
    for k, v in enumerate(vals):
        a = int(x0 + k * step + step * gapf / 2); b = int(x0 + (k + 1) * step - step * gapf / 2)
        h = int((base - top) * v); t[base - h:base, a:b] = 1.0; boxes.append((a, base - h, b, base))
    return t, boxes

def mask_box(shape, box):
    m = np.zeros(shape, bool); a, b, c, d = box; m[b:d, a:c] = True; return m

def label(im, xy, text, color, size=15, anchor='la', font='IBMPlexMono-Medium.ttf'):
    S = 2; W, H = im.size; big = im.resize((W * S, H * S), Image.LANCZOS); d = ImageDraw.Draw(big)
    f = ImageFont.truetype(F + font, size * S)
    d.text((xy[0] * S, xy[1] * S), text, font=f, fill=hexrgb(color), anchor=anchor)
    return big.resize((W, H), Image.LANCZOS)

# P1: 13 months of the public UCI Online Retail data, shape only (relative monthly revenue)
def p1():
    W, H = 1080, 760
    import json
    net = [m['net'] for m in json.load(open(B + '/site/proof/figures.json'))['monthly']]
    rel = [v / max(net) for v in net]
    t, bx = bars_tone(W, H, rel, 90, 990, 660, 60)
    a, b, c, d = bx[12]; t[b:d, a:c] = 0.25  # Dec 2011 is a partial month (to 9 Dec): outline only
    acc = mask_box(t.shape, bx[11])
    im = pixels(t, PALETTES['light'], cell=12, gap=2, accent=acc)
    for k, m in enumerate(['D', 'J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D']):
        a, _, b, _ = bx[k]
        im = label(im, ((a + b) / 2, 690), m + ('*' if k == 12 else ''), NAVY if k == 11 else '#64748B', 18, 'ma')
    im = label(im, (90, 728), '2010', '#64748B', 14); im = label(im, (bx[1][0], 728), '2011', '#64748B', 14)
    im = frame(im, (bx[11][0] - 10, bx[11][1] - 10, bx[11][2] + 10, bx[11][3] + 4), None, color=NAVY, ground='#F6F8FC')
    im.save('p1_img.png')

# C1: two numbers about the same thing, each bar built from digits
def c1():
    W, H = 1080, 760
    t, bx = bars_tone(W, H, [1.0, 88 / 130], 170, 910, 640, 90, gapf=0.42)
    im = ascii(t * 0.95, PALETTES['navy'], seed=7)
    for (a, top, b, _), big, sub in zip(bx, ['+130%', '+88%'], ['FORECAST · WHOLE SEASON', 'MEASURED · SO FAR THIS YEAR']):
        im = label(im, ((a + b) / 2, top - 70), big, '#E6EFFF', 44, 'ma')
        im = label(im, ((a + b) / 2, 672), sub, '#8A99B0', 16, 'ma')
    im.save('c1_img.png')

# C2: Earth in digits; the UAE's own digits recoloured and framed
def c2():
    W, H, D = 1080, 880, 900
    t = np.zeros((H, W)); ox = (W - D) // 2 + 40
    t[0:D, ox:ox + D - max(0, ox + D - W)] = tone('earth_hd.png', D, D, lo=0.05, hi=0.7)[:H, :W - ox]
    ax, ay = ox + 0.62 * D, 0.455 * D
    acc = ellipse(t.shape, ax, ay, 46, 34)
    y, x = np.mgrid[0:H, 0:W]
    faint = (x - ox - D / 2) ** 2 + (y - D / 2) ** 2 < (0.48 * D) ** 2
    im = ascii(t, PALETTES['navy'], accent=acc, faint=faint)
    im = frame(im, (ax - 70, ay - 60, ax + 70, ay + 60), 'UAE · 70.1% USE GENERATIVE AI', color=BRASS)
    im.save('c2_img.png')

# P2: a one-page dashboard drawn in cells: six tiles, revenue-by-hour tile highlighted
def p2():
    W, H = 1080, 780; t = np.zeros((H, W)); tiles = []
    for r in range(3):
        for c in range(2):
            a, b = 96 + c * 456, 96 + r * 228; tiles.append((a, b, a + 432, b + 204))
    hours = [0.2, 0.15, 0.1, 0.1, 0.12, 0.2, 0.35, 0.5, 0.62, 0.7, 0.75, 0.8, 0.85, 0.8, 0.7, 0.72, 0.78, 0.9, 1.0, 0.95, 0.85, 0.7, 0.5, 0.35]
    for k, (a, b, c, d) in enumerate(tiles):
        t[b:d, a:c] = np.maximum(t[b:d, a:c], 0.12)  # tile outline cells
        if k == 0:
            tt, _ = bars_tone(c - a, d - b - 40, hours, 12, c - a - 12, d - b - 52, 10, gapf=0.2)
            t[b + 40:d, a:c] = np.maximum(t[b + 40:d, a:c], tt[:d - b - 40] * 0.95)
        else:
            vals = [0.55, 0.7, 0.45, 0.35, 0.6][k - 1]
            t[b + 120:b + 156, a + 24:a + 24 + int(380 * vals)] = 0.8
    acc = mask_box(t.shape, tiles[0])
    im = pixels(t, PALETTES['light'], cell=12, gap=2, accent=acc)
    names = ['1 REVENUE BY HOUR', '2 CONVERSION', '3 AVG ORDER', '4 DISCOUNT DEPTH', '5 STOCK-OUTS', '6 RETURNS (30 DAYS)']
    for (a, b, c, d), n in zip(tiles, names):
        im = label(im, (a + 24, b + 18), n, NAVY, 15)
    im.save('p2_img.png')

# C3: line field, every line wobbles except one: revenue, defined once
def c3():
    W, H = 1080, 760; r = np.random.default_rng(5)
    y, x = np.mgrid[0:H, 0:W]; t = np.zeros((H, W))
    for k in range(9):
        cx, cy, s = r.uniform(80, 1000), r.uniform(60, 700), r.uniform(70, 160)
        t += r.uniform(0.4, 0.9) * np.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (2 * s * s))
    t = np.clip(t, 0, 1); band = (y > 372) & (y < 392); t[band] = 0.55
    acc = np.zeros_like(band); acc[378:386, :] = True
    im = lines(t, PALETTES['navy'], gap=20, amp=44, width=1.8, accent=acc)
    im = label(im, (90, 410), 'REVENUE · ONE DEFINITION, EVERY REPORT', BRASS, 16)
    im.save('c3_img.png')

# N1: five scattered sources, one dashboard
def n1():
    W, H = 1080, 760; t = np.zeros((H, W)); r = np.random.default_rng(11)
    srcs = [(90, 80), (300, 230), (110, 400), (330, 520), (150, 600)]
    for a, b in srcs:
        w, h = int(r.integers(130, 190)), int(r.integers(90, 130))
        blk = (r.random((h // 12 + 1, w // 12 + 1)) > 0.35) * r.uniform(0.3, 0.75, (h // 12 + 1, w // 12 + 1))
        t[b:b + h, a:a + w] = np.kron(blk, np.ones((12, 12)))[:h, :w]
    t[200:560, 640:990] = 0.25
    for k, v in enumerate([0.6, 0.85, 0.45, 0.95]):
        t[480 - int(220 * v):480, 680 + k * 76:680 + k * 76 + 52] = 0.95
    acc = mask_box(t.shape, (640, 200, 990, 560))
    im = pixels(t, PALETTES['navy'], cell=12, gap=2, accent=acc)
    im = frame(im, (628, 188, 1002, 572), 'ONE DASHBOARD · SAMPLE', color=BRASS)
    im.save('n1_img.png')

# N2: survey answers (digits) becoming an indicator; the indicator due in the report in brass
def n2():
    W, H = 1080, 760
    t, bx = bars_tone(W, H, [0.55, 0.72, 0.40, 0.86, 0.63], 120, 960, 640, 110)
    acc = mask_box(t.shape, bx[3])
    im = ascii(t * 0.95, PALETTES['navy'], seed=9, accent=acc)
    a, top, b, _ = bx[3]
    im = frame(im, (a - 14, top - 14, b + 14, 650), 'INDICATOR 4 · SAMPLE DATA', color=BRASS)
    im.save('n2_img.png')

if __name__ == '__main__':
    for f in (p1, c1, c2, p2, c3, n1, n2): f()
