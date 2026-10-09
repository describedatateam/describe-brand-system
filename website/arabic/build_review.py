"""build_review.py — ar-copy.json → review.html: English and Arabic side by side for the founder's review."""
import html, json, itertools

d = json.load(open('ar-copy.json', encoding='utf-8'))
HEADINGS = {'See your real profit, not just your sales.', 'Your store shows sales. Not what you keep.', 'Three ways in.',
            'Five stages. Each one stops the next being guesswork.', 'What a year of e‑commerce sales shows.',
            'We are a new practice.', 'The name is the method.', 'Before you write.', 'Tell us about your store.',
            'Store profit health check', 'Privacy', 'A number doesn’t have to be wrong to mislead you.',
            'September to November: a quarter of the calendar, over a third of the money.',
            'Reporting gaps and missing history were the symptom, not the thing to fix.'}
TITLES = {'nav': 'Navigation', 'footer': 'Footer', 'meta': 'Page title and description', 'hero': 'Hero',
          'rulers': 'The ruler band', '01 who': '01 · Who we help', '02 services': '02 · Services', '03 method': '03 · Method',
          '04 proof': '04 · Worked example', '05 where': '05 · Where we are', '06 about': '06 · About', '07 faq': '07 · Questions',
          '08 contact': '08 · Contact', 'check': 'Store profit check  ·  /ar/check/', 'privacy': 'Privacy  ·  /ar/privacy/'}

import re
def bidi(s):
    # Arabic runs inside an English note: isolate them so punctuation stays put
    return re.sub(r'(«[^»]*»)', lambda m: f'<bdi lang="ar" dir="rtl">{m.group(1)}</bdi>', html.escape(s))

def rows(entries):
    out = []
    for e in entries:
        en, ar = e[0], e[1]
        note = e[2] if len(e) > 2 else ''
        cls = ' h' if en in HEADINGS else ''
        arc = html.escape(ar) if ar else '<span class="none">— remove —</span>'
        out.append(f'<div class="row{cls}"><p class="en" lang="en">{html.escape(en)}</p>'
                   f'<p class="ar" lang="ar" dir="rtl">{arc}</p>'
                   + (f'<p class="note">{bidi(note)}</p>' if note else '') + '</div>')
    return ''.join(out)

groups = [('nav', d['nav'])] + list(d['home'].items()) + [('footer', d['footer']), ('check', d['check']), ('privacy', d['privacy'])]
toc = ''.join(f'<a href="#s{i}">{html.escape(TITLES[k])}</a>' for i, (k, _) in enumerate(groups))
body = ''.join(f'<section id="s{i}"><h2>{html.escape(TITLES[k])}<span>{len(v)}</span></h2>{rows(v)}</section>' for i, (k, v) in enumerate(groups))
n = sum(len(v) for _, v in groups)
tpl = open('review_template.html', encoding='utf-8').read()
open('review.html', 'w', encoding='utf-8').write(tpl.replace('{{TOC}}', toc).replace('{{BODY}}', body).replace('{{N}}', str(n)))
print('review.html', n, 'lines')
