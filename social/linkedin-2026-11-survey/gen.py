# Images for the Survey Analyzer pilot posts, Nov 2026 (same grammar as social/linkedin-2026-10-28/gen.py)
# The answer shown is made up, from the sample survey. Never a real person's words.
import os
B=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..'))
F=B+'/decisions/fonts/'
lock_light=open(B+'/wordmark/lockup-horizontal-compact-light.svg').read()
NAVY,BLUE,CORAL,GREY,LG,OFF='#092052','#0F58E5','#E5484D','#64748B','#CBD5E1','#F6F8FC'
css=f"""
@font-face{{font-family:Fraunces;src:url('file://{F}Fraunces%255BSOFT,WONK,opsz,wght%255D.ttf')}}
@font-face{{font-family:Readex;src:url('file://{F}ReadexPro%255BHEXP,wght%255D.ttf')}}
@font-face{{font-family:Plex;src:url('file://{F}IBMPlexMono-Regular.ttf');font-weight:400}}
@font-face{{font-family:Plex;src:url('file://{F}IBMPlexMono-Medium.ttf');font-weight:500}}
*{{margin:0;box-sizing:border-box}}
html,body{{width:1080px;height:1350px}}
.page{{width:1080px;height:1350px;padding:96px 88px 80px;display:flex;flex-direction:column;position:relative;overflow:hidden;background:{OFF};color:{NAVY};font-family:Readex;font-weight:300}}
h1{{font-family:Fraunces;font-weight:300;font-variation-settings:'SOFT' 0,'WONK' 0;font-size:80px;line-height:1.08;letter-spacing:-1.5px}}
[dir=rtl] h1{{font-family:Readex;font-weight:400;letter-spacing:0;line-height:1.3;font-size:68px}}
.lbl{{font-family:Plex;font-weight:500;font-size:22px;letter-spacing:3px;text-transform:uppercase;color:{GREY}}}
[dir=rtl] .lbl{{font-family:Readex;letter-spacing:0;font-size:26px}}
.mono{{font-family:Plex;font-weight:500}}
.card{{border-top:2px solid {LG};padding:30px 0 34px}}
.ans{{font-size:38px;line-height:1.45;margin-top:14px}}
.cut{{color:{CORAL};text-decoration:line-through;text-decoration-thickness:3px}}
.tag{{font-family:Plex;font-weight:500;font-size:30px;color:{BLUE};background:#E3ECFD;border-radius:8px;padding:2px 12px;unicode-bidi:isolate}}
.chip{{display:inline-block;font-size:28px;border:2px solid {BLUE};color:{BLUE};border-radius:40px;padding:8px 24px;margin:16px 14px 0 0}}
[dir=rtl] .chip{{margin:16px 0 0 14px}}
[dir=rtl] .ans{{line-height:1.75}}
.foot{{margin-top:auto;display:flex;justify-content:space-between;align-items:flex-end;gap:40px}}
.foot svg{{height:46px;width:auto}}
.src{{font-size:20px;color:{GREY};max-width:600px;line-height:1.4}}
"""
def page(body,src='',rtl=False):
    return f"<div class='page' dir='{'rtl' if rtl else 'ltr'}'>{body}<div class='foot'><div class='src'>{src}</div><div dir='ltr'>{lock_light}</div></div></div>"
def doc(p,lang='en'): return f"<!doctype html><html lang='{lang}'><head><meta charset='utf-8'><style>{css}</style></head><body>{p}</body></html>"
out={}
out['s1']=doc(page(f"""<div class='lbl'>Survey Analyzer · Pilot</div>
<h1 style='margin-top:32px'>Your survey answers hold the story. <span style='color:{BLUE}'>Not the names.</span></h1>
<div style='margin-top:64px'>
<div class='card'><div class='lbl'>Before</div><div class='ans'>“My name is <span class='cut'>Samir Haddad</span>, call me on <span class='cut'>0599 123 456</span>. We need clean water and the clinic is too far for my mother.”</div></div>
<div class='card'><div class='lbl'>After</div><div class='ans'>“My name is <span class='tag'>[NAME]</span>, call me on <span class='tag'>[PHONE]</span>. We need clean water and the clinic is too far for my mother.”</div>
<div><span class='chip'>Water</span><span class='chip'>Access to health care</span></div></div>
</div>
<div class='mono' style='font-size:28px;color:{BLUE};margin-top:20px'>Arabic + English · stays in your own account</div>""",src='A made-up answer from our sample survey.'))
out['s2']=doc(page(f"""<div class='lbl'>محلل الاستبيانات · تجربة</div>
<h1 style='margin-top:32px'>إجابات الاستبيان تحمل القصة. <span style='color:{BLUE}'>لا الأسماء.</span></h1>
<div style='margin-top:64px'>
<div class='card'><div class='lbl'>قبل</div><div class='ans'>«اسمي <span class='cut'>سمير حداد</span>، رقمي <span class='cut' dir='ltr' style='unicode-bidi:isolate'>0599 123 456</span>. نحتاج مياهاً نظيفة، والعيادة بعيدة جداً على والدتي.»</div></div>
<div class='card'><div class='lbl'>بعد</div><div class='ans'>«اسمي <span class='tag'>[الاسم]</span>، رقمي <span class='tag'>[الهاتف]</span>. نحتاج مياهاً نظيفة، والعيادة بعيدة جداً على والدتي.»</div>
<div><span class='chip'>المياه</span><span class='chip'>الوصول إلى الرعاية الصحية</span></div></div>
</div>
<div style='font-size:30px;color:{BLUE};margin-top:20px;font-weight:500'>بالعربية والإنجليزية · داخل حسابك أنت</div>""",src='إجابة مختلَقة من استبياننا التجريبي.',rtl=True),lang='ar')
for k,v in out.items(): open(os.path.join(os.path.dirname(os.path.abspath(__file__)),k+'.html'),'w').write(v)
