# Moodboard studies, 28 Oct 2026: halftone, digits, dither and the shape kit
B='/home/claude/describe-brand-system'
F=B+'/decisions/fonts/'
lock_dark=open(B+'/wordmark/lockup-horizontal-compact-dark.svg').read()
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
.dark{{background:{NAVY};color:{OFF}}}
h1{{font-family:Fraunces;font-weight:300;font-variation-settings:'SOFT' 0,'WONK' 0;font-size:84px;line-height:1.06;letter-spacing:-1.5px}}
.lbl{{font-family:Plex;font-weight:500;font-size:22px;letter-spacing:3px;text-transform:uppercase;color:{GREY}}}
.dark .lbl{{color:#8A99B0}}
.mono{{font-family:Plex;font-weight:500}}
.sub{{font-size:34px;line-height:1.4;color:{GREY}}}
.dark .sub{{color:#C9D3E6}}
.foot{{position:relative;z-index:5;margin-top:auto;display:flex;justify-content:space-between;align-items:flex-end;gap:40px}}
.foot svg{{height:46px;width:auto}}
.src{{font-size:20px;color:{GREY};max-width:600px;line-height:1.4}}
.dark .src{{color:#8A99B0}}
.ring{{position:absolute;border-radius:50%;border:2px solid}}
.row{{border-top:2px solid {LG};padding:30px 0;display:flex;gap:36px;align-items:baseline}}
.dark .row{{border-color:#1E3A6B}}
"""
def page(body,dark=False,src=''):
    lock=lock_dark if dark else lock_light
    return f"<div class='page {'dark' if dark else ''}'>{body}<div class='foot'><div class='src'>{src}</div>{lock}</div></div>"
def doc(p): return f"<!doctype html><html><head><meta charset='utf-8'><style>{css}</style></head><body>{p}</body></html>"

from shapes import board, pattern, cell
import os
H=os.getcwd()
out={}
AST="<svg width='120' height='96' viewBox='0 0 120 96' style='position:absolute;{pos}'><g stroke='{c}' stroke-width='7' stroke-linecap='round' fill='none'><path d='M30 70 L110 8'/><path d='M30 46 V94 M9 58 L51 82 M9 82 L51 58'/></g></svg>"
def ast(pos,c='#4F86F7'): return AST.format(pos=pos,c=c)
# S1 halftone globe (dark)
out['s1']=doc(page(f"""
<div style='position:absolute;left:0;top:360px;width:1080px;height:830px;overflow:hidden'><img src='file://{H}/v1.png' style='position:absolute;left:150px;top:0;width:1080px;-webkit-mask-image:radial-gradient(circle at 50% 50%,#000 58%,transparent 70%)'></div>
<div style='position:absolute;left:0;right:0;top:0;height:560px;background:linear-gradient(#092052 60%,transparent)'></div>
<div style='position:relative'><div class='lbl'>Halftone · Study 01</div>
<h1 style='margin-top:36px;font-size:92px'>From far, one picture.<br><span style='color:#4F86F7'>Up close, all data.</span></h1></div>
{ast('left:560px;top:640px')}
<div style='position:absolute;left:540px;top:728px;width:14px;height:14px;border-radius:50%;background:{CORAL};box-shadow:0 0 24px {CORAL}'></div>
""",dark=True,src='Procedural globe, AM halftone at 30°, glow and grain. No stock photo.').replace("class='page dark'","class='page dark' style='background:#092052'"))
# S2 digits field (cream)
out['s2']=doc(page(f"""
<div class='lbl' style='color:#7A6A4F'>Digits · Study 02</div>
<h1 style='margin-top:36px'>Every line is numbers.<br><span style='color:{BLUE}'>One of them is the story.</span></h1>
<div style='position:absolute;left:0;top:330px;width:1080px;height:860px;overflow:hidden'><img src='file://{H}/v2.png' style='width:1080px'></div>
{ast('left:600px;top:650px',BLUE)}
""",src='Each row is drawn from digits; the blue row is the highlight.').replace("class='page '","class='page' style='background:#F4EEE2'"))
# S3 dither wave (light)
out['s3']=doc(page(f"""
<div style='position:absolute;left:0;top:250px;width:1080px;height:940px;overflow:hidden'><img src='file://{H}/v3.png' style='width:1080px'></div>
<div style='position:relative'><div class='lbl'>Dither · Study 03</div>
<h1 style='margin-top:36px'>Signal rises.<br><span style='color:{BLUE}'>Noise falls away.</span></h1></div>
{ast('left:700px;top:420px',CORAL)}
""",src='Bayer-dithered cells; density dissolves toward the edge.'))
# S4 shape kit board
kit=board(904,904,4,[NAVY,BLUE,NAVY,CORAL],OFF,labels=True)
out['s4']=doc(page(f"""<div class='lbl'>Shape kit · Study 04</div>
<h1 style='margin-top:30px;font-size:72px'>Sixteen shapes from<br><span style='color:{BLUE}'>one bracket.</span></h1>
<div style='margin-top:40px'>{kit}</div>""",src='Built from the ( curve, the cursor bar and the asterisk.'))
# S5 brand pattern (navy)
pat=pattern(1080,1350,135,['quarter','paren','half','dot','leaf','bracket2','bars','star'],[BLUE,'#4F86F7',OFF,'#1E3A6B'],[NAVY,NAVY,'#0E2A63'],seed=11)
out['s5']=doc(f"""<div class='page dark' style='padding:0'>{pat}
<div style='position:absolute;left:88px;bottom:80px;right:88px;background:{NAVY};padding:44px 48px;border-radius:18px'>
<div class='lbl'>Pattern · Study 05</div>
<div style='font-family:Fraunces;font-weight:300;font-size:64px;line-height:1.08;margin-top:18px'>A pattern you can<br><span style='color:#4F86F7'>recognise as ours.</span></div>
<div style='margin-top:30px'>{lock_dark}</div></div></div>""")
for k,v in out.items(): open(k+'.html','w').write(v)
