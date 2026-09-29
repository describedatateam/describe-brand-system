"""arabic_sheet.py — the Arabic size/weight decision as a comparison sheet,
rendered with the real fonts. Ink metrics disagree on how big Arabic should
be next to Latin (0.67× to 1.68× depending on the method), so this is a
judgement by eye. Latin and Arabic share a baseline on every row."""
from PIL import Image, ImageDraw, ImageFont
import numpy as np
F = 'fonts/'; K = 2
INK = (9, 32, 82); BODY = (90, 107, 133); DIM = (99, 115, 141); RULE = (216, 225, 239); G = (246, 248, 252)

def font(p, px, axes=None):
    f = ImageFont.truetype(F + p, int(px * K), layout_engine=ImageFont.Layout.RAQM)
    if axes: f.set_variation_by_axes(axes)
    return f

def stem(f, t, rtl=False):
    S = f.size
    im = Image.new('L', (S * 4, S * 3), 0); ImageDraw.Draw(im).text((S, S), t, font=f, fill=255, direction='rtl' if rtl else None)
    a = np.asarray(im) > 128; ys, xs = np.where(a); y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    return float(np.median([a[y, x0:x1 + 1].sum() for y in range(y0 + (y1 - y0) // 3, y1 - (y1 - y0) // 3)]))

W = 1500 * K
rows = []
lab = font('ReadexPro%5BHEXP,wght%5D.ttf', 13, [400, 0])
title = font('Fraunces%5BSOFT,WONK,opsz,wght%5D.ttf', 30, [36, 300, 0, 0])

# ---- display: Fraunces 300 at 56 px vs Amiri at 56 × s
disp = [1.0, 1.1, 1.2, 1.3, 1.4]
# ---- body: Readex 300 at 16 px vs Vazirmatn at 16 × s, weight matched by stem
body = [1.0, 1.1, 1.2, 1.3]
ref_l = stem(font('ReadexPro%5BHEXP,wght%5D.ttf', 200, [300, 0]), 'l')
best_w = {}
for s in body:
    c = {w: stem(font('Vazirmatn%5Bwght%5D.ttf', 200 * s, [w]), 'ا', True) for w in (200, 250, 300, 350, 400)}
    best_w[s] = min(c, key=lambda w: abs(c[w] - ref_l))

H = (140 + len(disp) * 120 + 90 + len(body) * 150 + 60) * K
im = Image.new('RGB', (W, H), G); d = ImageDraw.Draw(im)
y = 40 * K
d.text((60 * K, y), 'Arabic next to Latin: pick the row where they look the same size', font=title, fill=INK); y += 60 * K
d.text((60 * K, y), 'Display: Fraunces 300 at 56 px, Amiri at 56 px × scale. Shared baseline.', font=lab, fill=BODY); y += 50 * K
fr = font('Fraunces%5BSOFT,WONK,opsz,wght%5D.ttf', 56, [56, 300, 0, 0])
for s in disp:
    am = font('Amiri-Regular.ttf', 56 * s)
    base = y + 80 * K
    d.line([(60 * K, base), (W - 60 * K, base)], fill=RULE, width=K)
    d.text((60 * K, base), 'Grow it on evidence', font=fr, fill=INK, anchor='ls')
    d.text((W - 200 * K, base), 'من البيانات إلى القرار', font=am, fill=INK, anchor='rs', direction='rtl')
    d.text((W - 60 * K, base), f'{s:.1f}', font=lab, fill=DIM, anchor='rs')
    y += 120 * K
y += 30 * K
d.text((60 * K, y), 'Body: Readex Pro 300 at 16 px, Vazirmatn at 16 px × scale, weight chosen by stem match.', font=lab, fill=BODY); y += 40 * K
rx = font('ReadexPro%5BHEXP,wght%5D.ttf', 16, [300, 0])
for s in body:
    vz = font('Vazirmatn%5Bwght%5D.ttf', 16 * s, [best_w[s]])
    for i, (la, ar) in enumerate([('We analyse your sales, customer and campaign numbers', 'نحلل أرقام مبيعاتك وعملائك وحملاتك'),
                                  ('so you know what is working before you bet on it.', 'لتعرف ما الذي ينجح قبل أن تراهن عليه.')]):
        base = y + (30 + i * 30) * K
        d.text((60 * K, base), la, font=rx, fill=BODY, anchor='ls')
        d.text((W - 200 * K, base), ar, font=vz, fill=BODY, anchor='rs', direction='rtl')
    d.text((W - 60 * K, y + 30 * K), f'{s:.1f} · w{best_w[s]}', font=lab, fill=DIM, anchor='rs')
    d.line([(60 * K, y + 90 * K), (W - 60 * K, y + 90 * K)], fill=RULE, width=K)
    y += 150 * K
im = im.resize((W // K, H // K), Image.LANCZOS)
im.save('arabic-size-sheet.png')
print(best_w)
