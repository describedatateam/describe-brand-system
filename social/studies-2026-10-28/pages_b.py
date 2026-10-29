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
CO='#E5484D'
def star(y,size=64):
    bars=''.join(f"<rect x='44' y='2' width='12' height='96' rx='6' fill='{CO}' transform='rotate({a} 50 50)'/>" for a in (0,60,120))
    return f"<svg viewBox='0 0 100 100' width='{size}' height='{size}' style='position:absolute;left:88px;top:{y-size/2}px;z-index:6'>{bars}</svg>"
def split(seam,top,bottom,labels=('',''),src='',lock='dark',topbg=OFF):
    a,b=labels
    lk=lock_dark
    return doc(f"""<div class='page' style='padding:0'>
<div style='position:absolute;left:0;top:0;width:1080px;height:{seam}px;overflow:hidden;background:{topbg}'>{top}</div>
<div class='dark' style='position:absolute;left:0;top:{seam}px;width:1080px;height:{1350-seam}px;overflow:hidden;background:{NAVY};color:{OFF}'>{bottom}<div style='position:absolute;left:0;right:0;bottom:0;height:150px;background:{NAVY}'></div></div>
<div style='position:absolute;left:60px;top:{seam-60}px;width:120px;height:60px;background:{topbg};z-index:5'></div>
<div style='position:absolute;left:60px;top:{seam}px;width:120px;height:60px;background:{NAVY};z-index:5'></div>
{star(seam)}

<div style='position:absolute;left:88px;right:88px;bottom:72px;display:flex;justify-content:space-between;align-items:flex-end;z-index:6'>
<div class='src' style='color:#8A99B0'>{src}</div><div class='lk'>{lk}</div></div>
</div>""")
HEAD=lambda lbl,l1,l2: f"<div style='padding:96px 88px 0;position:relative;z-index:3'><div class='lbl'>{lbl}</div><h1 style='margin-top:36px'>{l1}<br><span style='color:{BLUE}'>{l2}</span></h1></div>"
# S1
seam=440
out['s1b']=split(seam,HEAD('Halftone · Study 01','From far, one picture.','Up close, all data.'),
  f"<img src='file://{H}/v1b.png' style='position:absolute;left:0;top:-10px;width:1080px'>",
  ('From far','Up close'),'Procedural globe, halftone dots. The red dots are the same dots, recoloured.')
# S2: same field, cream above the seam, navy below
seam=760; off=330
out['s2b']=split(seam,f"<img src='file://{H}/v2_light.png' style='position:absolute;left:0;top:{off}px;width:1080px'>"+HEAD('Digits · Study 02','Every line is numbers.','One of them is the story.'),
  f"<img src='file://{H}/v2_dark.png' style='position:absolute;left:0;top:{off-seam}px;width:1080px'>",
  ('The story','The rest'),'Each row is drawn from digits; the blue row is the highlight.',topbg='#F4EEE2')
# S3
seam=820; off=300
out['s3b']=split(seam,f"<img src='file://{H}/v3_light.png' style='position:absolute;left:0;top:{off}px;width:1080px'>"+HEAD('Dither · Study 03','Signal rises.','Noise falls away.'),
  f"<img src='file://{H}/v3_dark.png' style='position:absolute;left:0;top:{off-seam}px;width:1080px'>",
  ('Noise','Signal'),'Bayer-dithered cells; density dissolves toward the edge.')
for k in out: out[k]=out[k].replace('</style>','.lk svg{height:46px;width:auto}</style>')
for k,v in out.items(): open(k+'.html','w').write(v)
