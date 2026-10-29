# S3 v3: the dither wave, but cells turn into numbers as they dissolve (moodboard: binary rain, pixel waves).
from engine import *
import engine
F='../../decisions/fonts/'
def wave(bg,lo,hi,dk,out):
    engine.rng=np.random.default_rng(5); r=np.random.default_rng(3)
    W,H=1080,1000
    x=np.linspace(0,1,W)[None,:]; y=np.linspace(0,1,H)[:,None]
    crest=0.42+0.18*np.sin(x*5.2+0.6)+0.07*np.sin(x*17)+0.03*np.sin(x*41)
    body=np.clip((y-crest)*6,0,1); tex=fbm(H,W,6,33,6)
    img=np.clip(body*(0.35+0.9*tex),0,1)
    diss=np.clip(1-(y-crest+0.12)*5,0,1)*0.9
    cells,_,_=dither_cells(img,cell=20,dissolve=diss)
    S=2; im=Image.new('RGB',(W*S,H*S),hexrgb(bg)); d=ImageDraw.Draw(im)
    f=ImageFont.truetype(F+'IBMPlexMono-Medium.ttf',19*S)
    for (cx,cy,v) in cells:
        col=lerp(hexrgb(lo),hexrgb(hi),min(1,v*1.3)) if v<0.75 else lerp(hexrgb(hi),hexrgb(dk),(v-0.75)*4)
        if v<0.6:   # thin data: a number, not a block
            d.text((cx*S+3*S,cy*S-2*S),str(int(r.random()*10)),font=f,fill=col)
        else:
            d.rectangle([cx*S+3,cy*S+3,(cx+20)*S-3,(cy+20)*S-3],fill=col)
    im.resize((W,H),Image.LANCZOS).save(out)
wave('#F6F8FC','#98BBFB','#0F58E5','#092052','v3c_light.png')
wave('#092052','#2A4C9A','#6095FA','#E6EFFF','v3c_dark.png')
