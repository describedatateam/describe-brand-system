"""
lockup.py — the wordmark set beside the locked 5a mark.

Alignment rule: the mark's bowl and the wordmark's x-height are the same size.
The mark is scaled so its bowl (outer) = the x-height, its bowl's bottom sits on
the baseline and its sighting rule on the x-height's midline. The mark's d and
the word's d are then the same letter at the same size.

Weights follow the mark's tiers:
  primary  mark (ring 4 / stem 6.8)  with the display wordmark
  compact  mark (ring 7 / stem 12)   with the small-size wordmark
"""
import os
import re
import wordmark as W

MARKS = {
    'primary': dict(ring=4.0, stem=6.8, src=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'brandkit', 'logo', 'logo-5a-primary-light-v1.0.svg')),
    'compact': dict(ring=7.0, stem=12.0, src=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'brandkit', 'logo', 'logo-5a-inverted-light-v1.0.svg')),
}
BOWL_CY, BOWL_R, BOWL_BOTTOM = 128.63, 42.0, 170.63


def mark_body(tier, ink, blue):
    s = open(MARKS[tier]['src']).read()
    s = re.sub(r'<metadata>.*?</metadata>|<title.*?</title>|<desc.*?</desc>', '', s, flags=re.S)
    body = re.search(r'<svg[^>]*>(.*)</svg>', s, re.S).group(1)
    return body.replace('#092052', ink).replace('#0F58E5', blue)


def scale(tier):
    return 100 / (2 * BOWL_R + MARKS[tier]['ring'])


def lockup(tier, parts, width, gap=None, ink=W.INK, blue=W.BLUE, bg=None, accents=None, pad=None, title=''):
    if accents is None:
        accents = '|' if any(c == '|' for c, _ in parts) else '('
    k = scale(tier)
    # mark: translate so bowl centre -> (x, 50) in y-up word space  => SVG y = -50
    # mark extends x from -20..220 (canvas); ink x-range ~ 12..190
    mx0 = 12.0                                     # left ink edge of ring (100-86-2)
    ring_right = 100 + 86 + MARKS[tier]['ring'] / 2  # ring's right extreme ~ 188-190
    gap = 52 if gap is None else gap      # ring to the full stop: half an x-height
    word_x = (ring_right - mx0) * k + gap
    tx, ty = -mx0 * k, -50 - (-BOWL_CY) * k * 1  # svg: y_svg = ty + k*y_mark ; want bowl centre y_mark=128.63 -> -50
    ty = -50 - BOWL_CY * k
    mark = f'<g transform="translate({tx:.2f} {ty:.2f}) scale({k:.4f})">{mark_body(tier, ink, blue)}</g>'
    words = ''.join(f'<path d="{d}" fill="{blue if ch in accents else ink}"/>' for ch, d in parts)
    total = word_x + width
    top = ty + k * (-20 + 10)       # alidade tip region
    top = min(top, -175)
    bottom = ty + k * 192
    pad = 30 if pad is None else pad
    vb = f'{-pad:.1f} {top - pad:.1f} {total + 2 * pad:.1f} {bottom - top + 2 * pad:.1f}'
    rect = f'<rect x="{-pad}" y="{top - pad:.1f}" width="{total + 2 * pad:.1f}" height="{bottom - top + 2 * pad:.1f}" fill="{bg}"/>' if bg else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" role="img" aria-label=".describe(">'
            f'<title>{title}</title>{rect}{mark}<g transform="translate({word_x:.2f} 0)">{words}</g></svg>')
