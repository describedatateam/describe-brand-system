"""
wordmark.py — .describe( wordmark studies, drawn as real vector outlines.

Three directions, all lowercase, all set beside the locked 5a mark:

  A  CONSTRUCTED  monoline letters built from the mark's own parts:
                  circular bowls, tangent stems, the bowl's horizontal
                  diameter as the e's bar, apertures set by the sight angle
                  θ = 40.6°, round terminals like the mark's strokes.
  B  HOUSE SANS   Readex Pro (the brand's interface face) as outlines,
                  spaced for display, the leading dot at the mark's ratio.
  C  HOUSE SERIF  Fraunces 300 (the brand's heading face) as outlines.

Every glyph is a filled path (no strokes, no live text), so the SVGs are
master artwork. Units: x-height = 100, y up; flipped to SVG on output.

    python3 wordmark.py      → out/*.svg + out/sheet.html
"""
import math
import os

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

OUT = 'out'
THETA = 40.6          # the mark's sight angle (degrees)
S_STRETCH = 1.27      # the s's horizontal stretch (width ≈ 0.72 of a bowl)
INK, BLUE = '#092052', '#0F58E5'


# ---------------------------------------------------------------- geometry
def P(x, y):
    return f'{x:.2f} {-y:.2f}'            # y-up → SVG y-down


def pt(cx, cy, r, a):
    a = math.radians(a)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def arc_band(cx, cy, r, a0, a1, w, caps=True, cap0=None, cap1=None):
    """Annular sector, centreline radius r, from a0 to a1 (ccw, degrees), thickness w.
    Contour runs counter-clockwise on screen so overlapping shapes union under nonzero."""
    ro, ri, h = r + w / 2, r - w / 2, w / 2
    large = 1 if (a1 - a0) % 360 > 180 else 0
    o0, o1 = pt(cx, cy, ro, a0), pt(cx, cy, ro, a1)
    i0, i1 = pt(cx, cy, ri, a0), pt(cx, cy, ri, a1)
    # in y-down SVG, ccw in y-up maths == sweep-flag 0
    d = f'M{P(*o0)}A{ro:.2f} {ro:.2f} 0 {large} 0 {P(*o1)}'
    c0 = caps if cap0 is None else cap0
    c1 = caps if cap1 is None else cap1
    d += f'A{h:.2f} {h:.2f} 0 0 0 {P(*i1)}' if c1 else f'L{P(*i1)}'
    d += f'A{ri:.2f} {ri:.2f} 0 {large} 1 {P(*i0)}'
    d += f'A{h:.2f} {h:.2f} 0 0 0 {P(*o0)}Z' if c0 else 'Z'
    return d


def ell_band(cx, cy, rx, ry, t0, t1, w):
    """Elliptical arc band (parametric angles t0→t1, ccw), constant-ish width w:
    the offset curves are approximated by ellipses rx±w/2, ry±w/2 (exact on the axes,
    within a few % between them at this eccentricity). Round caps."""
    h = w / 2
    def e(rx_, ry_, t):
        a = math.radians(t)
        return cx + rx_ * math.cos(a), cy + ry_ * math.sin(a)
    large = 1 if (t1 - t0) % 360 > 180 else 0
    o0, o1 = e(rx + h, ry + h, t0), e(rx + h, ry + h, t1)
    i0, i1 = e(rx - h, ry - h, t0), e(rx - h, ry - h, t1)
    d = f'M{P(*o0)}A{rx + h:.2f} {ry + h:.2f} 0 {large} 0 {P(*o1)}'
    d += f'A{h:.2f} {h:.2f} 0 0 0 {P(*i1)}'
    d += f'A{rx - h:.2f} {ry - h:.2f} 0 {large} 1 {P(*i0)}'
    d += f'A{h:.2f} {h:.2f} 0 0 0 {P(*o0)}Z'
    return d


def ring(cx, cy, r, w):
    ro, ri = r + w / 2, r - w / 2
    return (f'M{P(cx + ro, cy)}A{ro:.2f} {ro:.2f} 0 1 0 {P(cx - ro, cy)}A{ro:.2f} {ro:.2f} 0 1 0 {P(cx + ro, cy)}Z'
            f'M{P(cx + ri, cy)}A{ri:.2f} {ri:.2f} 0 1 1 {P(cx - ri, cy)}A{ri:.2f} {ri:.2f} 0 1 1 {P(cx + ri, cy)}Z')


def stem(x, y0, y1, w, round0=True, round1=True):
    """Vertical stroke on centreline x from y0 to y1 (centreline ends), round or flat ends."""
    h = w / 2
    d = f'M{P(x - h, y1)}L{P(x - h, y0)}'
    d += f'A{h:.2f} {h:.2f} 0 0 0 {P(x + h, y0)}' if round0 else f'L{P(x + h, y0)}'
    d += f'L{P(x + h, y1)}'
    d += f'A{h:.2f} {h:.2f} 0 0 0 {P(x - h, y1)}Z' if round1 else 'Z'
    return d


def bar(x0, x1, y, w):
    h = w / 2
    return f'M{P(x0, y + h)}L{P(x0, y - h)}L{P(x1, y - h)}L{P(x1, y + h)}Z'


def disc(cx, cy, r):
    return f'M{P(cx + r, cy)}A{r:.2f} {r:.2f} 0 1 0 {P(cx - r, cy)}A{r:.2f} {r:.2f} 0 1 0 {P(cx + r, cy)}Z'


# ---------------------------------------------------------- A: constructed
def constructed(w=13.0, asc=1.736, dot_ratio=1.4, idot=0.8):
    """Returns list of (glyph, path, advance, is_accent) laid out left to right.
    asc: ascender height as a multiple of x-height (the mark's own d is 1.77)."""
    rc = (100 - w) / 2                     # bowl centreline radius
    top = 100 * asc - w / 2                # ascender centreline end
    h = w / 2
    G = {}
    # each glyph: (path_fn(x) -> d, width) with x = left edge of ink
    G['.'] = (lambda x: disc(x + dot_ratio * w, dot_ratio * w, dot_ratio * w), 2 * dot_ratio * w)
    G['d'] = (lambda x: ring(x + h + rc, 50, rc, w) + stem(x + h + 2 * rc, h, top, w), 2 * rc + w)
    G['b'] = (lambda x: ring(x + h + rc, 50, rc, w) + stem(x + h, h, top, w), 2 * rc + w)
    # e: the bar is the bowl's horizontal diameter (as the mark's sighting rule);
    # the aperture runs from the bar down to the sight angle
    G['e'] = (lambda x: arc_band(x + h + rc, 50, rc, 0, 360 - THETA, w, cap0=False)
              + bar(x + h, x + h + 2 * rc, 50, w), 2 * rc + w)
    # c: aperture of 2θ, centred on the horizontal
    G['c'] = (lambda x: arc_band(x + h + rc, 50, rc, THETA, 360 - THETA, w), 2 * rc + w)
    # s: two equal circles joined by a straight spine on their internal tangent
    # (a drafting construction), then widened by an affine stretch f, which keeps
    # the spine tangent; stroked at constant width. Terminals on the sight angle.
    span = 100 - w
    rho, e, f = 0.232 * span, 0.035 * span, S_STRETCH
    s_w = f * (2 * e + 2 * rho) + w

    def s_glyph(x):
        cx = x + s_w / 2
        U, L = (-e, 100 - h - rho), (e, h + rho)          # circle space, x relative to cx
        mx, my = -U[0], (U[1] + L[1]) / 2 - U[1]
        d = math.hypot(mx, my)
        base, beta = math.degrees(math.atan2(my, mx)), math.degrees(math.acos(rho / d))
        a_u = (base - beta) % 360
        tu = pt(U[0], U[1], rho, a_u)
        tl = pt(L[0], L[1], rho, a_u - 180)
        tu, tl = (cx + f * tu[0], tu[1]), (cx + f * tl[0], tl[1])
        ang = math.atan2(tl[1] - tu[1], tl[0] - tu[0])
        nx, ny = -math.sin(ang) * h, math.cos(ang) * h
        spine = (f'M{P(tu[0] + nx, tu[1] + ny)}L{P(tu[0] - nx, tu[1] - ny)}'
                 f'L{P(tl[0] - nx, tl[1] - ny)}L{P(tl[0] + nx, tl[1] + ny)}Z')
        # parametric angles on the stretched ellipses equal the circle-space angles
        return (ell_band(cx + f * U[0], U[1], f * rho, rho, THETA, a_u if a_u > THETA else a_u + 360, w)
                + ell_band(cx + f * L[0], L[1], f * rho, rho, THETA - 180, a_u - 180, w) + spine)
    G['s'] = (s_glyph, s_w)
    rr = rc * 0.78
    G['r'] = (lambda x: stem(x + h, h, 100 - h, w)
              + arc_band(x + h + rr, 100 - h - rr, rr, 90 - THETA + 25, 180, w), h + rr * (1 + math.cos(math.radians(90 - THETA + 25))) + h)
    G['i'] = (lambda x: stem(x + h, h, 100 - h, w) + disc(x + h, 100 + 1.3 * w + idot * w, idot * w), w if idot * 2 <= 1 else 2 * idot * w)
    # the bracket: a long, shallow arc; its curvature is the ring's, relative to the bowl
    bh = (100 * asc + 32) / 2              # half-height, descender −32 to the ascender
    R = 190
    half = math.degrees(math.asin((bh - h) / R))
    bx = R * (1 - math.cos(math.radians(half)))
    G['('] = (lambda x: arc_band(x + h + R, 100 * asc - bh, R, 180 - half, 180 + half, w), bx + w)
    cw = 1.4 * w
    G['|'] = (lambda x: stem(x + cw / 2, -32 + cw / 2, 100 * asc - cw / 2, cw), cw)
    return G


# spacing, in x-height units, between ink of neighbours (round|straight sides)
SIDE = {'.': ('r', 'r'), 'd': ('r', 's'), 'e': ('r', 'r'), 's': ('r', 'r'), 'c': ('r', 'r'),
        'r': ('s', 'r'), 'i': ('s', 's'), 'b': ('s', 'r'), '(': ('r', 'r'), '|': ('s', 's')}
GAP = {('r', 'r'): 13, ('r', 's'): 17, ('s', 'r'): 17, ('s', 's'): 22}


PAIR = {'.d': 9, 'de': 11, 'es': 11, 'sc': 11, 'cr': 8, 'ri': 13, 'ib': 17, 'be': 11, 'e(': 10, '(|': 22}


def layout(text='.describe(|', **kw):
    """(glyph, left x, width) for each glyph, using the same spacing as set_constructed."""
    G = constructed(**kw)
    x, out = 0.0, []
    for i, ch in enumerate(text):
        wd = G[ch][1]
        out.append((ch, x, wd))
        if i + 1 < len(text):
            nxt = text[i + 1]
            x += wd + PAIR.get(ch + nxt, GAP[(SIDE[ch][1], SIDE[nxt][0])])
    return out


def set_constructed(text='.describe(', **kw):
    G = constructed(**kw)
    x, parts = 0.0, []
    for i, ch in enumerate(text):
        fn, wd = G[ch]
        parts.append((ch, fn(x)))
        if i + 1 < len(text):
            nxt = text[i + 1]
            gap = PAIR.get(ch + nxt, GAP[(SIDE[ch][1], SIDE[nxt][0])])
            x += wd + gap
    return parts, x + G[text[-1]][1]


# ------------------------------------------------------------- B, C: fonts
def set_font(path, text='.describe(', tracking=0.0, dot_scale=1.0):
    f = TTFont(path)
    gs, cmap, hmtx = f.getGlyphSet(), f.getBestCmap(), f['hmtx']
    xh = f['OS/2'].sxHeight
    s = 100 / xh
    x, parts = 0.0, []
    for ch in text:
        g = cmap[ord(ch)]
        pen = SVGPathPen(gs)
        k = dot_scale if ch == '.' else 1
        # the full stop scales about its origin on the baseline, advance and all
        tp = TransformPen(pen, (s * k, 0, 0, -s * k, x, 0))
        gs[g].draw(tp)
        parts.append((ch, pen.getCommands()))
        x += hmtx[g][0] * s * (dot_scale if ch == '.' else 1) + tracking
    return parts, x


# ------------------------------------------------------------------ output
def svg(parts, width, colour=True, pad=20, asc=170, desc=45, fg=INK, accent=BLUE, bg=None, title='', accents='('):
    vb = f'{-pad:.1f} {-asc - pad:.1f} {width + 2 * pad:.1f} {asc + desc + 2 * pad:.1f}'
    body = ''.join(f'<path d="{d}" fill="{accent if (colour and ch in accents) else fg}"/>' for ch, d in parts)
    rect = f'<rect x="{-pad}" y="{-asc - pad}" width="{width + 2 * pad}" height="{asc + desc + 2 * pad}" fill="{bg}"/>' if bg else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" role="img" aria-label=".describe(">'
            f'<title>{title}</title>{rect}<g fill-rule="nonzero">{body}</g></svg>')


def main():
    os.makedirs(OUT, exist_ok=True)
    sets = {
        'A-constructed': set_constructed(w=14, dot_ratio=1.2),
        'A-caret': set_constructed('.describe(|', w=14, dot_ratio=1.2),
        'A-small': set_constructed('.describe(|', w=18, dot_ratio=1.2),
        'B-readex': set_font('readex500.ttf', tracking=-2, dot_scale=1.35),
        'C-fraunces': set_font('fraunces300.ttf', tracking=-1),
    }
    for k, (parts, wd) in sets.items():
        acc = '|' if any(c == '|' for c, _ in parts) else '('
        open(f'{OUT}/{k}.svg', 'w').write(svg(parts, wd, title=f'.describe( wordmark study {k}', accents=acc))
        open(f'{OUT}/{k}-ink.svg', 'w').write(svg(parts, wd, colour=False, title=f'{k} one colour'))
        open(f'{OUT}/{k}-reversed.svg', 'w').write(svg(parts, wd, fg='#F6F8FC', accent='#4F86F7', bg='#092052', title=f'{k} reversed', accents=acc))
        print(k, round(wd, 1))
    return sets


if __name__ == '__main__':
    main()
