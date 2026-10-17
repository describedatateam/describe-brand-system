"""Colour maths for the token checks: WCAG contrast, OKLab/OKLCH, and the
Machado, Oliveira & Fernandes (2009) colour-vision-deficiency simulation at
severity 1.0.

Delta E everywhere in this repo is Euclidean distance in OKLab x100, the unit
charts/CHARTS.md §2 already reports in. The CVD thresholds in check.py are
calibrated to this simulation model, so the model is part of the standard.
Standard library only, so the check runs anywhere Python 3 does.
"""
import math

MACHADO = {
    "protan": ((0.152286, 1.052583, -0.204868),
               (0.114503, 0.786281, 0.099216),
               (-0.003882, -0.048116, 1.051998)),
    "deutan": ((0.367322, 0.860646, -0.227968),
               (0.280085, 0.672501, 0.047413),
               (-0.011820, 0.042940, 0.968881)),
    "tritan": ((1.255528, -0.076749, -0.178779),
               (-0.078411, 0.930809, 0.147602),
               (0.004733, 0.691367, 0.303900)),
}


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def rgb_hex(rgb):
    return "#" + "".join(f"{round(max(0, min(1, c)) * 255):02X}" for c in rgb)


def s2lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lin2s(c):
    c = max(0.0, min(1.0, c))
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def lin(h):
    return tuple(s2lin(c) for c in hex_rgb(h))


def luminance(h):
    r, g, b = lin(h)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def _oklab_lin(rgb):
    r, g, b = rgb
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)


def oklab(h):
    return _oklab_lin(lin(h))


def oklch(h):
    L, a, b = oklab(h)
    return L, math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360


def from_oklch(L, C, H):
    """OKLCH -> hex, reducing chroma until the colour is inside sRGB."""
    for _ in range(60):
        a, b = C * math.cos(math.radians(H)), C * math.sin(math.radians(H))
        l_ = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
        m_ = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
        s_ = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
        rgb = (4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_,
               -1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_,
               -0.0041960863 * l_ - 0.7034186147 * m_ + 1.7076147010 * s_)
        if all(-1e-4 <= c <= 1 + 1e-4 for c in rgb):
            return rgb_hex(tuple(lin2s(c) for c in rgb))
        C *= 0.97
    return rgb_hex(tuple(lin2s(c) for c in rgb))


def _simulate(h, kind):
    r, g, b = lin(h)
    return tuple(max(0.0, min(1.0, row[0] * r + row[1] * g + row[2] * b))
                 for row in MACHADO[kind])


def delta_e(h1, h2, kind=None):
    """OKLab Delta E x100; kind None is unsimulated (normal) vision."""
    a = _oklab_lin(_simulate(h1, kind) if kind else lin(h1))
    b = _oklab_lin(_simulate(h2, kind) if kind else lin(h2))
    return 100 * math.dist(a, b)


def delta_e_cvd(h1, h2):
    """Worst of protan and deutan: the pair as a colour-blind reader sees it."""
    return min(delta_e(h1, h2, "protan"), delta_e(h1, h2, "deutan"))
