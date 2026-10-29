# Lay the photo-sourced images out as 1080x1350 LinkedIn pages (same grammar as the 28 Oct studies).
import os
B = os.path.abspath('../..')
F = B + '/decisions/fonts/'
H = os.getcwd()
lock_dark = open(B + '/wordmark/lockup-horizontal-compact-dark.svg').read()
lock_light = open(B + '/wordmark/lockup-horizontal-compact-light.svg').read()
NAVY, BLUE, GREY, OFF, CREAM = '#092052', '#0F58E5', '#64748B', '#F6F8FC', '#F3EEE4'
css = f"""
@font-face{{font-family:Fraunces;src:url('file://{F}Fraunces%255BSOFT,WONK,opsz,wght%255D.ttf')}}
@font-face{{font-family:Readex;src:url('file://{F}ReadexPro%255BHEXP,wght%255D.ttf')}}
@font-face{{font-family:Plex;src:url('file://{F}IBMPlexMono-Medium.ttf');font-weight:500}}
*{{margin:0;box-sizing:border-box}}
html,body{{width:1080px;height:1350px}}
.page{{width:1080px;height:1350px;padding:96px 88px 80px;display:flex;flex-direction:column;position:relative;overflow:hidden;background:{OFF};color:{NAVY};font-family:Readex;font-weight:300}}
.dark{{background:{NAVY};color:{OFF}}}
h1{{font-family:Fraunces;font-weight:300;font-variation-settings:'SOFT' 0,'WONK' 0;font-size:88px;line-height:1.06;letter-spacing:-1.5px;margin-top:36px}}
.lbl{{font-family:Plex;font-weight:500;font-size:22px;letter-spacing:3px;text-transform:uppercase;color:{GREY}}}
.dark .lbl,.dark .src{{color:#8A99B0}}
.foot{{position:relative;z-index:5;margin-top:auto;display:flex;justify-content:space-between;align-items:flex-end;gap:40px}}
.foot svg{{height:46px;width:auto}}
.src{{font-size:20px;color:{GREY};max-width:620px;line-height:1.4}}
.art{{position:absolute;left:0;width:1080px}}
"""
def page(lbl, h1, art, src, dark=False, bg=None):
    lock = lock_dark if dark else lock_light
    st = f"style='background:{bg}'" if bg else ''
    return (f"<!doctype html><html><head><meta charset='utf-8'><style>{css}</style></head><body>"
            f"<div class='page {'dark' if dark else ''}' {st}>{art}<div style='position:relative'><div class='lbl'>{lbl}</div><h1>{h1}</h1></div>"
            f"<div class='foot'><div class='src'>{src}</div>{lock}</div></div></body></html>")
pages = {
 'p1': page('Type image · Study 01',
   "From far, one picture.<br><span style='color:#4F86F7'>Up close, all data.</span>",
   f"<div class='art' style='top:370px;height:800px;overflow:hidden;-webkit-mask-image:linear-gradient(#000 85%,transparent)'><img src='file://{H}/p1_img.png'></div>",
   'Earth photo redrawn in digits. The brass figures are the same digits, recoloured.', dark=True),
 'p2': page('Line field · Study 02',
   f"Every line is numbers.<br><span style='color:{BLUE}'>One of them is the story.</span>",
   f"<img class='art' src='file://{H}/p2_img.png' style='top:420px'>",
   'Sand ripples from a photo, each row set in digits; the blue row is the dune crest.', bg=CREAM),
 'p3': page('Dither · Study 03',
   f"Signal rises.<br><span style='color:{BLUE}'>Noise falls away.</span>",
   f"<img class='art' src='file://{H}/p3_img.png' style='top:150px'>",
   'A mountain ridge photo as dither cells. The summit cells are recoloured brass.'),
}
for k, v in pages.items(): open(k + '.html', 'w').write(v)
