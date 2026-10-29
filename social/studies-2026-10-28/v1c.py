# S1 v3, the S2 route: the globe is drawn in digits (moodboard: ASCII figures, type-as-image).
# Brightness picks the glyph weight and tint; the highlight is the same digits, recoloured.
from engine import *
F='../../decisions/fonts/'
W,H=1080,860
D=1500
g=globe(D,seed=11)
img=np.zeros((H,W)); ox=(W-D)//2; oy=60
img[oy:H,:]=g[0:H-oy,-ox:-ox+W]
patch=fbm(H,W,5,77,6)
r=np.random.default_rng(2)
S=2; im=Image.new('RGB',(W*S,H*S),hexrgb('#092052')); d=ImageDraw.Draw(im)
fr=ImageFont.truetype(F+'IBMPlexMono-Regular.ttf',15*S); fm=ImageFont.truetype(F+'IBMPlexMono-Medium.ttf',15*S)
lo=hexrgb('#1E3A6B'); hi=hexrgb('#E6EFFF'); hl=hexrgb('#DBB477')
cw,ch=10,17
cx,cy,rad=380,470,150
for j in range(0,H,ch):
    for i in range(0,W,cw):
        v=img[j,i]
        if v<0.06: continue
        c=lerp(lo,hi,min(1,v**1.7*1.3))
        dd=((i-cx)**2+(j-cy)**2)/rad**2
        if dd<1 and v>0.55 and patch[j,i]>0.5+0.25*dd: c=hl
        glyph=str(int(r.random()*10)) if v>0.22 else ('.' if v<0.12 else ':')
        d.text((i*S,j*S),glyph,font=fm if v>0.5 else fr,fill=c)
im.resize((W,H),Image.LANCZOS).save('v1c.png')
