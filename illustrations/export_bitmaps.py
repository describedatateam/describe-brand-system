"""export_bitmaps.py — every illustration as separate 1-bit layers.

For each figure: one transparent PNG per layer (ink = black, paper = transparent),
plus flat previews in the brand colours on paper and on navy.
    python3 export_bitmaps.py            → bitmaps/<name>/…
"""
import os, json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import bitmap as B
U = '/mnt/user-data/uploads/arabia/'
OUT = 'bitmaps'
K = 2.5   # scale against the web sizes

LIGHT = {'ground': (246, 248, 252), 'ink': (9, 32, 82), 'body': (90, 107, 133), 'faint': (203, 213, 225),
         'active': (15, 88, 229), 'mark': (229, 72, 77)}
DARK = {'ground': (5, 15, 46), 'ink': (246, 248, 252), 'body': (159, 176, 204), 'faint': (28, 53, 102),
        'active': (91, 141, 240), 'mark': (240, 105, 109)}


def fit(im, w):
    return im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)


def stars_at_scale(im, min_area, keep_ratio=0.55):
    """Find al-Sufi's red stars on a 1/K copy (where the detector is tuned),
    drop the specks left by red lettering, then redraw each star as a clean
    disc at full size."""
    small = im.resize((int(im.width / K), int(im.height / K)), Image.LANCZOS)
    _, stars = B.dot_layer(small, min_area=int(min_area / (K * K)))
    if stars:
        med = float(np.median([r for _, _, r in stars]))
        stars = [s for s in stars if s[2] >= keep_ratio * med]
        m = 0.03 * max(small.size)          # page gutter and trimmed edge: stains, not stars
        stars = [s for s in stars if m < s[0] < small.width - m and m < s[1] < small.height - m]
    yy, xx = np.mgrid[0:im.height, 0:im.width]
    out = np.zeros((im.height, im.width), bool)
    for cx, cy, r in stars:
        out |= (xx - cx * K) ** 2 + (yy - cy * K) ** 2 <= (r * K) ** 2
    return out


def figure(im, min_area, keep_ratio=0.55):
    red = stars_at_scale(im, min_area, keep_ratio)
    grey = B.grey_dot_layer(im, min_area=int(60 * K * K / 4))
    lines = B.line_layer(im, exclude=red | grey, min_blob=int(30 * K))
    return lines, red, grey


def save_mask(m, path):
    a = np.zeros((*m.shape, 4), np.uint8)
    a[m, 3] = 255
    Image.fromarray(a, 'RGBA').convert('LA').save(path, optimize=True)


def flat(layers, spec, pal, path):
    h, w = next(iter(layers.values())).shape
    out = np.zeros((h, w, 3), np.uint8)
    out[:] = pal['ground']
    for k, tok in spec:
        if k in layers:
            out[layers[k]] = pal[tok]
    Image.fromarray(out).save(path, optimize=True)


MANIFEST = []


def export(name, im, layers, spec, source):
    d = os.path.join(OUT, name)
    os.makedirs(d, exist_ok=True)
    files = {}
    for k, m in layers.items():
        p = f'{name}_{k}.png'
        save_mask(m, os.path.join(d, p))
        files[k] = p
    flat(layers, spec, LIGHT, os.path.join(d, f'{name}_preview-paper.png'))
    flat(layers, spec, DARK, os.path.join(d, f'{name}_preview-navy.png'))
    if 'dotted' in layers:   # the hero treatment: stars first, figure as a trace
        sf = [('dotted', 'body'), ('outside', 'ink'), ('stars', 'active')]
        flat(layers, sf, LIGHT, os.path.join(d, f'{name}_preview-starsfirst-paper.png'))
        flat(layers, sf, DARK, os.path.join(d, f'{name}_preview-starsfirst-navy.png'))
    MANIFEST.append({'name': name, 'size': list(im.size), 'layers': files,
                     'colours': {k: t for k, t in spec}, 'source': source})
    print(name, im.size, list(files))


def main():
    SUFI = 'al-Sufi, Book of the Images of the Fixed Stars, Iran, late 15th c. The Met 446297, public domain'
    STD = [('lines', 'ink'), ('outside', 'ink'), ('stars', 'active')]

    # Cygnus — full figure, with the dotted trace used in the hero
    cyg = fit(Image.open('sources/DP232491.jpg').crop((330, 760, 2380, 3120)), int(760 * K))
    L, R, G = figure(cyg, int(60 * K * K / 2))
    export('cygnus', cyg, {'lines': L, 'dotted': B.dotted(L, 3), 'stars': R, 'outside': G},
           [('lines', 'ink'), ('outside', 'ink'), ('stars', 'active')], SUFI + ' (DP232491)')

    # Cygnus detail — the two stars outside the figure, as outlier markers
    c1 = fit(Image.open('sources/DP232491.jpg').crop((330, 1700, 1500, 2800)), int(560 * K))
    L, R, G0 = figure(c1, int(40 * K * K / 2))
    n1 = B.flatten(c1, 25 * K)
    yy, xx = np.mgrid[0:c1.height, 0:c1.width]
    near = np.zeros(n1.shape, bool)
    for cx, cy in [(126, 212), (168, 256)]:
        near |= (xx - cx * K) ** 2 + (yy - cy * K) ** 2 < (24 * K) ** 2
    blob = ndi.binary_fill_holes((n1 < 0.72) & near)
    lab, k = ndi.label(blob)
    G = np.zeros(n1.shape, bool)
    clear = np.zeros(n1.shape, bool)
    for i in range(1, k + 1):
        if (lab == i).sum() < 40 * K * K:
            continue
        cy, cx = ndi.center_of_mass(lab == i)
        d2 = (xx - cx) ** 2 + (yy - cy) ** 2
        G |= ((d2 <= (14 * K) ** 2) & (d2 >= (11.5 * K) ** 2)) | (d2 <= (5 * K) ** 2)
        clear |= d2 <= (17 * K) ** 2
    L &= ~clear
    export('cygnus-outside', c1, {'lines': L, 'stars': R, 'outside': G},
           [('lines', 'ink'), ('stars', 'active'), ('outside', 'mark')], SUFI + ' (DP232491), detail')

    # Astrolabe plate — one layer
    ast = Image.open(U + 'Or 14270_0149.jpg').crop((70, 110, 820, 900))
    ast = ast.resize((ast.width * 2, ast.height * 2), Image.LANCZOS)   # source is only 894 px wide
    n = B.flatten(ast, 40)
    m = n < 0.86
    lab, k = ndi.label(m)
    sz = ndi.sum(m, lab, range(1, k + 1))
    keep = np.zeros(k + 1, bool)
    keep[1:] = sz >= 100
    export('astrolabe-plate', ast, {'lines': keep[lab]}, [('lines', 'ink')],
           'Arabic astrolabe treatise, British Library Or 14270, f. 0149 — SOURCE RECORD TO CONFIRM (upscaled 2x from an 894 px scan)')

    # Libra (on the globe), Cancer (globe and sky)
    for name, f, box, src in [
            ('libra', 'DP232533.jpg', (140, 700, 2080, 1960), 'DP232533'),
            ('cancer-globe', 'DP232528.jpg', (420, 860, 2000, 1880), 'DP232528, upper figure'),
            ('cancer-sky', 'DP232528.jpg', (380, 2380, 1980, 3440), 'DP232528, lower figure')]:
        im = fit(Image.open(U + f).crop(box), int(620 * K) if name == 'libra' else int(520 * K))
        L, R, G = figure(im, int(60 * K * K / 2), 0.75 if name == 'libra' else 0.55)
        export(name, im, {'lines': L, 'stars': R, 'outside': G}, STD, f'{SUFI} ({src})')

    # Sky band — Milky Way strip
    sky = Image.open(U + '11241855653_071d71380a_o.jpg').crop((0, 330, 1425, 610))
    sky = fit(sky, 2400)
    sm = B.sky_layer(sky, glow_max=0.26)
    x = np.linspace(0, 1, sky.width)
    env = np.clip(np.minimum(x, 1 - x) * 4, 0, 1)
    sm_fade = sm & B.ordered(np.tile(env, (sky.height, 1)), gamma=1.0, scale=1)
    export('sky-band', sky, {'sky': sm_fade, 'sky-nofade': sm}, [('sky', 'faint')],
           'Milky Way star chart, 19th-century book, British Library Flickr scan 11241855653 — SOURCE BOOK TO CONFIRM')

    json.dump(MANIFEST, open(os.path.join(OUT, 'manifest.json'), 'w'), indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
