"""export_more.py — second batch of 1-bit bitmaps (see bitmaps/README.md).

Two kinds of source, two treatments:
  engravings (moon, eclipse) are already line-and-hatch → threshold
  tonal plates (comet, orbit) have soft gradients → ordered dither
Night images get both polarities: `_dark` (the dark ink as ink) and
`_light` (the light — stars, glow — as ink, for a navy ground).
"""
import os, json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import bitmap as B
import export_bitmaps as E        # reuses save_mask / flat / palettes / figure()

U = '/mnt/user-data/uploads/arabia/'
OUT = 'bitmaps'
MAN = []


def gray(im):
    return np.asarray(im.convert('L'), np.float32) / 255


def dither_tone(t, gamma=1.0, scale=1, lo=.02, hi=.98):
    a, b = np.quantile(t, [lo, hi])
    return B.ordered(np.clip((t - a) / (b - a + 1e-6), 0, 1), gamma=gamma, scale=scale)


def export(name, size, layers, spec, source, note=''):
    d = os.path.join(OUT, name); os.makedirs(d, exist_ok=True)
    files = {}
    for k, m in layers.items():
        files[k] = f'{name}_{k}.png'; E.save_mask(m, os.path.join(d, files[k]))
    for pal, tag in [(E.LIGHT, 'paper'), (E.DARK, 'navy')]:
        E.flat(layers, spec[tag], pal, os.path.join(d, f'{name}_preview-{tag}.png'))
    MAN.append({'name': name, 'size': list(size), 'layers': files, 'source': source, 'note': note})
    print(name, size, list(files))


# 1 — Encke's comet in a telescope's circular field (tonal plate)
im = Image.open(U + '11034974776_770a27baf5_o.jpg')
g = gray(im)
H, W = g.shape
yy, xx = np.mgrid[0:H, 0:W]
cx, cy, r = 1131, 1345, 790
disc = (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r
base = ndi.grey_opening(g, size=(11, 11))
stars = ((g - base) > 0.10) & disc
stars = ndi.binary_dilation(ndi.binary_opening(stars), iterations=1)
glow = ndi.gaussian_filter(base, 8)
inside = glow[disc]
glow_t = np.clip((glow - np.quantile(inside, .5)) / (np.quantile(inside, .999) - np.quantile(inside, .5)), 0, 1)
glow_m = B.ordered(glow_t * 0.55, gamma=1.3, scale=2) & disc
ring = disc & ~ndi.binary_erosion(disc, iterations=4)
box = (cx - r - 20, cy - r - 20, cx + r + 21, cy + r + 21)
cut = lambda m: m[box[1]:box[3], box[0]:box[2]]
L = {'stars': cut(stars), 'comet-glow': cut(glow_m), 'window': cut(disc), 'window-edge': cut(ring)}
export('encke-comet', (box[2] - box[0], box[3] - box[1]), L,
       {'paper': [('window-edge', 'faint'), ('comet-glow', 'body'), ('stars', 'ink')],
        'navy': [('window-edge', 'faint'), ('comet-glow', 'body'), ('stars', 'ink')]},
       "\"Encke's Comet, as seen at its re-appearance, 22 Sept 1848\", engraved by J. Basire. "
       'British Library Flickr scan 11034974776 — SOURCE BOOK TO CONFIRM',
       'Stars and glow are the light of the plate, drawn as ink: a star-chart convention, dots on paper.')

# 2 — Earth's orbit round the sun (tonal plate, French labels)
im = Image.open(U + '11243281064_0ea57532e5_o.jpg').crop((178, 138, 1392, 1052))
g = gray(im)
# the plate's print screen beats against any dither: remove it first (blur),
# then keep the drawn lines and globes as a threshold and dither only the glow
soft = ndi.gaussian_filter(g, 3.0)
lines = (g - ndi.gaussian_filter(g, 6)) > 0.10          # fine light lines, labels
globes = soft > np.quantile(soft, .97)
glow = B.ordered(np.clip((soft - np.quantile(soft, .55)) / (np.quantile(soft, .97) - np.quantile(soft, .55)), 0, 1) * .6,
                 gamma=1.4, scale=1)
light = lines | globes | glow
export('earth-orbit', im.size, {'light': light, 'lines': lines | globes, 'glow': glow},
       {'paper': [('light', 'ink')], 'navy': [('light', 'ink')]},
       'Fig. 2, "Orbite de la terre autour du soleil", engraved by M. Rapine. '
       'British Library Flickr scan 11243281064 — SOURCE BOOK TO CONFIRM',
       'Carries French month labels (Janv … Déc). Crop or accept them.')

# 3 — Moon over an observatory ridge (engraving)
im = Image.open(U + '11292565783_0862547ab2_o.jpg').crop((14, 128, 1328, 1105))
n = B.flatten(im, 60)
g = gray(im)
dark = g < 0.42
export('moon-observatory', im.size, {'dark': dark, 'light': ~dark},
       {'paper': [('dark', 'ink')], 'navy': [('light', 'ink')]},
       'Moon and starfield over an observatory on a ridge, 19th-century wood engraving. '
       'British Library Flickr scan 11292565783 — SOURCE BOOK TO CONFIRM',
       'navy preview uses the light layer: stars and moon as ink on the navy ground.')

# 4 — Sun in total eclipse (engraving)
im = Image.open(U + '11300111425_0543ded533_o.jpg').crop((72, 130, 1044, 1110))
g = gray(im)
dark = g < 0.45
export('eclipse', im.size, {'dark': dark, 'light': ~dark},
       {'paper': [('dark', 'ink')], 'navy': [('light', 'ink')]},
       '"Appearance of Sun in an Eclipse", 19th-century engraving. '
       'British Library Flickr scan 11300111425 — SOURCE BOOK TO CONFIRM')

# 5 — Scorpio (al-Sufi tradition), page turned upright
im = Image.open(U + 'DP1.jpg').crop((270, 400, 1790, 1745)).rotate(90, expand=True)
im = im.resize((int(im.width * 1.2), int(im.height * 1.2)), Image.LANCZOS)
L, R, G = E.figure(im, int(60 * E.K * E.K / 2), 0.55)
export('scorpio', im.size, {'lines': L, 'stars': R, 'outside': G},
       {'paper': [('lines', 'ink'), ('outside', 'ink'), ('stars', 'active')],
        'navy': [('lines', 'ink'), ('outside', 'ink'), ('stars', 'active')]},
       'Scorpio, صورة العقرب على ما يُرى في الكرة, al-Sufi tradition. DP1.jpg — SOURCE UNKNOWN, do not publish until found',
       'Page was photographed sideways; turned upright. Four grey stars sit outside the figure.')

m = json.load(open(os.path.join(OUT, 'manifest.json')))
names = {x['name'] for x in MAN}
json.dump([x for x in m if x['name'] not in names] + MAN, open(os.path.join(OUT, 'manifest.json'), 'w'),
          indent=2, ensure_ascii=False)
