# .describe( image atmosphere: turn any source photo into the brand's image language.
# Rules live in ATMOSPHERE.md next to this file. One subject, rebuilt from one unit
# (glyph, pixel, dot or line) on a strict grid, one ink on one flat ground, attention
# guided by contrast falloff and by recolouring the image's own units at the focus.
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, '..', '..', 'decisions', 'fonts') + '/'

def hexrgb(h): h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
def lerp(a, b, t): return tuple(int(x + (y - x) * t) for x, y in zip(a, b))

# Grounds and inks. Each palette is one ground, a dim and a full ink, and one accent.
PALETTES = {
    'navy':  dict(ground='#092052', lo='#1E3A6B', hi='#E6EFFF', accent='#D9AE62'),   # brass accent
    'paper': dict(ground='#F3EEE4', lo='#D8D0C0', hi='#092052', accent='#0F58E5'),   # blue accent
    'light': dict(ground='#F6F8FC', lo='#C9D6F2', hi='#0F58E5', accent='#092052'),
    'blue':  dict(ground='#0F58E5', lo='#3B74E8', hi='#F6F8FC', accent='#D9AE62'),
}

def tone(path, W, H, fit='cover', offset=(0, 0), scale=1.0, lo=0.04, hi=0.9, invert=False):
    """Photo -> 0..1 tone map at W x H, subject bright. offset/scale place the photo."""
    im = Image.open(path).convert('L')
    s = max(W / im.width, H / im.height) * scale if fit == 'cover' else min(W / im.width, H / im.height) * scale
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    a = np.asarray(im, float) / 255
    if invert: a = 1 - a
    a = np.clip((a - lo) / (hi - lo), 0, 1)
    out = np.zeros((H, W))
    x0 = (W - a.shape[1]) // 2 + offset[0]; y0 = (H - a.shape[0]) // 2 + offset[1]
    sx0, sy0 = max(0, -x0), max(0, -y0); dx0, dy0 = max(0, x0), max(0, y0)
    w = min(a.shape[1] - sx0, W - dx0); h = min(a.shape[0] - sy0, H - dy0)
    out[dy0:dy0 + h, dx0:dx0 + w] = a[sy0:sy0 + h, sx0:sx0 + w]
    return out

def focus(t, cx, cy, r, floor=0.45):
    """Contrast falloff: full tone inside radius r of the focus, fading to `floor` far away."""
    y, x = np.mgrid[0:t.shape[0], 0:t.shape[1]]
    d = np.sqrt((x - cx) ** 2 + (y - cy) ** 2) / r
    k = np.clip(1 - (d - 1) * 0.6, floor, 1)
    return t * k

def ellipse(shape, cx, cy, rx, ry):
    y, x = np.mgrid[0:shape[0], 0:shape[1]]
    return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 < 1

# ---- treatments ---------------------------------------------------------------------

def ascii(t, pal, cw=8, ch=13, size=12, seed=4, accent=None, faint=None):
    """Digits for tone, weight for depth: bright = medium digits, mid = regular, dim = ':' '.'."""
    H, W = t.shape; S = 2; p = {k: hexrgb(v) for k, v in pal.items()}
    im = Image.new('RGB', (W * S, H * S), p['ground']); d = ImageDraw.Draw(im)
    fr = ImageFont.truetype(FONTS + 'IBMPlexMono-Regular.ttf', size * S)
    fm = ImageFont.truetype(FONTS + 'IBMPlexMono-Medium.ttf', size * S)
    r = np.random.default_rng(seed)
    for j in range(0, H, ch):
        for i in range(0, W, cw):
            v = t[j, i]
            if v < 0.05:
                if faint is not None and faint[j, i]:
                    d.text((i * S, j * S), '.', font=fr, fill=lerp(p['ground'], p['lo'], 0.6))
                continue
            c = lerp(p['lo'], p['hi'], min(1, v ** 1.5 * 1.2))
            if accent is not None and accent[j, i] and v > 0.45: c = p['accent']
            g = str(r.integers(10)) if v > 0.2 else ('.' if v < 0.11 else ':')
            d.text((i * S, j * S), g, font=fm if v > 0.5 else fr, fill=c)
    return im.resize((W, H), Image.LANCZOS)

def pixels(t, pal, cell=12, gap=2, accent=None, outline=True):
    """Square cells on a visible grid. Tone picks the fill step; empty cells keep a hairline grid."""
    H, W = t.shape; S = 2; p = {k: hexrgb(v) for k, v in pal.items()}
    im = Image.new('RGB', (W * S, H * S), p['ground']); d = ImageDraw.Draw(im)
    small = np.asarray(Image.fromarray((t * 255).astype(np.uint8)).resize((W // cell, H // cell), Image.BOX), float) / 255
    for j in range(small.shape[0]):
        for i in range(small.shape[1]):
            v = small[j, i]; x, y = i * cell * S, j * cell * S
            box = [x + gap, y + gap, x + cell * S - gap, y + cell * S - gap]
            if v < 0.08:
                continue
            q = min(4, int(v * 5))  # five tone steps, no gradients
            c = lerp(p['lo'], p['hi'], q / 4)
            ac = accent is not None and accent[min(H - 1, j * cell), min(W - 1, i * cell)] and v > 0.4
            if ac: c = p['accent']
            if q <= 1 and outline and not ac: d.rectangle(box, outline=c, width=S)
            else: d.rectangle(box, fill=c)
    return im.resize((W, H), Image.LANCZOS)

def dots(t, pal, cell=11, accent=None):
    """Halftone on a square grid: dot size carries tone, edges stay crisp (no blur, no grain)."""
    H, W = t.shape; S = 2; p = {k: hexrgb(v) for k, v in pal.items()}
    im = Image.new('RGB', (W * S, H * S), p['ground']); d = ImageDraw.Draw(im)
    for j in range(cell // 2, H, cell):
        for i in range(cell // 2, W, cell):
            v = t[j, i]
            if v < 0.06: continue
            rr = (0.12 + 0.38 * v ** 0.8) * cell * S
            c = p['accent'] if accent is not None and accent[j, i] and v > 0.4 else lerp(p['lo'], p['hi'], min(1, 0.35 + v))
            d.ellipse([i * S - rr, j * S - rr, i * S + rr, j * S + rr], fill=c)
    return im.resize((W, H), Image.LANCZOS)

def lines(t, pal, gap=10, amp=9, width=1.6, accent=None):
    """Line field: horizontal lines lifted by tone (moodboard line field, contour posters)."""
    H, W = t.shape; S = 2; p = {k: hexrgb(v) for k, v in pal.items()}
    tb = np.asarray(Image.fromarray((t * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2)), float) / 255
    im = Image.new('RGB', (W * S, H * S), p['ground']); d = ImageDraw.Draw(im)
    for y0 in range(gap, H, gap):
        pts = []; prev = None
        for x in range(0, W, 3):
            v = tb[y0, x]; y = y0 - v * amp
            c = p['accent'] if accent is not None and accent[y0, x] and v > 0.4 else lerp(p['lo'], p['hi'], min(1, 0.2 + v))
            if prev is not None:
                d.line([prev[0], (x * S, y * S)], fill=prev[1], width=int(width * S * (0.6 + v)))
            prev = ((x * S, y * S), c)
    return im.resize((W, H), Image.LANCZOS)

# ---- annotation ---------------------------------------------------------------------

def frame(im, box, label=None, color='#D9AE62', ground='#092052', k=26, w=2, side='below'):
    """Corner brackets around the focus, with an optional mono label on a knocked-out chip."""
    S = 2; W, H = im.size
    big = im.resize((W * S, H * S), Image.LANCZOS); d = ImageDraw.Draw(big)
    x0, y0, x1, y1 = [v * S for v in box]; c = hexrgb(color); k *= S; w *= S
    for px, py, sx, sy in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        d.line([(px, py), (px + sx * k, py)], fill=c, width=w); d.line([(px, py), (px, py + sy * k)], fill=c, width=w)
    if label:
        f = ImageFont.truetype(FONTS + 'IBMPlexMono-Medium.ttf', 15 * S)
        tx, ty = (x0, y1 + 14 * S) if side == 'below' else (x1 + 18 * S, y0)
        bb = d.textbbox((tx, ty), label, font=f)
        d.rectangle([bb[0] - 8 * S, bb[1] - 6 * S, bb[2] + 8 * S, bb[3] + 6 * S], fill=hexrgb(ground))
        d.text((tx, ty), label, font=f, fill=c)
    return big.resize((W, H), Image.LANCZOS)

TREATMENTS = dict(ascii=ascii, pixels=pixels, dots=dots, lines=lines)
