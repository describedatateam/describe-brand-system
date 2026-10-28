from engine import *
W,H=1080,1000
# a wave made of cells that dissolves into the sky
x=np.linspace(0,1,W)[None,:]; y=np.linspace(0,1,H)[:,None]
crest=0.42+0.18*np.sin(x*5.2+0.6)+0.07*np.sin(x*17)+0.03*np.sin(x*41)
body=np.clip((y-crest)*6,0,1)
tex=fbm(H,W,6,33,6)
img=np.clip(body*(0.35+0.9*tex),0,1)
diss=np.clip(1-(y-crest+0.12)*5,0,1)*0.9
cells,gw,gh=dither_cells(img,cell=20,dissolve=diss)
S=2; im=Image.new('RGB',(W*S,H*S),hexrgb('#F6F8FC')); d=ImageDraw.Draw(im)
lo=hexrgb('#C9D7F5'); hi=hexrgb('#0F58E5'); dk=hexrgb('#092052')
for (cx,cy,v) in cells:
    col=lerp(lo,hi,min(1,v*1.3)) if v<0.75 else lerp(hi,dk,(v-0.75)*4)
    g=3 if v>0.5 else 5
    d.rectangle([cx*S+g,cy*S+g,(cx+20)*S-g,(cy+20)*S-g],fill=col)
    if 0.45<v<0.7 and rng.random()<0.25:  # outline cells, like a grid sketch
        d.rectangle([cx*S+g,cy*S+g,(cx+20)*S-g,(cy+20)*S-g],outline=hi,width=2,fill=hexrgb('#F6F8FC'))
im=im.resize((W,H),Image.LANCZOS); im.save('v3.png')
