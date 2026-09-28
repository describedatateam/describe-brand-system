"""
build.py — assemble /home/claude/website/site.html

    python3 /home/claude/website/build.py

Inputs (read, never modified):
  template.html                         page source, with placeholders
  ../type/typography.css, ../ui/ui.css  the type and component system, inlined
  graphics.py                           the phase-2 graphics (rulers, tallies, wedges)
  ../illustrations/bitmaps/hero-night/  the night-plate sky masks (1x and 2x), embedded once each
  ../geometry/svg/z01-mark.svg          the 5a mark (nav / footer stand-in)
  ../ui/icons.json                      the 24-grid icon set
  ../decisions/uci_audit.json           the proof figures — the only source of numbers
  ../charts/chartkit.py                 chart furniture

Placeholders in template.html:
  /*CSS*/                typography.css + ui.css + chart classes
  <!--G:hero:d|m-->      the source file as a ruler (desktop x16 / phone x25 vernier)
  <!--TALLY:n-->         section index, n of 8
  <!--WEDGE:n:h-->       a wedge count for a small real number, h px tall
  {{hero_desc}}          text equivalent of the hero ruler
  <!--MARK:size-->       the mark, stroke weights adjusted for its render size
  {{icon:name}}          an icon
  {{n:key}}              a formatted figure from uci_audit.json
  <!--CHART:desktop-->   the proof chart, drawn to scale for wide screens
  <!--CHART:mobile-->    the same chart, drawn to scale for a 390px phone
  <!--CHART:xs-->        the same chart for phones under 375px, so no label falls below 9px
  <!--FRULE:kind-->      a finding drawn as a short ruler (half, jan, nocust; window = hero total -> chart n)

Deliberate departure from inspo/INSPO.md: no wedges in Services ("4 days", "2 revisions").
The three services share one figure-over-label row instead; wedges stay in Method and
"Where we are". See the note at the top of graphics.py.
  <!--TABLE-->           the chart's table twin
"""
import json
import os
import re
import sys
from datetime import date

R = '/home/claude/'
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, R + 'charts')
import chartkit as ck  # noqa: E402
sys.path.insert(0, H)
import graphics as gx  # noqa: E402

U = json.load(open(R + 'decisions/uci_audit.json'))
ICONS = json.load(open(R + 'ui/icons.json'))

# ------------------------------------------------------------------ figures
MONTHS = sorted(U['monthly_net_gbp'])
VALS = [U['monthly_net_gbp'][m] for m in MONTHS]
YEAR = U['year_net_gbp']
assert abs(sum(VALS) - YEAR) < 1, 'monthly figures do not add up to the year'
STORY = [i for i, m in enumerate(MONTHS) if m >= '2011-09']            # Sep–Nov
assert abs(sum(VALS[i] for i in STORY) / YEAR - U['sep_nov_share']) < 5e-4
# the ledger must reconcile before anything is drawn
LEDGER = [('Rows in the source file', U['rows'], None),
          ('Exact duplicate rows', U['duplicates'], 'removed'),
          ('Cancellation lines, netted against their orders', U['cancellation_lines'], 'removed'),
          ('Postage, fee and other non-product lines', U['nonproduct_lines'], 'set aside'),
          ('Zero or negative value lines', U['zero_or_negative_lines'], 'set aside')]
assert U['rows'] - sum(r[1] for r in LEDGER[1:]) == U['clean_sale_lines'], 'ledger does not reconcile'
assert U['window_sale_lines'] + U['window_left_out_sale_lines'] == U['clean_sale_lines'], 'window does not reconcile'

# the one flagged line that stays in the chart window and in the total:
# the January line was cancelled (netted out); December 2011 is outside the window
FLAG = next(f for f in U['flagged_lines'] if f['InvoiceNo'] == '556444')
FLAG_M = FLAG['InvoiceDate'][:7]
assert FLAG_M in MONTHS
FLAG_I = MONTHS.index(FLAG_M)

MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
MONL = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
        'September', 'October', 'November', 'December']


def mlabel(m, long=False):
    y, mm = m.split('-')
    return f"{(MONL if long else MON)[int(mm) - 1]} {y}"


def gbp(v):
    return f"£{v:,.0f}"


N = {
    'rows': f"{U['rows']:,}",
    'clean': f"{U['clean_sale_lines']:,}",
    'dups': f"{U['duplicates']:,}",
    'cancel': f"{U['cancellation_lines']:,}",
    'share': f"{U['sep_nov_share'] * 100:.1f}%",
    'year': f"£{YEAR / 1e6:.2f}M",
    'half': f"{U['customers_for_half']:,}",
    'known': f"{U['customers_known']:,}",
    'one_in': f"{round(U['customers_known'] / U['customers_for_half'])}",
    # the chart's window (Dec 2010 - Nov 2011): every proof figure is stated for this period
    'win_n': f"{U['window_sale_lines']:,}",
    'win_canc': f"{U['window_cancellation_lines']:,}",
    'win_out': f"{U['window_left_out_sale_lines']:,}",
    'nocust': f"{U['window_missing_customer_lines']:,}",
    # share of the same net revenue the chart shows (sale lines plus their cancellations)
    'nocust_share': f"{U['window_missing_customer_net_share'] * 100:.1f}%",
    'flag_val': gbp(FLAG['val']),
    'flag_q': f"{FLAG['Quantity']:,}",
    'flag_p': f"£{FLAG['UnitPrice']:,.2f}",
    'jan_q': f"{U['flagged_lines'][0]['Quantity']:,}",
    'jan_val': gbp(U['flagged_lines'][0]['val']),
    'jan_pct': f"{U['flagged_lines'][0]['val'] / U['monthly_net_gbp']['2011-01'] * 100:.0f}%",
    'computed': date(2026, 9, 28).strftime('%-d %b %Y').replace(' ', '\u00a0'),
}


# ------------------------------------------------------------------ chart
def hit(x, y, w, h, tip, below=False):
    """A month's hover/focus target: full band height, announced as its value."""
    tip = ck.esc(tip)
    return (f'<rect class="c-hit" x="{ck.f(x)}" y="{ck.f(y)}" width="{ck.f(w)}" height="{ck.f(h)}" '
            f'role="img" aria-label="{tip}" data-tip="{tip}" tabindex="0"{" data-below" if below else ""}/>')


RULER = 124   # depth of the calendar-to-revenue ruler under the month axis


def chart(W, H_, ml, mr, mt, mb, mobile, tag=None):
    mb += RULER
    H_ += RULER
    top = max(VALS)
    ticks = ck.nice_cover(0, top)
    y0, y1 = H_ - mb, mt
    ys = ck.Linear(0, ticks[-1], y0, y1)
    slot = (W - ml - mr) / len(VALS)
    bw = min(24, slot - 10)
    fs = 10 if mobile else 10.5
    b = []
    # grid first (solid hairlines), then marks, then labels (CHARTS §3 layer order)
    b.append(ck.y_axis(ys, ml, W - mr, ticks,
                       fmt=lambda t: '0' if t == 0 else f"{t / 1e6:.1f}"))
    b.append(ck.line(ml, y0, W - mr, y0, 'c-axis'))
    b.append(ck.unit_label(ml - 8, y1 - 16, '£ million, net'))
    for i, (m, v) in enumerate(zip(MONTHS, VALS)):
        cx = ml + slot * i + slot / 2
        cls = 'c-story' if i in STORY else 'c-context'
        if i == FLAG_I:
            # the flagged line drawn to scale as its own segment on top of the month
            # one bar like its neighbours; the ring marks the flagged line's share at its top
            b.append(ck.bar(cx - bw / 2, cx + bw / 2, y0, ys(v), cls))
        else:
            b.append(ck.bar(cx - bw / 2, cx + bw / 2, y0, ys(v), cls))
        b.append(ck.line(cx, y0, cx, y0 + 5, 'c-axis'))
        mon = MON[int(m[5:]) - 1]
        lab = mon[0] if mobile else mon.upper()     # initials on a phone: no run-on mono phrase
        b.append(ck.text(cx, y0 + 18, lab, 'c-body', fs, 'middle', 'mono'))
    # year change: a divider tick between Dec and Jan, each year 8px clear of it
    for i, m in enumerate(MONTHS):
        if i and m.endswith('-01'):
            xd = ml + slot * i
            b.append(ck.line(xd, y0 + 24, xd, y0 + 36, 'c-axis'))
            b.append(ck.text(xd - 8, y0 + 33, MONTHS[i - 1][:4], 'c-dim', 10, 'end', 'mono'))
            b.append(ck.text(xd + 8, y0 + 33, m[:4], 'c-dim', 10, 'start', 'mono'))
    # calendar vs revenue: the equal month slots above, projected onto a rule where
    # each month is as long as its net revenue (the s3 plate, built into the chart)
    L = W - ml - mr
    yc, yr = y0 + 50, y0 + 104
    b.append(ck.line(ml, yc, W - mr, yc, 'c-grid'))
    cum = 0.0
    for i in range(len(VALS) + 1):
        xc = ml + slot * i
        xr = ml + cum / YEAR * L
        story_edge = i >= STORY[0]
        b.append(ck.line(xc, yc - 4, xc, yc + 4, 'c-axis'))
        b.append(f'<path class="{"c-story" if story_edge else "c-proj"}" d="M{ck.f(xc)} {ck.f(yc + 6)}L{ck.f(xr)} {ck.f(yr - 8)}" '
                 f'stroke-width="1" stroke-dasharray="3 3" fill="none"/>')
        b.append(ck.line(xr, yr - 6, xr, yr + 6, 'c-axis'))
        if i < len(VALS):
            nx = ml + (cum + VALS[i]) / YEAR * L
            b.append(ck.line(xr + 1, yr, nx - 1, yr, 'c-story' if i in STORY else 'c-context', 4))
            cum += VALS[i]
    assert abs(cum - YEAR) < 1
    b.append(ck.unit_label(ml, yr + 22, 'Net revenue, to scale'))
    rs = ml + sum(VALS[:STORY[0]]) / YEAR * L
    re_ = W - mr
    b.append(f'<path class="c-ink" d="M{ck.f(rs)} {ck.f(yr + 11)}V{ck.f(yr + 16)}H{ck.f(re_)}V{ck.f(yr + 11)}" '
             f'fill="none" stroke-width="1"/>')
    b.append(f'<text class="c-ink c-halo" x="{ck.f(re_ - 2)}" y="{ck.f(yr + 37)}" text-anchor="end" '
             f'font-size="{12 if mobile else 12.5}" font-family="{ck.SANS}" font-weight="500" '
             f'style="font-variant-numeric:tabular-nums">{N["share"]} of the money</text>')
    # Sep–Nov bracket over the bars: their share of the calendar (a sentence, so sans throughout)
    sx = ml + slot * STORY[0] + (slot - bw) / 2
    ex = ml + slot * (STORY[-1] + 1) - (slot - bw) / 2
    by = y1 - 10
    b.append(f'<path class="c-ink" d="M{ck.f(sx)} {ck.f(by + 5)}V{ck.f(by)}H{ck.f(ex)}V{ck.f(by + 5)}" '
             f'fill="none" stroke-width="1"/>')
    b.append(f'<text class="c-ink c-halo" x="{ck.f(ex)}" y="{ck.f(by - 7)}" text-anchor="end" '
             f'font-size="{12 if mobile else 12.5}" font-family="{ck.SANS}" font-weight="500" '
             f'style="font-variant-numeric:tabular-nums">{len(STORY) / len(VALS) * 100:.0f}% of the calendar</text>')
    # hover / focus targets: full band height, one per month, each announced
    for i, (m, v) in enumerate(zip(MONTHS, VALS)):
        x = ml + slot * i
        b.append(hit(x, y1, slot, y0 - y1,
                     f"{mlabel(m)}: {gbp(v)} net, {v / YEAR * 100:.1f}% of the year", below=(i == FLAG_I)))
    # the flagged line: coral ring + dot seated on its own segment, rule stated, text in ink.
    # Drawn after the hit targets so it takes its own hover and focus.
    fx = ml + slot * FLAG_I + slot / 2
    fy = (ys(VALS[FLAG_I]) + ys(VALS[FLAG_I] - FLAG['val'])) / 2
    tip = ck.esc(f"Flagged line, {mlabel(FLAG_M)}: {FLAG['Quantity']} × £{FLAG['UnitPrice']:.2f} = "
                 f"{gbp(FLAG['val'])}. Robust z > 7 on log line value. Kept in the total.")
    b.append(f'<g class="c-flag" tabindex="0" role="img" aria-label="{tip}" data-tip="{tip}">'
             f'<circle class="c-focusring" cx="{ck.f(fx)}" cy="{ck.f(fy)}" r="13" fill="none" '
             f'stroke-width="1.5" stroke-dasharray="3 2"/>'
             f'<circle class="c-ringhalo" cx="{ck.f(fx)}" cy="{ck.f(fy)}" r="8" fill="none" stroke-width="4"/>'
             f'<circle class="c-mark" cx="{ck.f(fx)}" cy="{ck.f(fy)}" r="8" fill="none" stroke-width="1.5"/>'
             f'<circle class="c-mark c-fill" cx="{ck.f(fx)}" cy="{ck.f(fy)}" r="3.2"/></g>')
    dx, dy = (-34, -84) if not mobile else (-6, -74)   # clear of the 1.0 tick label on phones
    b.append(ck.leader(fx, fy, dx, dy, 'One line flagged, kept',
                       sub=f"{N['flag_val']} · z > 7", r_off=9))
    label = (f"Bar chart of net monthly revenue, December 2010 to November 2011. "
             f"September to November are highlighted: {len(STORY) / len(VALS) * 100:.0f}% of the calendar months and {N['share']} of the year's "
             f"net revenue, shown on a rule below where each month is as long as its revenue. "
             f"One line in June, {N['flag_val']}, is flagged as an outlier and kept. "
             f"Tab through the months to hear each value; the table below holds every value.")
    s = ck.svg(''.join(b), W, H_, label)
    # tabindex=-1: Chromium otherwise gives the <svg> itself a tab stop before the first bar
    s = s.replace('role="img"', 'role="group" focusable="false" tabindex="-1"', 1)
    return s.replace('class="dsc-chart"', f'class="dsc-chart chart__svg chart__svg--{tag or ("m" if mobile else "d")}"', 1)


def table():
    rows = []
    for i, (m, v) in enumerate(zip(MONTHS, VALS)):
        flag = ''
        if m == FLAG_M:   # the flag sits with the month: no empty column, no null mark where nothing is missing
            flag = (f'<span class="flagmark" aria-hidden="true"></span>'
                    f'<span class="flagnote"><span class="vh">, </span>1 flagged line, {N["flag_val"]}, kept</span>')
        cls = ' class="is-story"' if i in STORY else ''
        rows.append(f'<tr{cls}><th scope="row">{mlabel(m)}{flag}</th><td class="num">{gbp(v)}</td>'
                    f'<td class="num">{v / YEAR * 100:.1f}%</td></tr>')
    rows.append(f'<tr class="is-total"><th scope="row">Twelve months</th><td class="num">{gbp(YEAR)}</td>'
                f'<td class="num">100.0%</td></tr>')
    return ('<div class="d-tablewrap" tabindex="0" role="region" aria-label="Net revenue by month, scrollable table">'
            '<table class="d-table twin__table">'
            '<caption class="vh">Net revenue by month, December 2010 to November 2011, with each month’s share '
            'of the year. The ringed month holds the flagged line.</caption>'
            '<thead><tr><th scope="col">Month</th><th scope="col" class="num">Net, £</th>'
            '<th scope="col" class="num">Share</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>')



# ------------------------------------------------------------------ mark
MARK_SRC = open(R + 'geometry/svg/z01-mark.svg').read()


def mark(size):
    body = re.sub(r'<style>.*?</style>', '', MARK_SRC, flags=re.S)
    body = re.sub(r'^<svg[^>]*>', '', body).replace('</svg>', '')
    # at small sizes the 240-unit strokes fall under a device pixel; thicken them
    k = {'nav': 1.9, 'foot': 1.25}[size]
    body = re.sub(r'stroke-width="([\d.]+)"', lambda m: f'stroke-width="{float(m.group(1)) * k:.2f}"', body)
    return (f'<svg class="mark mark--{size}" viewBox="-20 -20 240 240" fill="none" aria-hidden="true" '
            f'focusable="false">{body}</svg>')


def icon(name, extra=''):
    ic = ICONS[name]
    d = ' d-icon--dir' if ic['directional'] else ''
    return (f'<svg class="d-icon{d}{extra}" viewBox="0 0 24 24" aria-hidden="true" '
            f'focusable="false">{ic["body"]}</svg>')


# ------------------------------------------------------------------ assemble
TYPO = open(R + 'type/typography.css').read()
for fam in ('Prata', r'Reem\+Kufi'):   # not used on this page: don't make visitors download them
    TYPO = re.sub(r"@import url\('https://fonts\.googleapis\.com/css2\?family=" + fam + r"[^']*'\);\n", '', TYPO)
assert 'Prata&' not in TYPO and 'Reem+Kufi' not in TYPO
css = (TYPO + '\n' +
       re.sub(r"@import url\('\.\./type/typography\.css'\);\s*", '', open(R + 'ui/ui.css').read()) +
       '\n/* ---- chart tokens and classes (charts/chartkit.py) ---- */\n' +
       ck.page_tokens() + ck.style_block(tokens=False))

t = open(os.path.join(H, 'template.html'), encoding='utf-8').read()
t = t.replace('/*CSS*/', css, 1)
t = re.sub(r'<!--G:hero:(\w)-->', lambda m: gx.hero_rows(m.group(1)), t)
# the night plate: each density cropped to the only region the page ever shows, then
# embedded once, as a 1-bit palette PNG (lit = opaque). Crops are in CSS px at 1x:
#   desktop window: mask origin at plate (800, 250); window <= 1020 x 600  -> x 800-1820, y 250-850
#   phone strip:    mask origin at plate (820, 300); strip  <=  999 x 240  -> x 820-1819, y 300-540
# so 1x and 2x carry the union (800-1820 x 250-850), and 3x only the phone strip,
# which is the only place 3-dppx screens show it (desktop at 3 dppx falls back to 2x, pixelated).
import base64, io  # noqa: E401,E402
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402
SKY = R + 'illustrations/bitmaps/hero-night/'
CROP = {'SKY1': ('hero-night_lit.png', 1, (800, 250, 1820, 850)),
        'SKY2': ('hero-night_lit@2x.png', 2, (800, 250, 1820, 850)),
        'SKY3': ('hero-night_lit@3x.png', 3, (820, 300, 1820, 540))}
DESK_W, DESK_H, PHONE_W, PHONE_H = 1020, 600, 999, 240
assert CROP['SKY1'][2] == (800, 250, 800 + DESK_W, 250 + DESK_H)
assert 820 >= 800 and 820 + PHONE_W <= 1820 and 300 + PHONE_H <= 850      # phone strip inside the 1x/2x crop
assert (820 + PHONE_W, 300 + PHONE_H) <= (CROP['SKY3'][2][2], CROP['SKY3'][2][3])
SKY_BYTES = 0
for tag, (fn, k, (x0, y0, x1, y1)) in CROP.items():
    assert t.count(f'<!--{tag}-->') == 1, f'{tag} must be embedded exactly once'
    lit = np.array(Image.open(SKY + fn))[..., -1] > 127
    assert lit.shape == (1200 * k, 2400 * k), f'{fn} is not the full plate at {k}x'
    im = Image.fromarray(lit[y0 * k:y1 * k, x0 * k:x1 * k].astype(np.uint8), 'L').convert('P')
    im.putpalette([0, 0, 0, 255, 255, 255] + [0] * 762)
    buf = io.BytesIO()
    im.save(buf, 'PNG', optimize=True, bits=1, transparency=0)
    SKY_BYTES += len(buf.getvalue())
    t = t.replace(f'<!--{tag}-->', 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode())
# the clean figure is right-aligned to the blue index tick: its end margin is the set-aside share
t = t.replace('<!--XC_END-->', f"{(1 - U['clean_sale_lines'] / U['rows']) * 100:.3f}%")
t = re.sub(r'<!--TALLY:(\d)-->', lambda m: gx.tally(int(m.group(1))), t)
t = re.sub(r'<!--WEDGE:(\d):(\d+)-->', lambda m: gx.wedges(int(m.group(1)), int(m.group(2))), t)
t = t.replace('{{hero_desc}}', gx.HERO_DESC)
t = re.sub(r'<!--MARK:(\w+)-->', lambda m: mark(m.group(1)), t)
t = re.sub(r'\{\{icon:(\w+)\}\}', lambda m: icon(m.group(1)), t)
t = re.sub(r'\{\{n:(\w+)\}\}', lambda m: N[m.group(1)], t)
t = t.replace('<!--CHART:desktop-->', chart(720, 380, 44, 12, 62, 46, False))
t = t.replace('<!--CHART:mobile-->', chart(326, 306, 32, 0, 46, 46, True))
t = t.replace('<!--CHART:xs-->', chart(272, 306, 33, 1, 46, 46, True, 'x'))   # <375px: labels stay >= 9px
t = re.sub(r'<!--FRULE:(\w+)-->', lambda m: gx.finding_rule(m.group(1)), t)
t = t.replace('<!--TABLE-->', table())
left = re.findall(r'<!--[A-Z]+:[^>]*-->|\{\{[^}]*\}\}', t)
assert not left, f'unfilled placeholders: {left}'
for bad in (r'<!doctype', r'<html[\s>]', r'<head[\s>]', r'<body[\s>]'):
    assert not re.search(bad, t, re.I), f'artifact must not contain {bad}'
assert t.startswith('<title>'), 'artifact must start with <title>'
open(os.path.join(H, 'site.html'), 'w', encoding='utf-8').write(t)
print(f'site.html {len(t) // 1024} KB (sky masks {SKY_BYTES // 1024} KB as PNG, embedded as base64)')
