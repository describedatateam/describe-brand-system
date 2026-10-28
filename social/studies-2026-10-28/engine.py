# Halftone / dither / digit engine for .describe( studies. Procedural sources only (no stock photos).
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
rng=np.random.default_rng(7)

def fbm(h,w,octaves=6,seed=1,scale=3.0):
    r=np.random.default_rng(seed); out=np.zeros((h,w)); amp=1; tot=0
    for o in range(octaves):
        n=int(scale*2**o)+2
        g=r.random((n,n))
        im=Image.fromarray((g*255).astype(np.uint8)).resize((w,h),Image.BICUBIC)
        out+=amp*np.asarray(im,float)/255; tot+=amp; amp*=0.5
    return out/tot

def globe(size=1400,seed=3):
    y,x=np.mgrid[-1:1:size*1j,-1:1:size*1j]
    r2=x*x+y*y; inside=r2<=1
    z=np.sqrt(np.clip(1-r2,0,1))
    # spherical texture coords
    lon=np.arctan2(x,z); lat=np.arcsin(np.clip(y,-1,1))
    u=((lon/np.pi+1)/2); v=(lat/np.pi+0.5)
    T=fbm(900,1800,8,seed,5)
    land=T[(v*899).astype(int),(u*1799).astype(int)]
    C=fbm(900,1800,7,seed+9,7)
    cloud=C[(v*899).astype(int),(u*1799).astype(int)]
    L=np.array([-0.45,-0.35,0.82]); L/=np.linalg.norm(L)
    shade=np.clip(x*L[0]+y*L[1]+z*L[2],0,1)
    base=np.where(land>0.53,0.62+1.2*(land-0.53),0.26+0.25*land)
    base=base+np.clip((cloud-0.56)*2.6,0,0.7)
    img=np.clip(base*(0.15+0.95*shade),0,1)
    rim=np.exp(-((np.sqrt(r2)-1)**2)/0.0009)*0.6
    img=np.where(inside,img,0)+rim*(1-inside)*0.8
    return img

def terrain(w=1400,h=1100,seed=5):
    T=fbm(h,w,7,seed,2)
    gy,gx=np.gradient(T)
    shade=np.clip(0.5-gx*60-gy*40,0,1)
    return shade

def halftone(img,cell=14,angle=45,gamma=1.0):
    """AM halftone: returns list of (x,y,r) dots on a rotated grid."""
    h,w=img.shape; a=np.deg2rad(angle); dots=[]
    diag=int(np.hypot(w,h)/cell)+2
    for i in range(-diag,diag):
        for j in range(-diag,diag):
            cx=w/2+(i*np.cos(a)-j*np.sin(a))*cell; cy=h/2+(i*np.sin(a)+j*np.cos(a))*cell
            if 0<=cx<w and 0<=cy<h:
                v=img[int(cy),int(cx)]**gamma
                if v>0.02: dots.append((cx,cy,v*cell*0.62))
    return dots

def bayer(n):
    if n==1: return np.array([[0]])
    b=bayer(n//2); return np.block([[4*b,4*b+2],[4*b+3,4*b+1]])

def dither_cells(img,cell=18,dissolve=None):
    """Pixel dither: coarse grid, Bayer threshold; dissolve map (0..1) thins cells out."""
    h,w=img.shape; gh,gw=h//cell,w//cell
    small=np.asarray(Image.fromarray((img*255).astype(np.uint8)).resize((gw,gh),Image.BOX),float)/255
    B=(bayer(4)+0.5)/16; out=[]
    for j in range(gh):
        for i in range(gw):
            v=small[j,i]; t=B[j%4,i%4]
            if dissolve is not None and rng.random()<dissolve[j*cell,i*cell]: continue
            if v>t*0.9: out.append((i*cell,j*cell,v))
    return out,gw,gh

def render_dots(dots,w,h,bg,fg,scale=2):
    im=Image.new('RGB',(w*scale,h*scale),bg); d=ImageDraw.Draw(im)
    for x,y,r in dots:
        r*=scale; d.ellipse([x*scale-r,y*scale-r,x*scale+r,y*scale+r],fill=fg)
    return im.resize((w,h),Image.LANCZOS)

def lerp(c1,c2,t):
    return tuple(int(a+(b-a)*t) for a,b in zip(c1,c2))
def hexrgb(h): h=h.lstrip('#'); return tuple(int(h[i:i+2],16) for i in (0,2,4))
