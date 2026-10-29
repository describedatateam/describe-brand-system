# Photo-sourced studies, 29 Oct 2026. Canva-generated photos (src/) are turned into the
# moodboard grammar: digits, a line field and dither cells. No star; highlights are the
# image's own marks recoloured.
import sys
sys.path.insert(0, '../studies-2026-10-28')
from engine import *
F = '../../decisions/fonts/'
NAVY, BLUE, BRASS, OFF, CREAM = '#092052', '#0F58E5', '#BF8F3C', '#F6F8FC', '#F3EEE4'

def lum(path, w, h):
    im = Image.open(path).convert('L').resize((w, h), Image.LANCZOS)
    a = np.asarray(im, float) / 255
    return (a - a.min()) / (a.max() - a.min() + 1e-6)

def contrast(a, lo, hi):
    return np.clip((a - lo) / (hi - lo), 0, 1)

# P1: Earth photo drawn in digits on navy. Brightest land over Arabia picks up brass.
def p1():
    W, H = 1080, 880
    S = 2
    src = np.zeros((H, W))
    D = 900
    g = contrast(lum('src/earth_hd.png', D, D), 0.06, 0.85)
    ox, oy = (W - D) // 2 + 40, 0
    src[oy:oy + min(D, H - oy), ox:ox + D - max(0, ox + D - W)] = g[:H - oy, :W - ox]
    im = Image.new('RGB', (W * S, H * S), hexrgb(NAVY)); d = ImageDraw.Draw(im)
    fr = ImageFont.truetype(F + 'IBMPlexMono-Regular.ttf', 12 * S)
    fm = ImageFont.truetype(F + 'IBMPlexMono-Medium.ttf', 12 * S)
    lo, hi, hl = hexrgb('#1E3A6B'), hexrgb('#E6EFFF'), hexrgb('#D9AE62')
    r = np.random.default_rng(4)
    cw, ch = 8, 13
    # brass region: the Arabian Peninsula sits around (0.57, 0.43) of the Replicate photo
    ax, ay = ox + 0.57 * D, oy + 0.43 * D
    for j in range(0, H, ch):
        for i in range(0, W, cw):
            v = src[j, i]
            inside = (i - (ox + 0.5 * D)) ** 2 + (j - (oy + 0.5 * D)) ** 2 < (0.48 * D) ** 2
            if v < 0.05:
                if inside: d.text((i * S, j * S), '.', font=fr, fill=hexrgb('#1B3566'))
                continue
            c = lerp(lo, hi, min(1, v ** 1.5 * 1.2))
            dd = ((i - ax) ** 2 / 120 ** 2 + (j - ay) ** 2 / 95 ** 2)
            if dd < 1 and v > 0.5: c = hl
            g_ = str(r.integers(10)) if v > 0.2 else ('.' if v < 0.11 else ':')
            d.text((i * S, j * S), g_, font=fm if v > 0.5 else fr, fill=c)
    im.resize((W, H), Image.LANCZOS).save('p1_img.png')

# P2: dune photo as a line field. Each row is a line of digits, lifted by the sand's
# brightness; the dune crest row is set in blue.
def p2():
    W, H = 1080, 760
    S = 2
    a = lum('src/dunes.png', 400, 500)
    a = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(5)), float) / 255
    im = Image.new('RGB', (W * S, H * S), hexrgb(CREAM)); d = ImageDraw.Draw(im)
    f = ImageFont.truetype(F + 'IBMPlexMono-Medium.ttf', 12 * S)
    r = np.random.default_rng(9)
    rows = 24; step = 7
    crest = 14
    f = ImageFont.truetype(F + 'IBMPlexMono-Medium.ttf', 11 * S)
    for k in range(rows):
        t = k / (rows - 1)
        base = 70 + t * (H - 130)
        sy = int(t * 499)
        col = lerp(hexrgb('#D6CFC1'), hexrgb(NAVY), t ** 0.8)
        if k == crest: col = hexrgb(BLUE)
        amp = 70 + 110 * t
        gap = 0
        for i in range(0, W, step):
            if gap > 0: gap -= 1; continue
            if k != crest and r.random() < 0.04: gap = int(r.integers(1, 4)); continue
            v = a[sy, int(i / W * 399)]
            y = base - (v - 0.5) * amp
            d.text((i * S, y * S), str(r.integers(10)), font=f, fill=col)
    im.resize((W, H), Image.LANCZOS).save('p2_img.png')

# P3: mountain ridge as dither cells in the S3 v1 blues. The summit's own cells go brass.
def p3():
    W, H = 1080, 800
    cell = 20
    gw, gh = W // cell, H // cell
    a = lum('src/ridge.png', gw, gh)
    # extend the land below the photo so the cells reach the footer, as in S3 v1
    a = np.vstack([a, np.zeros((12, gw))]); gh += 12; H += 12 * cell
    land = a < 0.35
    # depth below the skyline: cells dissolve near the ridge and go solid further down
    sky = np.argmax(land, axis=0)
    depth = np.arange(gh)[:, None] - sky[None, :]
    noise = fbm(gh, gw, 4, 3, 3)
    B = (bayer(4) + 0.5) / 16
    im = Image.new('RGB', (W * 2, H * 2), hexrgb(OFF)); d = ImageDraw.Draw(im)
    pal = [hexrgb(c) for c in ('#BFD0F5', '#7FA2EE', '#3B74E8', '#0F58E5', '#0B3FA8', '#092052')]
    thr = np.random.default_rng(12).random((gh, gw)) * 0.9
    peak_i = int(np.argmin(sky[gw // 2:])) + gw // 2
    for j in range(gh):
        for i in range(gw):
            if not land[j, i]: continue
            v = np.clip(depth[j, i] / 14 + 0.12, 0, 1)
            if v <= thr[j, i] and not (abs(i - peak_i) <= 1 and depth[j, i] < 3): continue
            c = pal[min(5, int(np.clip(v * 4.2 + (noise[j, i] - 0.5) * 1.6, 0, 5.99)))]
            if abs(i - peak_i) <= 1 and depth[j, i] == 0: c = hexrgb(BRASS)
            x, y = i * cell * 2, j * cell * 2
            d.rectangle([x + 2, y + 2, x + cell * 2 - 2, y + cell * 2 - 2], fill=c)
    im.resize((W, H), Image.LANCZOS).save('p3_img.png')

if __name__ == '__main__':
    p1(); p2(); p3()
