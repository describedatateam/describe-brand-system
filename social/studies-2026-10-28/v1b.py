# S1 v2: crisp halftone planet rising, no glow or grain; highlight = real dots recoloured.
from engine import *
W,H=1080,800
D=1500
g=globe(D,seed=11)
img=np.zeros((H,W)); ox=(W-D)//2; oy=70
ys,ye=0,min(H,D+oy)
img[oy:H,:]=g[0:H-oy,-ox:-ox+W]
cell=16
dots=halftone(img,cell=cell,angle=0,gamma=1.1)
S=2; im=Image.new('RGB',(W*S,H*S),hexrgb('#092052')); d=ImageDraw.Draw(im)
lo=hexrgb('#2A4C9A'); hi=hexrgb('#DCE6FF'); hl=hexrgb('#E5484D')
cx,cy,rad=380,470,150   # region; only bright dots inside an irregular patch are recoloured
patch=fbm(H,W,5,77,6)
for x,y,r in dots:
    t=min(1,r/(cell*0.62)); col=lerp(lo,hi,t**1.2)
    dd=((x-cx)**2+(y-cy)**2)/rad**2
    if dd<1 and t>0.55 and patch[int(y),int(x)]>0.5+0.25*dd: col=hl
    rr=r*S; d.ellipse([x*S-rr,y*S-rr,x*S+rr,y*S+rr],fill=col)
im.resize((W,H),Image.LANCZOS).save('v1b.png')
