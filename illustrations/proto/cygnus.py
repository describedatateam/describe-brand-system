import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import bitmap as B
S='/tmp/claude-0/-home-claude/4b7aacfc-1b57-5487-8c3e-f31920615e64/scratchpad/'
U='/mnt/user-data/uploads/arabia/'
W,H=1800,1000
# sky: crop, scale to cover
sky=Image.open(U+'11241855653_071d71380a_o.jpg').crop((0,100,1425,855))
sky=sky.resize((int(sky.width*H/sky.height)+1,H),Image.LANCZOS).crop((0,0,W,H)) if sky.width*H/sky.height>=W else sky.resize((W,int(sky.height*W/sky.width)),Image.LANCZOS).crop((0,0,W,H))
skym=B.sky_layer(sky)
# figure
fig=Image.open('sources/DP232491.jpg').crop((330,760,2380,3120))
fh=int(H*0.94); fw=int(fig.width*fh/fig.height)
fig=fig.resize((fw,fh),Image.LANCZOS)
dots,stars=B.dot_layer(fig,min_area=40)
lines=B.line_layer(fig,exclude=dots)
sil=ndi.binary_fill_holes(ndi.binary_closing(lines|dots,iterations=10))
sil=ndi.binary_dilation(sil,iterations=14)
ox,oy=W-fw-60,(H-fh)//2
def place(m):
    z=np.zeros((H,W),bool); z[oy:oy+fh,ox:ox+fw]=m; return z
L,D,SIL=place(lines),place(dots),place(sil)
skym&=~SIL
for name,ground,cs,cl,cd in [('light',(246,248,252),(190,203,224),(9,32,82),(15,88,229)),('dark',(5,15,46),(40,66,120),(246,248,252),(91,141,240))]:
    B.compose([(skym,cs),(L,cl),(D,cd)],(W,H),ground,S+f'banner_{name}.png')
for n,m in [('sky',skym),('lines',L),('dots',D)]:
    B.to_png(m,S+f'mask_{n}.png')
import os; print({n:os.path.getsize(S+f'mask_{n}.png') for n in ['sky','lines','dots']}, len(stars))
