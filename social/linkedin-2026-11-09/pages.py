# HTML pages (1080x1350) around the images from gen.py; shot.js screenshots them.
import re
B = '/home/claude/describe-brand-system'; F = 'file://' + B + '/decisions/fonts/'
LD = re.sub(r'<metadata>.*?</metadata>', '', open(B + '/wordmark/lockup-horizontal-compact-dark.svg').read(), flags=re.S)
LL = re.sub(r'<metadata>.*?</metadata>', '', open(B + '/wordmark/lockup-horizontal-compact-light.svg').read(), flags=re.S)
CSS = f"""@font-face{{font-family:Fraunces;src:url('{F}Fraunces%255BSOFT,WONK,opsz,wght%255D.ttf')}}
@font-face{{font-family:Readex;src:url('{F}ReadexPro%255BHEXP,wght%255D.ttf')}}
@font-face{{font-family:Plex;src:url('{F}IBMPlexMono-Medium.ttf');font-weight:500}}
*{{margin:0;box-sizing:border-box}} html,body{{width:1080px;height:1350px}}
.page{{width:1080px;height:1350px;padding:88px 88px 72px;display:flex;flex-direction:column;position:relative;overflow:hidden;background:#F6F8FC;color:#092052;font-family:Readex;font-weight:300}}
.dark{{background:#092052;color:#F6F8FC}}
h1{{font-family:Fraunces;font-weight:300;font-variation-settings:'SOFT' 0,'WONK' 0;font-size:80px;line-height:1.06;letter-spacing:-1.5px;margin-top:30px}}
h1 span{{color:#0F58E5}} .dark h1 span{{color:#4F86F7}}
[dir=rtl] h1{{font-family:Readex;font-weight:400;font-size:76px;line-height:1.25;letter-spacing:0}}
.lbl{{font-family:Plex;font-weight:500;font-size:22px;letter-spacing:3px;text-transform:uppercase;color:#64748B}}
[dir=rtl] .lbl{{font-family:Readex;font-weight:500;letter-spacing:0;font-size:26px}}
.dark .lbl,.dark .src{{color:#8A99B0}}
.foot{{position:relative;z-index:5;margin-top:auto;display:flex;justify-content:space-between;align-items:flex-end;gap:40px}}
.foot svg{{height:46px;width:auto;flex:none}}
.src{{font-size:20px;color:#64748B;max-width:640px;line-height:1.4}} [dir=rtl] .src{{font-size:22px}}
.art{{position:absolute;left:0;width:1080px}}"""
P = {
 'r1': (0, 'ltr', 'Sample report · public data', 'One year of orders.<br><span>One sample report.</span>', 'Public UCI Online Retail dataset, Dec 2010 to Dec 2011. The 43 brass dots are the top 1% of customers by net revenue.', 'r1_img.png', 400),
 'b1': (1, 'ltr', 'Black Friday · Nov 27', 'AI shoppers are coming.<br><span>Will your reports see them?</span>', 'Adobe expects AI-assistant traffic to US retail sites up about 130% this season and 95% on Black Friday. Bars are a sample, not real data.', 'b1_img.png', 400),
 'b2': (0, 'ltr', 'AI on small-business data', 'Seven times more AI.<br><span>The same messy data.</span>', 'Coupler.io, among its own small-business and agency customers, Sep 2025 to Sep 2026.', 'b2_img.png', 400),
 'r2': (1, 'ltr', 'Christmas stock check · tested', '1% off in total.<br><span>55% off per product.</span>', 'Black Friday week projected to 24 December, tested against what December 2011 really sold in the public Online Retail dataset.', 'r2_img.png', 400),
 'b3': (0, 'ltr', 'Planning 2027', 'Five numbers<br><span>before any tool.</span>', 'For each number: who owns it, where it comes from, and what would make you act.', 'b3_img.png', 400),
 'n1': (1, 'ltr', 'NGO Data Diagnostic · one week', 'The writing is quick.<br><span>The table takes the week.</span>', 'Sample indicator table, no real data. Free 20-minute call: describe.team', 'n1_img.png', 390),
 'n2': (0, 'ltr', 'For M&amp;E teams', 'Which indicator<br><span>took the longest?</span>', 'Sample data. Survey answers drawn as dots, gathered into the indicators a donor report asks for.', 'n2_img.png', 390),
}
for n, (dark, d, lbl, h1, src, img, top) in P.items():
    html = f"""<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>
<div class='page{' dark' if dark else ''}' dir='{d}'><div class='art' style='top:{top}px;height:{1350-top-150}px;overflow:hidden'><img src='{img}'></div>
<div style='position:relative'><div class='lbl'>{lbl}</div><h1>{h1}</h1></div>
<div class='foot' dir='ltr'>{'<div class=src dir=rtl style="text-align:right;order:2">' + src + '</div>' if d == 'rtl' else '<div class=src>' + src + '</div>'}{LD if dark else LL}</div></div></body></html>"""
    open(n + '.html', 'w').write(html)
