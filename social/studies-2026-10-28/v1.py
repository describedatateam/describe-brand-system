from engine import *
W,H=1080,1000
g=globe(1000,seed=11)
img=np.zeros((H,W)); img[0:1000,40:1040]=g
dots=halftone(img,cell=11,angle=30,gamma=0.9)
navy=hexrgb('#092052'); 
S=2; im=Image.new('RGB',(W*S,H*S),navy); d=ImageDraw.Draw(im)
c_lo=hexrgb('#1B3A8A'); c_hi=hexrgb('#BFD3FF')
for x,y,r in dots:
    t=min(1,r/(11*0.62)); col=lerp(c_lo,c_hi,t**1.3)
    rr=r*S; d.ellipse([x*S-rr,y*S-rr,x*S+rr,y*S+rr],fill=col)
im=im.resize((W,H),Image.LANCZOS)
# atmosphere: glow from blurred copy + grain
glow=im.filter(ImageFilter.GaussianBlur(28)); im=Image.blend(im,Image.composite(glow,im,Image.new('L',(W,H),120)),0.5)
im=Image.fromarray(np.clip(np.asarray(im,float)+np.asarray(glow,float)*0.35,0,255).astype(np.uint8))
a=np.asarray(im,float); a+=rng.normal(0,6,a.shape[:2])[...,None]; im=Image.fromarray(np.clip(a,0,255).astype(np.uint8))
im.save('v1.png')
