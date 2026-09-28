"""web_assets.py — cut the illustration masks the homepage mock uses.
Each mask is a 2-colour palette PNG: index 1 opaque, index 0 transparent,
so CSS mask-image can colour it from a theme token."""
import base64, io, json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import bitmap as B
U='/mnt/user-data/uploads/arabia/'

def png(mask):
    a=mask.astype(np.uint8)
    im=Image.fromarray(a,'L').convert('P'); im.putpalette([0,0,0,0,0,0]+[0,0,0]*254)
    im=Image.fromarray(a).convert('P'); 
    im.putpalette([255,255,255, 0,0,0]); 
    bio=io.BytesIO(); im.save(bio,'PNG',transparency=0,optimize=True,bits=1)
    return 'data:image/png;base64,'+base64.b64encode(bio.getvalue()).decode()

def fit(im,w):
    return im.resize((w,int(im.height*w/im.width)),Image.LANCZOS)

def figure(im,min_area=120):
    red,_=B.dot_layer(im,min_area=min_area)
    grey=B.grey_dot_layer(im)
    lines=B.line_layer(im,exclude=red|grey,min_blob=30)
    return lines,red,grey

out={}
def add(name,im,layers):
    out[name]={'w':im.width,'h':im.height,'layers':{k:png(v) for k,v in layers.items()}}
    print(name,im.size,{k:len(v)//1024 for k,v in out[name]['layers'].items()})

# hero — Cygnus, stars first
cyg=fit(Image.open('sources/DP232491.jpg').crop((330,760,2380,3120)),760)
L,R,G=figure(cyg,min_area=60)
add('cygnus',cyg,{'lines':L,'dotted':B.dotted(L,3),'stars':R,'outside':G})
# service 1 — the two stars outside the figure (lower-left of Cygnus)
c1=fit(Image.open('sources/DP232491.jpg').crop((330,1700,1500,2800)),560)
L,R,G=figure(c1,min_area=40)
# the two stars al-Sufi labels خارجة عن الصورة — located by hand (curation, not detection)
n1=B.flatten(c1,25); yy,xx=np.mgrid[0:c1.height,0:c1.width]
near=np.zeros(n1.shape,bool)
for cx,cy in [(126,212),(168,256)]:
    near|=(xx-cx)**2+(yy-cy)**2<24**2
# drawn as the brand's own outlier marker (ring + dot), centred on each star
G=np.zeros(n1.shape,bool); clear=np.zeros(n1.shape,bool)
blob=ndi.binary_fill_holes((n1<0.72)&near); lab,k=ndi.label(blob)
for i in range(1,k+1):
    if (lab==i).sum()<40: continue
    cy,cx=ndi.center_of_mass(lab==i); d2=(xx-cx)**2+(yy-cy)**2
    G|=((d2<=14**2)&(d2>=11.5**2))|(d2<=5**2); clear|=d2<=17**2
L&=~clear
print('outside px',G.sum())
add('cyg_outside',c1,{'lines':L,'stars':R,'outside':G})
# service 2 — astrolabe plate, one ink
ast=Image.open(U+'Or 14270_0149.jpg').crop((70,110,820,900)); ast=fit(ast,620)
n=B.flatten(ast,20); m=n<0.86
lab,k=ndi.label(m); sz=ndi.sum(m,lab,range(1,k+1)); keep=np.zeros(k+1,bool); keep[1:]=sz>=25; m=keep[lab]
add('astrolabe',ast,{'lines':m})
# service 3 — Libra on the globe
lib=fit(Image.open(U+'DP232533.jpg').crop((140,700,2080,1960)),620)
L,R,G=figure(lib,min_area=60)
add('libra',lib,{'lines':L,'stars':R,'outside':G})
# method — Cancer, two views
for nm,box in [('cancer_globe',(420,860,2000,1880)),('cancer_sky',(380,2380,1980,3440))]:
    c=fit(Image.open(U+'DP232528.jpg').crop(box),520)
    L,R,G=figure(c,min_area=60)
    add(nm,c,{'lines':L,'stars':R,'outside':G})
# sky band — Milky Way strip, fading at both ends
sky=Image.open(U+'11241855653_071d71380a_o.jpg').crop((0,330,1425,610))
sky=fit(sky,1600)
sm=B.sky_layer(sky, glow_max=0.26)
x=np.linspace(0,1,sky.width); env=np.clip(np.minimum(x,1-x)*4,0,1)
sm&=B.ordered(np.tile(env,(sky.height,1)),gamma=1.0,scale=1)
add('skyband',sky,{'sky':sm})
json.dump(out,open('web_assets.json','w'))
print(sum(len(l) for a in out.values() for l in a['layers'].values())//1024,'KB total')
