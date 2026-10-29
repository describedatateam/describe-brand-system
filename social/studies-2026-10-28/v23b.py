# Two-palette renders for the split pages (S2 digits, S3 dither); composited at the seam in the page.
from engine import *
import sys
F='../../decisions/fonts/'
def digits(bg,pale,ink,hlc,out,seed=7):
    r=np.random.default_rng(seed)
    W,H=1080,980
    im=Image.new('RGB',(W,H),hexrgb(bg)); d=ImageDraw.Draw(im)
    rows=34
    def ridge(x,k):
        t=k/rows
        return (90*np.exp(-((x-0.62)/0.16)**2)+55*np.exp(-((x-0.25)/0.12)**2)+18*np.sin(x*19+k*0.4))*(0.25+t)
    hl=12
    for k in range(rows):
        t=k/(rows-1); size=int(11+t*9)
        font=ImageFont.truetype(F+'IBMPlexMono-Medium.ttf',size)
        y0=120+k*(H-200)/rows; x=0
        while x<W:
            y=y0-ridge(x/W,k)
            col=hexrgb(hlc) if k==hl else lerp(hexrgb(pale),hexrgb(ink),t**0.8)
            ch=str(int(r.random()*10)); keep=r.random()>0.15*(1-t)
            if k==hl or keep: d.text((x,y),ch,font=font,fill=col)
            x+=size*0.62
    im.save(out)
digits('#F4EEE2','#B9C3D8','#092052','#0F58E5','v2_light.png')
digits('#092052','#2A4C9A','#C9D7F5','#0F58E5','v2_dark.png')
def wave(bg,lo,hi,dk,outline_bg,out):
    r=np.random.default_rng(3)
    W,H=1080,1000
    x=np.linspace(0,1,W)[None,:]; y=np.linspace(0,1,H)[:,None]
    crest=0.42+0.18*np.sin(x*5.2+0.6)+0.07*np.sin(x*17)+0.03*np.sin(x*41)
    body=np.clip((y-crest)*6,0,1); tex=fbm(H,W,6,33,6)
    img=np.clip(body*(0.35+0.9*tex),0,1)
    diss=np.clip(1-(y-crest+0.12)*5,0,1)*0.9
    global rng
    import engine; engine.rng=np.random.default_rng(5)
    cells,gw,gh=dither_cells(img,cell=20,dissolve=diss)
    S=2; im=Image.new('RGB',(W*S,H*S),hexrgb(bg)); d=ImageDraw.Draw(im)
    for (cx,cy,v) in cells:
        col=lerp(hexrgb(lo),hexrgb(hi),min(1,v*1.3)) if v<0.75 else lerp(hexrgb(hi),hexrgb(dk),(v-0.75)*4)
        g=3 if v>0.5 else 5
        d.rectangle([cx*S+g,cy*S+g,(cx+20)*S-g,(cy+20)*S-g],fill=col)
        if 0.45<v<0.7 and r.random()<0.25:
            d.rectangle([cx*S+g,cy*S+g,(cx+20)*S-g,(cy+20)*S-g],outline=hexrgb(hi),width=2,fill=hexrgb(outline_bg))
    im.resize((W,H),Image.LANCZOS).save(out)
wave('#F6F8FC','#C9D7F5','#0F58E5','#092052','#F6F8FC','v3_light.png')
wave('#092052','#1E3A6B','#4F86F7','#DCE6FF','#092052','v3_dark.png')
