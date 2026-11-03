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
 'p1': (0, 'ltr', 'Online Retail data · 13 months', 'One year of data<br><span>can’t show growth.</span>', 'Net monthly revenue, public UCI Online Retail dataset, Dec 2010 to Dec 2011. *December 2011 runs only to 9 Dec.', 'p1_img.png', 400),
 'c1': (1, 'ltr', 'Same topic · two numbers', '+130% or +88%?<br><span>Both can be right.</span>', 'Growth in shoppers arriving at retail sites from AI assistants, as quoted this autumn: one a season forecast, one measured so far this year.', 'c1_img.png', 420),
 'c2': (1, 'ltr', 'AI adoption · UAE', 'The Gulf isn’t short of AI.<br><span>It’s short of clean data.</span>', 'Microsoft AI Diffusion Report: 70.1% of the UAE’s working-age population uses generative AI. Earth redrawn in digits; the brass digits are the UAE.', 'c2_img.png', 370),
 'p2': (0, 'ltr', 'Black Friday · Nov 27', 'Six numbers,<br><span>one page.</span>', 'Sample layout, no real data. Set it up now and test it on a quiet weekday.', 'p2_img.png', 400),
 'c3': (1, 'ltr', 'Gulf AI · 2026', 'The news is about models.<br><span>The work is one definition.</span>', 'Saudi Arabia’s Year of AI, the UAE’s AI and Data Authority, GITEX at Expo City Dubai, 8 to 11 Dec.', 'c3_img.png', 420),
 'n1': (1, 'rtl', 'فحص بيانات المؤسسة · أسبوع واحد', 'خمسة أماكن للأرقام،<br><span>ولوحة مؤشرات واحدة.</span>', 'بيانات توضيحية. مكالمة مجانية ٢٠ دقيقة: describe.team', 'n1_img.png', 420),
 'n2': (1, 'rtl', 'من الميدان إلى تقرير المانح', 'من نموذج المسح<br><span>إلى لوحة المؤشرات.</span>', 'بيانات توضيحية. إجابات المسح مرسومة بالأرقام، والمؤشر النحاسي هو المطلوب في التقرير.', 'n2_img.png', 420),
}
for n, (dark, d, lbl, h1, src, img, top) in P.items():
    html = f"""<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>
<div class='page{' dark' if dark else ''}' dir='{d}'><div class='art' style='top:{top}px;height:{1350-top-150}px;overflow:hidden'><img src='{img}'></div>
<div style='position:relative'><div class='lbl'>{lbl}</div><h1>{h1}</h1></div>
<div class='foot' dir='ltr'>{'<div class=src dir=rtl style="text-align:right;order:2">' + src + '</div>' if d == 'rtl' else '<div class=src>' + src + '</div>'}{LD if dark else LL}</div></div></body></html>"""
    open(n + '.html', 'w').write(html)
