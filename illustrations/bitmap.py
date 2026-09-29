"""
bitmap.py — turn a manuscript or engraving scan into .describe( 1-bit layers.

Every output is a MASK: a 1-bit PNG where ink = opaque, paper = transparent.
The page colours it (CSS mask-image + background-color), so one file serves
light and dark grounds.

    line_layer(img)   pen and ink → 1 bit (paper tone flattened first)
    dot_layer(img)    the red-gold star dots in al-Sufi → solid discs
    sky_layer(img)    a printed night sky → stars as dots, glow as a
                      45° ordered dither (never random noise)
"""

from __future__ import annotations

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi


def _gray(img):
    return np.asarray(img.convert("L"), dtype=np.float32) / 255.0


def flatten(img, radius=40):
    """Divide out the paper: stains, foxing and page curl become flat white."""
    g = _gray(img)
    bg = np.asarray(img.convert("L").filter(ImageFilter.GaussianBlur(radius)),
                    dtype=np.float32) / 255.0
    return np.clip(g / np.maximum(bg, 1e-3), 0, 1)


def red_mask(img, min_sat=0.22):
    """Pixels that are red/orange ink (the star dots, the rubrics)."""
    a = np.asarray(img.convert("RGB"), dtype=np.float32) / 255.0
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx, mn = a.max(-1), a.min(-1)
    sat = (mx - mn) / np.maximum(mx, 1e-3)
    return (sat > min_sat) & (r > g * 1.18) & (r > b * 1.35) & (r > 0.35)


def line_layer(img, thresh=0.88, exclude=None, min_blob=10, radius=25):
    n = flatten(img, radius)
    m = n < thresh
    if exclude is not None:
        m &= ~ndi.binary_dilation(exclude, iterations=3)
    lab, k = ndi.label(m)
    if k:
        sizes = ndi.sum(m, lab, range(1, k + 1))
        keep = np.zeros(k + 1, bool)
        keep[1:] = sizes >= min_blob
        m = keep[lab]
    return m


def dot_layer(img, min_area=120, max_area=None):
    """al-Sufi's stars → filled discs at the same centre and size."""
    m = ndi.binary_opening(red_mask(img), iterations=2)
    m = ndi.binary_fill_holes(ndi.binary_closing(m, iterations=3))
    lab, k = ndi.label(m)
    out = np.zeros(m.shape, bool)
    yy, xx = np.mgrid[0:m.shape[0], 0:m.shape[1]]
    stars = []
    for i, sl in enumerate(ndi.find_objects(lab), 1):
        area = (lab[sl] == i).sum()
        if area < min_area:
            continue
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if max(h, w) > 1.9 * max(1, min(h, w)):     # a stroke, not a dot (rubric text)
            continue
        if area / float(h * w) < 0.5:               # not disc-like: a letter
            continue
        cy, cx = ndi.center_of_mass(lab[sl] == i)
        cy += sl[0].start
        cx += sl[1].start
        r = (area / np.pi) ** 0.5
        stars.append((cx, cy, r))
        y0, y1 = int(cy - r - 2), int(cy + r + 3)
        x0, x1 = int(cx - r - 2), int(cx + r + 3)
        out[y0:y1, x0:x1] |= (yy[y0:y1, x0:x1] - cy) ** 2 + (xx[y0:y1, x0:x1] - cx) ** 2 <= r * r
    return out, stars


BAYER8 = (np.array([
    [0, 32, 8, 40, 2, 34, 10, 42], [48, 16, 56, 24, 50, 18, 58, 26],
    [12, 44, 4, 36, 14, 46, 6, 38], [60, 28, 52, 20, 62, 30, 54, 22],
    [3, 35, 11, 43, 1, 33, 9, 41], [51, 19, 59, 27, 49, 17, 57, 25],
    [15, 47, 7, 39, 13, 45, 5, 37], [63, 31, 55, 23, 61, 29, 53, 21]]) + .5) / 64


def ordered(tone, gamma=1.6, scale=1):
    """Ordered (Bayer) dither: a regular screen that reads as engraving, not static."""
    h, w = tone.shape
    t = np.tile(np.kron(BAYER8, np.ones((scale, scale))), (h // (8 * scale) + 1, w // (8 * scale) + 1))[:h, :w]
    return tone ** gamma > t


def sky_layer(img, star_delta=0.16, glow_max=0.30, glow_lo=0.35, region=None):
    """A printed night sky (light stars on dark) → star dots + a sparse glow.
    Crop to the sky itself first: paper margins would read as glow.
    region: optional bool mask of where the sky is (e.g. a circular chart)."""
    g = _gray(img)
    base = ndi.grey_opening(g, size=(9, 9))                 # sky without its stars
    stars = (g - base) > star_delta                        # white top-hat
    stars = ndi.binary_opening(stars) | ((g - base) > star_delta * 2.2)
    glow = ndi.gaussian_filter(base, 5)
    lo, hi = np.quantile(glow, glow_lo), np.quantile(glow, .995)
    glow = np.clip((glow - lo) / (hi - lo + 1e-6), 0, 1) * glow_max
    m = stars | ordered(glow, scale=2)
    if region is not None:
        m &= region
    return m


def to_png(mask, path):
    a = (mask * 255).astype(np.uint8)
    Image.fromarray(a, "L").convert("1").save(path, optimize=True)


def compose(layers, size, ground, path):
    """Preview only: [(mask, rgb)] painted in order onto a ground."""
    out = np.zeros((size[1], size[0], 3), np.uint8)
    out[:] = ground
    for m, rgb in layers:
        out[m] = rgb
    Image.fromarray(out).save(path)


def grey_dot_layer(img, thresh=0.62, min_area=60, radius=25):
    """al-Sufi's grey stars — the ones he marks as outside the figure."""
    n = flatten(img, radius)
    m = ndi.binary_opening(n < thresh, iterations=2)
    m = ndi.binary_fill_holes(m)
    lab, k = ndi.label(m)
    out = np.zeros(m.shape, bool)
    for i, sl in enumerate(ndi.find_objects(lab), 1):
        blob = lab[sl] == i
        area = blob.sum()
        h, w = blob.shape
        if area < min_area or max(h, w) > 1.5 * max(1, min(h, w)) or area / float(h * w) < 0.6:
            continue
        out[sl] |= blob
    return out


def dotted(mask, step=4):
    """Re-set a line mask in the stipple language: keep 1 pixel in `step`
    along a diagonal screen, so a drawn line becomes a dotted one."""
    h, w = mask.shape
    yy, xx = np.mgrid[0:h, 0:w]
    return mask & (((xx + yy) % step) == 0) & ((yy % 2) == 0)


def gradient_screen(shape, axis=1, start=0.0, end=0.35, reverse=False):
    """An ordered-dither fade: density ramps across the frame."""
    h, w = shape
    ramp = np.linspace(start, end, w if axis == 1 else h)
    if reverse:
        ramp = ramp[::-1]
    tone = np.tile(ramp, (h, 1)) if axis == 1 else np.tile(ramp[:, None], (1, w))
    return ordered(tone, gamma=1.0, scale=2)
