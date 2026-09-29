"""hero_cut.py — the hero: a dithered field with an astrolabe cut into it.
A: the .describe( 5a mark knocked out of a dithered Milky Way.
B: the manuscript astrolabe plate knocked out of the same field."""
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import bitmap as B
S='/tmp/claude-0/-home-claude/4b7aacfc-1b57-5487-8c3e-f31920615e64/scratchpad/'
U='/mnt/user-data/uploads/arabia/'
W,H=1400,1000
PAL={'light':dict(ground=(246,248,252),ink=(9,32,82),blue=(15,88,229)),
     'dark':dict(ground=(5,15,46),ink=(52,84,150),blue=(91,141,240))}

def field():
    sky=Image.open(U+'11241855653_071d71380a_o.jpg').crop((0,100,1425,855)).convert('L')
    s=max(W/sky.width,H/sky.height); sky=sky.resize((int(sky.width*s)+1,int(sky.height*s)+1),Image.LANCZOS)
    x0=(sky.width-W)//2; sky=sky.crop((x0,0,x0+W,H))
    g=np.asarray(sky,np.float32)/255
    g=ndi.gaussian_filter(g,1.2)
    dark=1-g
    lo,hi=np.quantile(dark,[.02,.98]); t=np.clip((dark-lo)/(hi-lo),0,1)
    t=0.08+0.62*t                      # never solid, never empty: a screen, not a photo
    return B.ordered(t,gamma=1.25,scale=2)

def mark_mask(size, stroke_boost=1):
    m=np.asarray(Image.open(S+'mark.png').convert('RGBA'))[...,3]>40
    im=np.asarray(Image.open(S+'mark.png').convert('RGB')).astype(int)
    stem=(im[...,2]>180)&(im[...,0]<80)&m
    ys,xs=np.where(m); y0,y1,x0,x1=ys.min(),ys.max(),xs.min(),xs.max()
    m=m[y0:y1+1,x0:x1+1]; stem=stem[y0:y1+1,x0:x1+1]
    s=size/max(m.shape)
    r=lambda a: np.asarray(Image.fromarray(a.astype(np.uint8)*255).resize((int(a.shape[1]*s),int(a.shape[0]*s)),Image.LANCZOS))>127
    m,stem=r(m),r(stem)
    if stroke_boost>1: m=ndi.binary_dilation(m,iterations=stroke_boost-1); stem=ndi.binary_dilation(stem,iterations=stroke_boost-1)
    return m,stem

def plate_mask(size):
    ast=Image.open(U+'Or 14270_0149.jpg').crop((70,110,820,900))
    s=size/max(ast.size); ast=ast.resize((int(ast.width*s),int(ast.height*s)),Image.LANCZOS)
    n=B.flatten(ast,30); m=n<0.86
    lab,k=ndi.label(m); sz=ndi.sum(m,lab,range(1,k+1)); keep=np.zeros(k+1,bool); keep[1:]=sz>=60
    return ndi.binary_dilation(keep[lab],iterations=1)

def place(m,cx,cy):
    z=np.zeros((H,W),bool); h,w=m.shape; y=int(cy-h/2); x=int(cx-w/2)
    ys=slice(max(0,y),min(H,y+h)); xs=slice(max(0,x),min(W,x+w))
    z[ys,xs]=m[ys.start-y:ys.stop-y, xs.start-x:xs.stop-x]; return z

F=field()
mA,stemA=mark_mask(820,stroke_boost=3)
A_cut=place(mA,W*0.56,H*0.5); A_stem=place(stemA,W*0.56,H*0.5)
mB=plate_mask(860); B_cut=place(mB,W*0.56,H*0.5)

for name,cut,fill in [('A-mark',A_cut,A_stem),('B-plate',B_cut,None)]:
    for th,p in PAL.items():
        out=np.zeros((H,W,3),np.uint8); out[:]=p['ground']
        out[F & ~cut]=p['ink']
        if fill is not None: out[fill]=p['blue']
        Image.fromarray(out).save(S+f'hero_{name}_{th}.png')
    B.to_png(F & ~cut, S+f'hero_{name}_field.png')
    if fill is not None: B.to_png(fill, S+f'hero_{name}_stem.png')
print('ok')


# ---------------------------------------------------------------- invert
def invert_cut(field, cut, sigma=5, thresh=0.30, halo=2):
    """The cut inverts against what's behind it, so it reads everywhere:
    over dense dither the lines are paper, over open paper they're ink.
    A thin halo in the opposite colour keeps every line crisp against the
    speckle."""
    dens = ndi.gaussian_filter(field.astype(np.float32), sigma)
    on_dark = dens > thresh
    ring = ndi.binary_dilation(cut, iterations=halo) & ~cut
    ink = field.copy()
    ink[ring & on_dark] = True        # solid ink behind paper lines
    ink[ring & ~on_dark] = False      # clear paper behind ink lines
    ink[cut & on_dark] = False        # line knocked out to paper
    ink[cut & ~on_dark] = True        # line drawn in ink
    return ink


if __name__ == '__main__':
    for name, cut, fill in [('B-plate-invert', B_cut, None), ('A-mark-invert', A_cut, A_stem)]:
        ink = invert_cut(F, cut)
        for th, p in PAL.items():
            out = np.zeros((H, W, 3), np.uint8); out[:] = p['ground']
            out[ink] = p['ink']
            if fill is not None: out[fill] = p['blue']
            Image.fromarray(out).save(S + f'hero_{name}_{th}.png')
        B.to_png(ink, S + f'hero_{name}_ink.png')
    print('invert ok')
