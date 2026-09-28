"""
graphics.py — the phase-2 graphics system for the .describe( homepage.

Every graphic is inline SVG painted by semantic classes (ink, body, faint,
active, gap) that the page maps to its theme tokens, so light, dark and
single-ink are the same drawing. No hex here.

Devices (see inspo/INSPO.md):
  hero_rows(v)     the source file as a ruler, with a vernier on what was set aside
  tally(n)         section index: n of 8, counted
  wedges(n, h)     a cuneiform-style count for small real numbers (0-9)

Rulers are drawn with percentage x and pixel y, so they stretch to the
column while type and strokes keep their true size.

Deliberate departure from INSPO.md (accepted by the visual agent, round 1):
wedges are NOT used for "4 days" / "2 revisions" in Services. There the three
service columns share one figure-over-label row; wedges stay in Method and
"Where we are", where a count is the whole point.
"""
import json
import sys

sys.path.insert(0, '/home/claude/geometry')
sys.path.insert(0, '/home/claude/website/inspo')
from astrolabe import W_HAIR, W_MARK, W_RING, tally_progress  # noqa: E402
from sketches import wedge_number  # noqa: E402

U = json.load(open('/home/claude/decisions/uci_audit.json'))
ROWS = U['rows']
CLEAN = U['clean_sale_lines']
PARTS = [(U['duplicates'], 'Exact duplicates'),
         (U['cancellation_lines'], 'Cancellations netted'),
         (U['nonproduct_lines'], 'Postage and fees'),
         (U['zero_or_negative_lines'], 'Zero or negative')]
ASIDE = ROWS - CLEAN
assert sum(n for n, _ in PARTS) == ASIDE, 'hero ruler does not reconcile'


def P(v):
    """A fraction of the rule as an SVG percentage."""
    return f'{v * 100:.3f}%'.replace('.000%', '%')


def ln(x0, y0, x1, y1, cls, w=W_HAIR, dash=False):
    d = ' stroke-dasharray="3 4"' if dash else ''
    return (f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" class="{cls}" '
            f'stroke-width="{w}"{d}/>')


def tx(x, y, s, cls, anchor='start', dx=None):
    d = f' dx="{dx}"' if dx is not None else ''
    return f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}"{d}>{s}</text>'


def label(x, y, s, anchor='start', dx=None, cls='body'):
    """Mono label: uppercase, <= 11px, four words or fewer."""
    assert len(s.split()) <= 4, s
    return tx(x, y, s.upper(), f'mo {cls}', anchor, dx)


def fig(x, y, s, anchor='middle', cls='ink'):
    return tx(x, y, s, f'fr {cls}', anchor)


# ---------------------------------------------------------------- hero ruler pair
# Round 5 (founder): the two rulers read alone. The main rule, then an EMPTY
# magnifier zone crossed only by two dashed projections that stop 8px short,
# then the vernier across the full column, so its scale is the true ratio
# rows / set-aside at every width. Values sit left-aligned at each segment's
# start, with no leaders. Vertical metrics (px) follow inspo/direction-r5.md:
#   tick labels 8px+ above the tick tops; labels >= 8px from any rule;
#   vernier label row 12px above its rule; values 24px below it (T5 figures).
SCALE = ROWS / ASIDE                       # the vernier spans the column: 28.02
assert abs(SCALE - round(SCALE)) < 0.05, 'scale is not a whole number; label it with a decimal'
CAP_MO, CAP_FR = 0.70, 0.70                # cap height / font size (Plex Mono, Fraunces)


def hero_rows(v):
    """v='d' (>= 1200px): one row of values. v='m': numbered 2x2 grid of values."""
    mobile = v == 'm'
    Y = 48                                  # main rule (4px stroke: 46-50)
    xc = CLEAN / ROWS
    o = []
    for val in range(0, ROWS + 1, 20000):
        x = P(val / ROWS)
        major = val % 100000 == 0
        o.append(ln(x, Y - 4, x, Y - (14 if major else 8), 'body' if major else 'faint'))
        if major:   # label baseline 24: 10px clear of the tallest tick (top at 34)
            o.append(label(x, 24, f'{val // 1000}K' if val else '0', 'start' if not val else 'middle'))
    o.append(ln('0', Y, P(xc), Y, 'ink', W_RING))
    o.append(ln(P(xc), Y, '100%', Y, 'body', W_RING))
    acc = CLEAN
    for n, _ in PARTS[:-1]:
        acc += n
        o.append(ln(P(acc / ROWS), Y - 2.5, P(acc / ROWS), Y + 2.5, 'gap', 1))
    o.append(ln('100%', Y - 10, '100%', Y + 10, 'body'))
    # the magnifier zone: empty except for two dashed projections, each 8px short of what it joins
    ZONE = 80 if mobile else 112
    zt = Y + 2 + ZONE                       # top of the vernier's label row (cap top)
    lab_y = zt + round(10.5 * CAP_MO)       # its baseline
    VY = lab_y + 12 + 2                     # vernier rule centre: 12px under the label row
    o.append(ln(P(xc), Y + 8 + 8, '0', zt - 8, 'proj', W_HAIR, dash=True))   # index tick ends at Y+8
    o.append(ln('100%', Y + 10 + 8, '100%', zt - 8, 'proj', W_HAIR, dash=True))
    # the vernier: the tail at full column width; end ticks rise to its label row
    spans, x = [], 0.0
    for n, _ in PARTS:
        w = n / ASIDE
        spans.append((x, x + w))
        o.append(ln(P(x), VY, P(x + w), VY, 'body', W_RING))
        x += w
    for a_, _ in spans[1:]:
        o.append(ln(P(a_), VY - 2, P(a_), VY + 2 + 8, 'body'))           # segment ticks drop 8px
    o.append(ln('0', zt, '0', VY + 10, 'body'))
    o.append(ln('100%', zt, '100%', VY + 10, 'body'))
    o.append(label('0', lab_y, f'{ASIDE:,} set aside', 'start', 8))
    o.append(label('100%', lab_y, f'Scale ×{SCALE:.0f}', 'end', -8))
    # the one active reading, drawn last: where clean data ends
    o.append(ln(P(xc), Y - 18, P(xc), Y + 8, 'active', W_MARK))
    o.append(f'<circle cx="{P(xc)}" cy="{Y}" r="4.2" class="active fill"/>')
    rb = VY + 2                              # vernier rule bottom
    if mobile:
        idx_y = rb + 8 + 7                   # index 1-4 under each segment, 8px clear of the rule
        for i, (a_, b_) in enumerate(spans):
            o.append(label(P((a_ + b_) / 2), idx_y, str(i + 1), 'middle', cls='ink'))
        fcap = round(21 * CAP_FR)
        r1 = idx_y + 14 + fcap               # T5: 12px clear under the index row (+2 for glyph overshoot)
        r2 = r1 + 4 + 8 + 7 + 14 + fcap      # comma descent, own label 8px, label, 12px clear (+2)
        for i, ((n, name), (cx, ry)) in enumerate(zip(PARTS, [('0', r1), ('45%', r1), ('0', r2), ('45%', r2)])):
            o.append(label(cx, ry, str(i + 1), cls='ink'))
            o.append(tx(cx, ry, '−' + f'{n:,}', 'fr ink', 'start', 16))
            o.append(label(cx, ry + 4 + 8 + 7, name, dx=16))
        H = r2 + 4 + 8 + 7 + 3
    else:
        vy = rb + 24 + round(26 * CAP_FR)    # values: cap top 24px under the vernier
        for (n, name), (a_, _) in zip(PARTS, spans):
            o.append(fig(P(a_), vy, '−' + f'{n:,}', 'start'))
            o.append(label(P(a_), vy + 5 + 8 + 7, name))                  # comma descent + 8px own label
        H = vy + 5 + 8 + 7 + 3
    return (f'<svg class="gx hr hr--{v}" width="100%" height="{H}" aria-hidden="true" '
            f'focusable="false">{"".join(o)}</svg>')


# ---------------------------------------------------------------- findings as rulers
def _rule(o, y, parts, total):
    """A straight rule of `total`, with `parts` [(value, cls, weight)] laid end to end."""
    x = 0.0
    for val, cls, w in parts:
        o.append(ln(P(x / total), y, P((x + val) / total), y, cls, w))
        x += val
    o.append(ln('0', y - 5, '0', y + 5, 'body'))
    o.append(ln('100%', y - 5, '100%', y + 5, 'body'))


def finding_rule(kind):
    o = []
    if kind == 'half':
        # one rule of the 4,284 identified customers, ranked by revenue; the top 234 in ink
        k, n = U['customers_for_half'], U['customers_known']
        _rule(o, 14, [(k, 'ink', W_RING), (n - k, 'body', W_HAIR)], n)
        o.append(ln(P(k / n), 9, P(k / n), 19, 'ink'))
        o.append(label(P(k / n), 35, 'Half the revenue', 'start', 6))
        o.append(label('100%', 35, f'{n:,} customers', 'end'))
    elif kind == 'jan':
        # January as counted, and the cancelled order it would have carried if left in
        j = U['monthly_net_gbp']['2011-01']
        f = U['flagged_lines'][0]['val']
        _rule(o, 14, [(j, 'ink', W_RING), (f, 'body', W_HAIR)], j + f)
        o.append(ln(P(j / (j + f)), 9, P(j / (j + f)), 19, 'ink'))
        o.append(label('0', 35, 'January, net'))
        o.append(label('100%', 35, f'+{f / j * 100:.0f}% if left in', 'end'))
    elif kind == 'window':
        # the hero's clean total, reconciled to the chart's n: the partial December is set aside
        w, out = U['window_sale_lines'], U['window_left_out_sale_lines']
        assert w + out == CLEAN
        # one row above the rule (the set-aside tail, at its end) and one below (the window, the total);
        # every label 8px+ clear of the rule and its end ticks. Phones get the short wording.
        _rule(o, 24, [(w, 'ink', W_RING), (out, 'body', W_RING)], CLEAN)
        o.append(ln(P(w / CLEAN), 19, P(w / CLEAN), 29, 'gap', 2))
        o.append(label('100%', 9, f'−{out:,} Dec 2011, partial', 'end'))
        for cls, left, right in (('wide', f'{w:,} in the window', f'{CLEAN:,} clean lines'),
                                 ('narrow', f'{w:,} in window', f'of {CLEAN:,} clean')):
            o.append(f'<g class="{cls}">' + label('0', 45, left) + label('100%', 45, right, 'end') + '</g>')
        return (f'<svg class="gx frule frule--window" width="100%" height="50" aria-hidden="true" '
                f'focusable="false">{"".join(o)}</svg>')
    else:
        # missing customer ID, as a share of the same net revenue the chart shows
        sh = U['window_missing_customer_net_share']
        _rule(o, 14, [(sh, 'ink', W_RING), (1 - sh, 'body', W_HAIR)], 1)
        o.append(ln(P(sh), 9, P(sh), 19, 'ink'))
        o.append(label('0', 35, 'No customer ID'))
        o.append(label('100%', 35, 'Net revenue', 'end'))
    return (f'<svg class="gx frule frule--{kind}" width="100%" height="40" aria-hidden="true" '
            f'focusable="false">{"".join(o)}</svg>')


HERO_DESC = (f'The source file as a ruler: {ROWS:,} rows, of which {CLEAN:,} are clean sale lines. '
             f'The {ASIDE:,} rows set aside are magnified: '
             + ', '.join(f'{n:,} {name.lower()}' for n, name in PARTS) + '.')


# ---------------------------------------------------------------- section tally
def tally(n, total=8):
    body = tally_progress(n, total, 1.5, 1, 16, 7, 9)
    w = 7 * (total - 1) + 9 * ((total - 1) // 5) + 3
    return (f'<svg class="gx tally" viewBox="0 0 {w} 18" width="{w}" height="18" '
            f'aria-hidden="true" focusable="false">{body}</svg>')


# ---------------------------------------------------------------- wedge counts
def wedges(n, h=34):
    """Units only (0-9), always set beside its numeral; zero is the empty place."""
    assert 0 <= n <= 9, 'wedges are for 0-9 only'
    # drawn at the library's native 34-unit height, then scaled as a whole
    g, w = wedge_number(n, 1, 0, 'ink', 34, 15)
    if not n:
        g = g.replace('class="faint"', 'class="zero"')
    W = (w + 2) if n else 24
    k = h / 34
    return (f'<svg class="gx wedge" viewBox="0 0 {W:.1f} 34" width="{W * k:.1f}" height="{h}" '
            f'aria-hidden="true" focusable="false">{g}</svg>')


if __name__ == '__main__':
    print(HERO_DESC)
    print(len(hero_rows('d')), len(hero_rows('m')), tally(3)[:80], wedges(4, 20)[:120])
