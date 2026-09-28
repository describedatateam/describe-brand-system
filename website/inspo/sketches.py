"""
sketches.py — three proof plates for the proposed graphics system.

Built with the Role 02 library (astrolabe.py); every number comes from
/home/claude/decisions/uci_audit.json or the site's existing copy.

    python3 sketches.py        writes s1-*.svg s2-*.svg s3-*.svg here
    python3 render.py          rasters them to PNG next to the SVGs
"""
import json
import math
import sys

sys.path.insert(0, '/home/claude/geometry')
from astrolabe import (THETA, W_HAIR, W_MARK, W_RING, W_STEM, circle, dot,  # noqa
                       f, line, measuring_edge, path, projection,
                       tally_progress, tick_row)

A = json.load(open('/home/claude/decisions/uci_audit.json', encoding='utf-8'))

# Sketch palette: literal light tokens (the site uses the CSS variables).
STYLE = """
.ink{stroke:#092052;color:#092052}.body{stroke:#64748B;color:#64748B}
.faint{stroke:#CBD5E1;color:#CBD5E1}.active{stroke:#0F58E5;color:#0F58E5}
.mark{stroke:#E5484D;color:#E5484D}.fill{stroke:none}
.fr{font-family:Fraunces,Georgia,serif;font-weight:300;
 font-variation-settings:'SOFT' 0,'WONK' 0;font-variant-numeric:lining-nums tabular-nums}
.rx{font-family:'Readex Pro',system-ui,sans-serif}
.mo{font-family:'IBM Plex Mono',ui-monospace,monospace;letter-spacing:.06em}
.am{font-family:Amiri,serif}
"""


def doc(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}" fill="none" role="img" aria-label="{title}">'
            f'<style>{STYLE}</style><rect width="{w}" height="{h}" fill="#F6F8FC"/>'
            f'{body}</svg>')


def T(x, y, s, cls='ink', size=16, face='rx', anchor='start', weight=None, extra=''):
    wt = f' font-weight="{weight}"' if weight else ''
    return (f'<text x="{f(x)}" y="{f(y)}" class="{cls} fill {face}" fill="currentColor" '
            f'font-size="{size}" text-anchor="{anchor}"{wt} {extra}>{s}</text>')


def label(x, y, s, cls='body', anchor='start'):
    """Mono label: uppercase, <= 11px, four words or fewer (brief rule)."""
    assert len(s.split()) <= 4, s
    return T(x, y, s.upper(), cls, 10.5, 'mo', anchor)


def num(n):
    return f'{n:,}'


# ---------------------------------------------------------------------------
# The wedge: a counting sign cut at the sight angle.
#   · unit wedge  — a vertical stroke with a triangular head; head apex angle
#                   is 2|θ| = 81.2°, the mark's own angle
#   · ten wedge   — the corner wedge (Winkelhaken): arms at ±θ from horizontal
# Units stack in rows of up to three, top row first (Old Babylonian practice;
# attested variants differ). A value above 59 is never drawn: set a numeral.
# ---------------------------------------------------------------------------
TAN = math.tan(math.radians(abs(THETA)))


def unit_wedge(x, y, h=34.0, hw=12.0, cls='ink'):
    hd = (hw / 2) / TAN
    head = (f'M{f(x - hw / 2)} {f(y)}L{f(x + hw / 2)} {f(y)}L{f(x)} {f(y + hd)}Z')
    return (path(head, cls + ' fill', None, fill='currentColor')
            + line(x, y + hd - 1, x, y + h, cls, W_MARK * 0.8,
                   **{'stroke-linecap': 'butt'}))


def ten_wedge(x, y, h=34.0, cls='ink'):
    """Corner wedge; (x, y) is the vertex, arms open to the right at ±θ.

    Drawn as one filled impression (a stylus corner pressed in), not two
    strokes, so a pair never reads as a guillemet.
    """
    ax = (h / 2) / TAN
    notch = ax * 0.55
    d = (f'M{f(x)} {f(y)}L{f(x + ax)} {f(y - h / 2)}L{f(x + notch)} {f(y)}'
         f'L{f(x + ax)} {f(y + h / 2)}Z')
    return path(d, cls + ' fill', None, fill='currentColor')


def wedge_number(n, x, y, cls='ink', h=34.0, pitch=15.0, row=None):
    """Draw 0 <= n <= 59 in wedges. 0 is the empty place: a faint slot.

    On the site use units only (0-9): at screen sizes a pair of corner
    wedges reads as a back arrow. ten_wedge() stays here for print.
    """
    assert 0 <= n <= 59, 'over 59: set a numeral instead'
    tens, units = divmod(n, 10)
    out = []
    if n == 0:
        out.append(path(f'M{f(x)} {f(y)}L{f(x)} {f(y + h)}M{f(x + 22)} {f(y)}L{f(x + 22)} {f(y + h)}',
                        'faint', W_HAIR, **{'stroke-dasharray': '3 4'}))
        return ''.join(out), 22
    tp = h * 0.62                      # tens pitch
    for i in range(tens):
        out.append(ten_wedge(x + i * tp, y + h / 2, h * 0.72, cls))
    ux = x + (tens * tp + h * 0.35 if tens else 0)
    rows = [3] * (units // 3) + ([units % 3] if units % 3 else [])
    if len(rows) > 1 and rows[-1] < rows[0]:
        pass                            # fuller row on top: 4 = 3 over 1
    nr = max(len(rows), 1)
    gap = 4.0
    rh = (h - gap * (nr - 1)) / nr
    hw = 12.0 if nr == 1 else 10.0
    for r, k in enumerate(rows):
        for j in range(k):
            out.append(unit_wedge(ux + j * pitch + hw / 2, y + r * (rh + gap), rh, hw, cls))
    width = ux - x + (max(rows) * pitch if rows else 0)
    return ''.join(out), width


# ---------------------------------------------------------------------------
# S1 — HERO: the source file as a ruler, with a vernier on what was set aside
# ---------------------------------------------------------------------------

def s1():
    W, H = 1200, 540
    X0, X1, Y = 80.0, 1120.0, 262.0
    rows = A['rows']
    parts = [('duplicates', A['duplicates'], 'Exact duplicates'),
             ('cancellation_lines', A['cancellation_lines'], 'Cancellations netted'),
             ('nonproduct_lines', A['nonproduct_lines'], 'Postage and fees'),
             ('zero_or_negative_lines', A['zero_or_negative_lines'], 'Zero or negative')]
    clean = A['clean_sale_lines']
    assert rows - sum(p[1] for p in parts) == clean
    k = (X1 - X0) / rows
    xc = X0 + clean * k
    o = []
    # figures
    o.append(label(X0, 92, 'Rows in the file'))
    o.append(T(X0 - 4, 188, num(rows), 'body', 104, 'fr'))
    # main rule: graduated every 100k, minors every 20k
    o.append(tick_row(X0, Y - 14, 100000 * 5 * k, 26, 5, 5, 11, cls='faint', w=W_HAIR))
    for i in range(6):
        o.append(label(X0 + i * 100000 * k, Y - 32, f'{i * 100}k' if i else '0', 'body', 'middle'))
    o.append(line(X0, Y, xc, Y, 'ink', W_RING, **{'stroke-linecap': 'butt'}))
    # the set-aside tail: four slices at true scale, 1px apart
    x = xc
    for _, n, _ in parts:
        w = n * k
        o.append(line(x + 0.6, Y, x + w - 0.6, Y, 'body', W_RING, **{'stroke-linecap': 'butt'}))
        x += w
    o.append(line(X1, Y - 10, X1, Y + 10, 'faint', W_HAIR))
    # the reading: one active index where clean data ends
    o.append(line(xc, Y - 22, xc, Y + 16, 'active', W_MARK))
    o.append(dot(xc, Y, 4.2, 'active'))
    # vernier: magnify the tail ×16 below, joined by projection lines
    M = 16
    VX1 = X1
    VX0 = X1 - (rows - clean) * k * M
    VY = 404
    o.append(projection(xc, Y + 8, VX0, VY - 8))
    o.append(projection(X1, Y + 8, VX1, VY - 8))
    aside = rows - clean
    o.append(label(VX0, VY - 20, f'{num(aside)} set aside'))
    o.append(label(VX1, VY - 20, f'Scale ×{M}', 'body', 'end'))
    x = VX0
    for idx, (_, n, name) in enumerate(parts):
        w = n * k * M
        o.append(line(x + 1.5, VY, x + w - 1.5, VY, 'body', W_RING, **{'stroke-linecap': 'butt'}))
        o.append(line(x, VY - 9, x, VY + 9, 'faint', W_HAIR))
        ly = VY + 44 if idx % 2 == 0 else VY + 92
        o.append(line(x + w / 2, VY + 6, x + w / 2, ly - 26, 'faint', W_HAIR))
        o.append(T(x + w / 2, ly, '−' + num(n), 'ink', 26, 'fr', 'middle'))
        o.append(label(x + w / 2, ly + 18, name, 'body', 'middle'))
        x += w
    o.append(line(VX1, VY - 9, VX1, VY + 9, 'faint', W_HAIR))
    # the result
    o.append(label(X0, 360, 'Clean sale lines'))
    o.append(T(X0 - 3, 440, num(clean), 'ink', 80, 'fr'))
    o.append(T(X0, 482, 'Every row accounted for. UCI Online Retail, the worked example below.',
               'body', 14, 'rx'))
    return doc(W, H, ''.join(o), 'Source file of 541,909 rows as a ruler; 19,341 set aside, magnified')


# ---------------------------------------------------------------------------
# S2 — THE SPINE: measuring edge, section numeral, tally index, wedge counts
# ---------------------------------------------------------------------------

def s2():
    W, H = 1200, 640
    o = []
    # page spine: the measuring edge at the left margin (a slice of the page)
    o.append(measuring_edge(x=40, y0=24, y1=616, count=38, major_every=6, cls='faint'))
    # this section's major tick is the active reading
    sy = 96
    o.append(line(40, sy, 62, sy, 'active', W_MARK))
    o.append(dot(40, sy, 4.2, 'active'))
    # section numeral + tally index (section 3 of 8)
    o.append(T(88, 150, '03', 'body', 132, 'fr'))
    o.append(tally_progress(3, 8, 96, 178, 18, 7, 10))
    o.append(label(96, 222, 'Section 3 of 8'))
    o.append(T(300, 104, 'Five stages. Each one stops', 'ink', 44, 'fr'))
    o.append(T(300, 156, 'the next being guesswork.', 'ink', 44, 'fr'))
    # method rule: five stations, each numbered in wedges
    stages = ['Observe', 'Measure', 'Understand', 'Identify', 'Decide']
    X0, X1, Y = 300.0, 1140.0, 262.0
    o.append(line(X0, Y, X1, Y, 'body', W_HAIR))
    o.append(tick_row(X0, Y, X1 - X0, 41, 8, 4, 10, cls='faint', w=W_HAIR))
    step = (X1 - X0) / 5
    for i, s in enumerate(stages):
        x = X0 + i * step
        o.append(line(x, Y - 16, x, Y + 16, 'ink', W_MARK))
        g, _ = wedge_number(i + 1, x + 2, Y + 32, 'ink', 44, 15)
        o.append(g)
        o.append(T(x, Y + 112, s, 'ink', 24, 'fr'))
    # where we are: the three honest counts, and the reply time
    by = 440
    o.append(line(300, by - 50, 1140, by - 50, 'faint', W_HAIR))
    o.append(T(88, by + 8, 'We are a', 'ink', 30, 'fr'))
    o.append(T(88, by + 44, 'new practice.', 'ink', 30, 'fr'))
    counts = [(1, 'Exploratory session'), (1, 'Proposal written'),
              (0, 'Completed projects')]
    cx = 300
    for n, name in counts:
        g, w = wedge_number(n, cx, by - 22, 'ink', 48)
        o.append(g)
        o.append(T(cx + 40, by + 24, str(n), 'ink' if n else 'body', 64, 'fr'))
        o.append(label(cx, by + 60, name))
        cx += 280
    return doc(W, H, ''.join(o), 'Page spine, section numeral with tally index, and wedge counts')


# ---------------------------------------------------------------------------
# S3 — PROOF: the calendar ruler against the revenue ruler
# ---------------------------------------------------------------------------

def s3():
    W, H = 1200, 560
    m = A['monthly_net_gbp']
    keys = list(m)
    total = sum(m.values())
    assert abs(total - A['year_net_gbp']) < 1
    X0, X1 = 80.0, 1120.0
    YC, YR = 200.0, 380.0        # calendar rule, revenue rule
    L = X1 - X0
    o = []
    o.append(T(X0, 70, 'September to November: a quarter of the calendar,', 'ink', 34, 'fr'))
    o.append(T(X0, 112, 'over a third of the money.', 'ink', 34, 'fr'))
    # calendar rule: 12 equal months
    o.append(label(X0, YC - 30, 'Calendar, equal months'))
    o.append(line(X0, YC, X1, YC, 'body', W_HAIR))
    # revenue rule: the same 12 months, each as wide as its net revenue
    o.append(label(X0, YR + 30, 'Net revenue, £, cumulative'))
    o.append(line(X0, YR, X1, YR, 'body', W_HAIR))
    cum = 0.0
    abbr = ['D', 'J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N']
    story = {'2011-09', '2011-10', '2011-11'}
    for i, key in enumerate(keys + [None]):
        xc = X0 + i * L / 12
        xr = X0 + cum / total * L
        on = key in story or (key is None) or (i > 0 and keys[i - 1] in story and key in story)
        edge_story = (key in story) or (i > 0 and keys[i - 1] in story)
        o.append(line(xc, YC - 8, xc, YC + 8, 'body', W_HAIR))
        o.append(line(xr, YR - 8, xr, YR + 8, 'body', W_HAIR))
        o.append(projection(xc, YC + 10, xr, YR - 10, 'active' if edge_story else 'faint'))
        if key:
            v = m[key]
            nxc = X0 + (i + 1) * L / 12
            nxr = X0 + (cum + v) / total * L
            cls = 'active' if key in story else 'body'
            o.append(label((xc + nxc) / 2, YC - 10, abbr[i], 'body', 'middle'))
            o.append(line(xr + 1.5, YR, nxr - 1.5, YR, cls, W_RING, **{'stroke-linecap': 'butt'}))
            cum += v
    # the finding, measured on the revenue rule
    s0 = X0 + sum(m[k] for k in keys[:9]) / total * L
    o.append(line(s0, YR + 60, X1, YR + 60, 'active', W_HAIR))
    o.append(line(s0, YR + 54, s0, YR + 66, 'active', W_HAIR))
    o.append(line(X1, YR + 54, X1, YR + 66, 'active', W_HAIR))
    o.append(T((s0 + X1) / 2, YR + 108, f"{A['sep_nov_share'] * 100:.1f}%", 'ink', 44, 'fr', 'middle'))
    o.append(line(X1 - 3 * L / 12, YC - 50, X1, YC - 50, 'body', W_HAIR))
    o.append(line(X1 - 3 * L / 12, YC - 56, X1 - 3 * L / 12, YC - 44, 'body', W_HAIR))
    o.append(line(X1, YC - 56, X1, YC - 44, 'body', W_HAIR))
    o.append(label(X1 - 1.5 * L / 12, YC - 64, '25% of months', 'body', 'middle'))
    # the one outlier: June holds the flagged line (robust z > 7), kept
    jx0 = X0 + sum(m[k] for k in keys[:6]) / total * L
    jx1 = jx0 + m['2011-06'] / total * L
    jm = (jx0 + jx1) / 2
    o.append(circle(jm, YR, 8.5, 'mark', W_HAIR))
    o.append(dot(jm, YR, 3.4, 'mark'))
    o.append(path(f'M{f(jm)} {f(YR + 10)}L{f(jm)} {f(YR + 70)}L{f(jm - 18)} {f(YR + 70)}', 'body', W_HAIR))
    o.append(label(jm - 24, YR + 74, 'One line flagged, kept', 'body', 'end'))
    o.append(T(X0, 540, f"n = {num(A['clean_sale_lines'])} sale lines · UCI Online Retail, Dec 2010 – Nov 2011 · "
               f"net £{A['year_net_gbp'] / 1e6:.2f}m", 'body', 13, 'rx'))
    return doc(W, H, ''.join(o), 'Calendar months projected onto a revenue-weighted ruler')


if __name__ == '__main__':
    for name, fn in (('s1-hero-rows-ruler', s1), ('s2-spine-and-counts', s2),
                     ('s3-proof-calendar-vs-revenue', s3)):
        open(f'/home/claude/website/inspo/{name}.svg', 'w', encoding='utf-8').write(fn())
        print('wrote', name)
