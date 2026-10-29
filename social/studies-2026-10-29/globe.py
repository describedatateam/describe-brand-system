# Round two of the Earth-in-digits study, using moves from the user's moodboard folder:
#  a: the globe sits low and its top dissolves into loose cells and digits (moodboard "Repairing")
#  b: thin corner brackets frame a region, with a mono label (moodboard "Point of view", "Koza")
#  c: navy ink on cream paper, a column of digits set beside it (moodboard binary Great Wave)
from render import *

def earth(D):
    return contrast(lum('src/earth_hd.png', D, D), 0.06, 0.85)

def draw_digits(src, W, H, bg, lo, hi, cw=8, ch=13, size=12, seed=4, hl=None, hl_mask=None,
                dissolve=None, dot=None):
    S = 2
    im = Image.new('RGB', (W * S, H * S), hexrgb(bg)); d = ImageDraw.Draw(im)
    fr = ImageFont.truetype(F + 'IBMPlexMono-Regular.ttf', size * S)
    fm = ImageFont.truetype(F + 'IBMPlexMono-Medium.ttf', size * S)
    r = np.random.default_rng(seed)
    for j in range(0, H, ch):
        for i in range(0, W, cw):
            v = src[j, i]
            if dissolve is not None and r.random() < dissolve[j, i]: continue
            if v < 0.05:
                if dot is not None and dot[j, i]: d.text((i * S, j * S), '.', font=fr, fill=lerp(hexrgb(bg), lo, 0.6))
                continue
            c = lerp(lo, hi, min(1, v ** 1.5 * 1.2))
            if hl_mask is not None and hl_mask[j, i] and v > 0.45: c = hl
            g = str(r.integers(10)) if v > 0.2 else ('.' if v < 0.11 else ':')
            d.text((i * S, j * S), g, font=fm if v > 0.5 else fr, fill=c)
    return im.resize((W, H), Image.LANCZOS)

def disc(W, H, cx, cy, rad):
    y, x = np.mgrid[0:H, 0:W]
    return (x - cx) ** 2 + (y - cy) ** 2 < rad ** 2

# a: large globe, top third breaks up as it rises
def ga():
    W, H, D = 1080, 900, 1200
    src = np.zeros((H, W)); ox, oy = (W - D) // 2, 260
    g = earth(D); src[oy:H, :] = g[:H - oy, -ox:-ox + W]
    y = np.mgrid[0:H, 0:W][0]
    dissolve = np.clip((oy + 330 - y) / 330, 0, 1) ** 1.4 * 0.92
    im = draw_digits(src, W, H, NAVY, hexrgb('#1E3A6B'), hexrgb('#E6EFFF'), dissolve=dissolve,
                     dot=disc(W, H, ox + D / 2, oy + D / 2, 0.48 * D))
    # loose cells above the horizon: the same digits lifting off as squares
    d = ImageDraw.Draw(im); r = np.random.default_rng(21)
    for _ in range(140):
        i = int(r.integers(0, W // 16)) * 16; j = int(oy + 120 - abs(r.normal(0, 150)))
        if j < 0 or src[min(H - 1, j + 200), i] < 0.15: continue
        s = 9 if r.random() < 0.7 else 13
        d.rectangle([i, j, i + s, j + s], fill=lerp(hexrgb('#1E3A6B'), hexrgb('#9DB5E8'), r.random()))
    im.save('ga_img.png')

# b: globe drawn in digits, Arabia recoloured brass and framed with corner brackets + label
def gb():
    W, H, D = 1080, 880, 900
    src = np.zeros((H, W)); ox, oy = (W - D) // 2 + 40, 0
    src[oy:oy + D, ox:ox + D - max(0, ox + D - W)] = earth(D)[:H - oy, :W - ox]
    ax, ay = ox + 0.57 * D, oy + 0.43 * D
    y, x = np.mgrid[0:H, 0:W]
    mask = ((x - ax) ** 2 / 120 ** 2 + (y - ay) ** 2 / 95 ** 2) < 1
    im = draw_digits(src, W, H, NAVY, hexrgb('#1E3A6B'), hexrgb('#E6EFFF'), hl=hexrgb('#D9AE62'),
                     hl_mask=mask, dot=disc(W, H, ox + D / 2, oy + D / 2, 0.48 * D))
    S = 2; im = im.resize((W * S, H * S), Image.LANCZOS); d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = [v * S for v in (ax - 140, ay - 115, ax + 140, ay + 115)]
    k, w, c = 26 * S, 2 * S, hexrgb('#D9AE62')
    for (px, py, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        d.line([(px, py), (px + sx * k, py)], fill=c, width=w); d.line([(px, py), (px, py + sy * k)], fill=c, width=w)
    f = ImageFont.truetype(F + 'IBMPlexMono-Medium.ttf', 15 * S)
    t = 'GCC · 1 OF 7 REGIONS'; tx, ty = x0, y1 + 14 * S
    bb = d.textbbox((tx, ty), t, font=f)
    d.rectangle([bb[0] - 8 * S, bb[1] - 6 * S, bb[2] + 8 * S, bb[3] + 6 * S], fill=hexrgb(NAVY))
    d.text((tx, ty), t, font=f, fill=c)
    im.resize((W, H), Image.LANCZOS).save('gb_img.png')

# c: paper and ink. Navy digits on cream, a tall digit column at the left edge
def gc():
    W, H, D = 1080, 900, 940
    src = np.zeros((H, W)); ox, oy = 170, -20
    g = earth(D); src[0:H, ox:W] = g[-oy:-oy + H, :W - ox]
    ax, ay = ox + 0.57 * D, oy + 0.43 * D
    y, x = np.mgrid[0:H, 0:W]
    mask = ((x - ax) ** 2 / 120 ** 2 + (y - ay) ** 2 / 95 ** 2) < 1
    im = draw_digits(src, W, H, CREAM, hexrgb('#D8D0C0'), hexrgb(NAVY), hl=hexrgb(BLUE), hl_mask=mask,
                     dot=disc(W, H, ox + D / 2, oy + D / 2, 0.48 * D))
    d = ImageDraw.Draw(im); f = ImageFont.truetype(F + 'IBMPlexMono-Medium.ttf', 15)
    r = np.random.default_rng(3)
    for j in range(40, 560, 19):
        d.text((88, j), ''.join(str(r.integers(2)) for _ in range(3)), font=f, fill=hexrgb(NAVY))
    im.save('gc_img.png')

if __name__ == '__main__':
    ga(); gb(); gc()
