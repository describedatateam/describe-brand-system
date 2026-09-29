"""build_study.py — the wordmark study page (study.html) from final/*.svg."""
import math, re
import wordmark as W
import lockup as L
from build_wordmark import word, stacked

F = 'final/'


def themable(svg):
    """Swap the literal brand colours for page tokens so a figure follows the page theme."""
    return (svg.replace('#092052', 'var(--ink)').replace('#0F58E5', 'var(--active)')
               .replace('fill="#F6F8FC"', 'fill="var(--ground)"'))


def construction():
    """The primary lockup with its construction shown: guides, bowl circles, θ rays."""
    tier = 'primary'
    (parts, wd), w = word(tier)
    base = L.lockup(tier, parts, wd, title='.describe( wordmark, construction', pad=60)
    vb = re.search(r'viewBox="([^"]+)"', base).group(1)
    x0, y0, vw, vh = map(float, vb.split())
    vw += 190                                   # a right margin for the guide labels
    base = base.replace(f'viewBox="{vb}"', f'viewBox="{x0} {y0} {vw} {vh}"')
    k = L.scale(tier)
    word_x = (100 + 86 + L.MARKS[tier]['ring'] / 2 - 12.0) * k + 52
    g = []
    guides = [(0, 'BASELINE'), (-100, 'X-HEIGHT'), (-173.6, 'ASCENDER'), (32, 'DESCENDER')]
    for y, lab in guides:
        g.append(f'<line x1="{x0 + 10:.1f}" x2="{x0 + vw - 190:.1f}" y1="{y}" y2="{y}" class="g-line"/>')
        g.append(f'<text x="{x0 + vw - 178:.1f}" y="{y + 4}" class="g-lab">{lab}</text>')
    rc = (100 - w) / 2
    h = w / 2
    for ch, x, gw in W.layout('.describe(|', w=w, dot_ratio=1.4):
        X = word_x + x
        if ch in 'debc':
            cx = X + h + rc
            g.append(f'<circle cx="{cx:.1f}" cy="-50" r="{rc:.1f}" class="g-circ"/>')
            if ch in 'ec':
                for a in ((-W.THETA, W.THETA) if ch == 'c' else (-W.THETA,)):
                    ex, ey = cx + (rc + 34) * math.cos(math.radians(a)), -50 - (rc + 34) * math.sin(math.radians(a))
                    g.append(f'<line x1="{cx:.1f}" y1="-50" x2="{ex:.1f}" y2="{ey:.1f}" class="g-ray"/>')
    # the mark's bowl, drawn on the same circle size as the word's bowls
    bx = (66.59 - 12.0) * k
    g.append(f'<circle cx="{bx:.1f}" cy="-50" r="{42 * k:.1f}" class="g-circ g-hot"/>')
    overlay = '<g class="constr">' + ''.join(g) + '</g>'
    return themable(base.replace('</svg>', overlay + '</svg>'))


def page():
    (pp, pw), wp = word('primary')
    (cp, cw), wc = word('compact')
    hero = themable(open(F + 'lockup-horizontal-primary-light.svg').read())
    lock = {n: open(F + n + '.svg').read() for n in [
        'lockup-horizontal-primary-light', 'lockup-horizontal-primary-dark', 'lockup-horizontal-primary-ink',
        'lockup-stacked-primary-light', 'lockup-stacked-compact-dark', 'lockup-horizontal-compact-light',
        'wordmark-primary-light', 'wordmark-compact-light', 'alt-B-readex', 'alt-C-fraunces']}
    sizes_c = ''.join(f'<figure class="sz"><div style="height:{h}px">{lock["lockup-horizontal-compact-light"]}</div><figcaption>{h}px</figcaption></figure>' for h in (48, 32, 24, 20))
    sizes_p = ''.join(f'<figure class="sz"><div style="height:{h}px">{lock["lockup-horizontal-primary-light"]}</div><figcaption>{h}px</figcaption></figure>' for h in (96, 64, 48))
    tpl = open('study_template.html').read()
    for key, val in {'HERO': hero, 'CONSTR': construction(),
                     'H_LIGHT': lock['lockup-horizontal-primary-light'], 'H_DARK': lock['lockup-horizontal-primary-dark'],
                     'H_INK': lock['lockup-horizontal-primary-ink'], 'S_LIGHT': lock['lockup-stacked-primary-light'],
                     'S_DARK': lock['lockup-stacked-compact-dark'], 'W_PRIMARY': themable(lock['wordmark-primary-light']),
                     'W_COMPACT': themable(lock['wordmark-compact-light']), 'SIZES_C': sizes_c, 'SIZES_P': sizes_p,
                     'ALT_B': lock['alt-B-readex'], 'ALT_C': lock['alt-C-fraunces']}.items():
        tpl = tpl.replace('{{' + key + '}}', val)
    assert '{{' not in tpl
    open('study.html', 'w').write(tpl)
    print('study.html', len(tpl) // 1024, 'KB')


if __name__ == '__main__':
    import build_wordmark
    build_wordmark.parts_w = {}
    page()
