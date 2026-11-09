# Images for the LinkedIn posts of 10-12 Nov 2026. Follows social/atmosphere/ATMOSPHERE.md:
# one subject rebuilt from one unit on a grid, highlight = the image's own units recoloured,
# no star, no glow/grain, no pattern. Real figures come from site/proof/figures.json; others are labelled sample.
import numpy as np, json
from PIL import Image, ImageDraw, ImageFont
from atmos import *
B = '/home/claude/describe-brand-system'; F = B + '/decisions/fonts/'
NAVY, BRASS, GREY, DGREY = '#092052', '#D9AE62', '#64748B', '#8A99B0'
FIG = json.load(open(B + '/site/proof/figures.json'))

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

# R1: every identified customer as one dot (4,371 = 93 x 47); the top 1% (43) recoloured brass
def r1():
    n, top = FIG['identified_customers'], FIG['top_1pct_customers']
    cols, rows, cell = 93, 47, 10; x0, y0 = 75, 40; W, H = 1080, 600
    t = np.zeros((H, W)); acc = np.zeros((H, W), bool)
    for k in range(n):
        j, i = divmod(k, cols); cx, cy = x0 + i * cell + 5, y0 + j * cell + 5
        t[cy - 2:cy + 3, cx - 2:cx + 3] = 0.75
        if k < top: acc[cy - 2:cy + 3, cx - 2:cx + 3] = True
    im = dots(t, PALETTES['light'], cell=cell, accent=acc) if False else None
    # draw directly: one dot per customer, crisp
    S = 2; p = {k: hexrgb(v) for k, v in PALETTES['light'].items()}
    big = Image.new('RGB', (W * S, H * S), p['ground']); d = ImageDraw.Draw(big)
    for k in range(n):
        j, i = divmod(k, cols); cx, cy = (x0 + i * cell + 5) * S, (y0 + j * cell + 5) * S
        c = p['accent'] if k < top else lerp(p['lo'], p['hi'], 0.45); r = 3.6 * S if k < top else 2.6 * S
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)
    im = big.resize((W, H), Image.LANCZOS)
    im = frame(im, (x0 - 6, y0 - 6, x0 + 43 * cell + 6, y0 + cell + 6), None, color=NAVY, ground='#F6F8FC')
    im = label(im, (x0, y0 + rows * cell + 26), f'{n:,} CUSTOMERS · ONE DOT EACH', GREY, 15)
    im = label(im, (x0, y0 + rows * cell + 52), f'THE FIRST {top}: {round(FIG["top_1pct_share_of_identified_net"]*100)}% OF REVENUE', NAVY, 15)
    im.save('r1_img.png')

# B1: traffic by channel in digits (sample); the AI-assistant slice inside "referral" in brass
def b1():
    W, H = 1080, 720
    vals = [0.92, 0.74, 0.46, 0.30]
    t, bx = bars_tone(W, H, vals, 110, 970, 600, 60, gapf=0.36)
    a, top, b, base = bx[2]; acc = mask_box(t.shape, (a, top, b, top + 70))
    im = ascii(t * 0.95, PALETTES['navy'], seed=3, accent=acc)
    for (a, _, b, _), n in zip(bx, ['DIRECT', 'ORGANIC', 'REFERRAL', 'PAID']):
        im = label(im, ((a + b) / 2, 630), n, DGREY, 16, 'ma')
    a, top, b, _ = bx[2]
    im = frame(im, (a - 12, top - 12, b + 12, top + 82), 'AI ASSISTANTS · SAMPLE', color=BRASS)
    im.save('b1_img.png')

# B2: one block of pixels for Sep 2025, seven for Sep 2026 (Coupler.io's ratio, shape only)
def b2():
    W, H = 1080, 720; t = np.zeros((H, W)); blk = 72; base = 620
    colA, colB = 260, 640
    t[base - blk:base, colA:colA + 180] = 0.85
    for k in range(7): t[base - (k + 1) * blk - k * 0 : base - k * blk, colB:colB + 180] = 0.85 if k == 0 else 0.85
    acc = mask_box(t.shape, (colB, base - 7 * blk, colB + 180, base - blk))
    im = pixels(t, PALETTES['light'], cell=12, gap=2, accent=acc)
    im = label(im, (colA + 90, 646), 'SEP 2025', GREY, 17, 'ma'); im = label(im, (colB + 90, 646), 'SEP 2026', NAVY, 17, 'ma')
    im = label(im, (colA + 90, base - blk - 40), '1×', GREY, 30, 'ma'); im = label(im, (colB + 90, base - 7 * blk - 44), '7×', NAVY, 30, 'ma')
    im.save('b2_img.png')

# R2: forecast error, total vs per product (real test on the Online Retail data)
def r2():
    W, H = 1080, 720
    t, bx = bars_tone(W, H, [0.02, 0.55 / 0.6], 200, 880, 600, 90, gapf=0.42)
    a, b_, c, d = bx[0]; t[d - 12:d, a:c] = 1.0  # 1% still shows as one row of digits
    acc = mask_box(t.shape, bx[1])
    im = ascii(t * 0.95, PALETTES['navy'], seed=12, accent=acc)
    for (a, top, b, _), big, sub in zip(bx, ['1%', '~55%'], ['ALL PRODUCTS · TOTAL', 'ONE PRODUCT · AVERAGE']):
        im = label(im, ((a + b) / 2, min(top, 588) - 62), big, '#E6EFFF', 42, 'ma')
        im = label(im, ((a + b) / 2, 630), sub, DGREY, 16, 'ma')
    im = label(im, (540, 676), 'PROJECTION VS ACTUAL DECEMBER 2011', DGREY, 14, 'ma')
    im.save('r2_img.png')

# B3: a five-line worksheet in pixels: number, owner, source, act-if; cells left to fill in
def b3():
    W, H = 1080, 740; t = np.zeros((H, W)); x = [90, 470, 650, 830, 990]; rows = []
    for r in range(5):
        y = 70 + r * 128; rows.append(y)
        t[y:y + 96, x[0]:x[0] + 24] = 0.85
        for c in range(1, 4): t[y:y + 96, x[c]:x[c + 1] - 24] = 0.15
    im = pixels(t, PALETTES['light'], cell=12, gap=2)
    for c, n in zip(range(1, 4), ['OWNER', 'SOURCE', 'ACT IF']):
        im = label(im, (x[c], 38), n, GREY, 15)
    for r, n in enumerate(['1 REVENUE, NET', '2 GROSS MARGIN', '3 NEW CUSTOMERS', '4 REPEAT CUSTOMERS', '5 CASH IN BANK']):
        im = label(im, (x[0] + 44, rows[r] + 38), n, NAVY, 17)
    im.save('b3_img.png')

# N1: an indicator table (12 indicators x 4 quarters) in pixels; this quarter's column still being compiled
def n1():
    W, H = 1080, 800; t = np.zeros((H, W)); r = np.random.default_rng(21)
    cx = [250, 430, 610, 790]; cw, rh = 156, 46
    for i in range(12):
        y = 60 + i * 56; t[y:y + rh, 80:220] = 0.3
        for q in range(4):
            v = r.choice([0.55, 0.7, 0.85]) if q < 3 else (0.85 if r.random() < 0.35 else 0.12)
            t[y:y + rh, cx[q]:cx[q] + cw] = v
    acc = mask_box(t.shape, (cx[3], 0, cx[3] + cw, H))
    im = pixels(t, PALETTES['navy'], cell=12, gap=2, accent=acc)
    for q, n in enumerate(['Q1', 'Q2', 'Q3', 'Q4']): im = label(im, (cx[q], 14), n, BRASS if q == 3 else DGREY, 16)
    im = frame(im, (cx[3] - 12, 48, cx[3] + cw + 12, 60 + 11 * 56 + rh + 12), 'STILL BEING COMPILED · SAMPLE', color=BRASS)
    im.save('n1_img.png')

# N2: survey answers as dots, gathered into five indicator columns; the slowest one in brass (sample)
def n2():
    W, H = 1080, 760; t = np.zeros((H, W)); r = np.random.default_rng(8)
    y, x = np.mgrid[0:H, 0:W]
    hrs = [0.35, 0.5, 0.95, 0.4, 0.6]; cols = [140, 330, 520, 710, 900]
    for c, v in zip(cols, hrs):
        t[int(640 - 540 * v):640, c - 50:c + 50] = 0.9
    acc = mask_box(t.shape, (cols[2] - 50, 0, cols[2] + 50, 640))
    im = dots(t, PALETTES['light'], cell=12, accent=acc)
    for k, c in enumerate(cols): im = label(im, (c, 668), f'IND. {k + 1}', NAVY if k == 2 else GREY, 15, 'ma')
    im = label(im, (540, 706), 'HOURS TO PRODUCE EACH INDICATOR · SAMPLE', GREY, 14, 'ma')
    im.save('n2_img.png')

if __name__ == '__main__':
    for f in (r1, b1, b2, r2, b3, n1, n2): f()
