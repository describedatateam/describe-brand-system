"""
build_wordmark.py — the .describe( wordmark set (direction A, constructed), plus
the two alternates for comparison.

    python3 build_wordmark.py   → final/*.svg

Tiers (paired with the mark's tiers):
  primary  letters w = the primary mark's stem at lockup scale (6.8 × k)
  compact  letters w = the compact mark's stem at lockup scale (12 × k)
The caret is the mark's blue stem: 1.7 × the letter stroke, like the mark's stem to its ring.
"""
import os
import re
import wordmark as W
import lockup as L

OUT = 'final'
LIGHT = dict(ink='#092052', blue='#0F58E5', bg=None)
DARK = dict(ink='#F6F8FC', blue='#4F86F7', bg='#092052')
INK1 = dict(ink='#092052', blue='#092052', bg=None)
THEMES = {'light': LIGHT, 'dark': DARK, 'ink': INK1}


def word(tier):
    k = L.scale(tier)
    w = 10.0 if tier == 'primary' else 15.0      # tuned for legibility; see the study notes
    return W.set_constructed('.describe(|', w=w, dot_ratio=1.4 if tier == 'primary' else 1.25), w


def stacked(tier, parts, width, ink, blue, bg=None, title=''):
    """Mark centred above the word at twice the horizontal lockup's scale: there the
    mark's ring matches the letters' stroke and its stem matches the caret."""
    k = 2 * L.scale(tier)     # ring ≈ letter stroke, stem ≈ caret (within ~10%)
    ring = L.MARKS[tier]['ring']
    # mark ink box in its own units: x 12..190 (ring), y ~ 8..188 (alidade tip to ring bottom)
    x0, x1, y0, y1 = 12.0, 186 + ring / 2, 8.0, 186 + ring / 2
    mw, mh = (x1 - x0) * k, (y1 - y0) * k
    asc_top = 100 * 1.736
    gap = 90
    mx = width / 2 - mw / 2 - x0 * k
    my = -(asc_top + gap) - mh - y0 * k
    mark = f'<g transform="translate({mx:.2f} {my:.2f}) scale({k:.4f})">{L.mark_body(tier, ink, blue)}</g>'
    words = ''.join(f'<path d="{d}" fill="{blue if ch == "|" else ink}"/>' for ch, d in parts)
    top = my + y0 * k
    pad = 40
    vb = f'{-pad} {top - pad:.1f} {width + 2 * pad:.1f} {45 - top + 2 * pad:.1f}'
    rect = f'<rect x="{-pad}" y="{top - pad:.1f}" width="{width + 2 * pad:.1f}" height="{45 - top + 2 * pad:.1f}" fill="{bg}"/>' if bg else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" role="img" aria-label=".describe(">'
            f'<title>{title}</title>{rect}{mark}{words}</svg>')


parts_w = {}

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for tier in ('primary', 'compact'):
        (parts, wd), w = word(tier)
        parts_w[tier] = w
        for th, c in THEMES.items():
            acc = '|'
            open(f'{OUT}/wordmark-{tier}-{th}.svg', 'w').write(
                W.svg(parts, wd, fg=c['ink'], accent=c['blue'], bg=c['bg'], accents=acc,
                      title=f'.describe( wordmark, {tier}, {th}'))
            open(f'{OUT}/lockup-horizontal-{tier}-{th}.svg', 'w').write(
                L.lockup(tier, parts, wd, ink=c['ink'], blue=c['blue'], bg=c['bg'],
                         title=f'.describe( lockup, horizontal, {tier}, {th}'))
            open(f'{OUT}/lockup-stacked-{tier}-{th}.svg', 'w').write(
                stacked(tier, parts, wd, c['ink'], c['blue'], c['bg'], title=f'.describe( lockup, stacked, {tier}, {th}'))
    # alternates, for the study only
    for name, (parts, wd) in {'alt-B-readex': W.set_font('readex300.ttf', text='.describe(', tracking=-1, dot_scale=1.3),
                              'alt-C-fraunces': W.set_font('fraunces300.ttf', text='.describe(', tracking=-1)}.items():
        open(f'{OUT}/{name}.svg', 'w').write(L.lockup('primary', parts, wd, title=name))
    print(sorted(os.listdir(OUT)))
