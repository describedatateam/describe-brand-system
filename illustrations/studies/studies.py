import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi
import bitmap as B
S='/tmp/claude-0/-home-claude/4b7aacfc-1b57-5487-8c3e-f31920615e64/scratchpad/'
U='/mnt/user-data/uploads/arabia/'
GROUND=(246,248,252); INK=(9,32,82); BLUE=(15,88,229); FAINT=(190,203,224); BODY=(90,107,133)
TW,TH=900,700

def load(f, box, scale=0.5):
    im=Image.open(U+f if not f.startswith('sources') else f).crop(box)
    return im.resize((int(im.width*scale),int(im.height*scale)),Image.LANCZOS)

def layers(im):
    red,_=B.dot_layer(im,min_area=160)
    grey=B.grey_dot_layer(im)
    lines=B.line_layer(im,exclude=red|grey,min_blob=40)
    return lines,red,grey

def canvas(): 
    a=np.zeros((TH,TW,3),np.uint8); a[:]=GROUND; return a
def put(a,m,rgb,ox,oy):
    h,w=m.shape; sub=a[oy:oy+h,ox:ox+w]; mm=m[:TH-oy,:TW-ox]; sub[mm[:sub.shape[0],:sub.shape[1]]]=rgb
def fit(im,maxw,maxh):
    s=min(maxw/im.width,maxh/im.height); return im.resize((int(im.width*s),int(im.height*s)),Image.LANCZOS)

libra_globe=load('DP232533.jpg',(140,440,2080,1960),1.0)
cancer_globe=load('DP232528.jpg',(420,860,2000,1880),1.0)
cancer_sky=load('DP232528.jpg',(380,2380,1980,3440),1.0)
sky=Image.open(U+'11241855653_071d71380a_o.jpg').crop((0,100,1425,855))

studies=[]
# 1 plate — figure alone, quiet
a=canvas(); im=fit(libra_globe,760,600); L,R,G=layers(im)
ox,oy=(TW-im.width)//2,(TH-im.height)//2
put(a,L,INK,ox,oy); put(a,G,INK,ox,oy); put(a,R,BLUE,ox,oy); studies.append(('1  Plate: the figure alone',a))
# 2 stars first — data hero, figure as a dotted whisper
a=canvas(); put(a,B.dotted(L,3),BODY,ox,oy); put(a,G,INK,ox,oy); put(a,R,BLUE,ox,oy); studies.append(('2  Stars first: figure as a dotted trace',a))
# 3 two views — globe vs sky (mirror)
a=canvas(); w2=(TW-90)//2
for k,src in enumerate([cancer_globe,cancer_sky]):
    im=fit(src,w2,560); L2,R2,G2=layers(im); x=30+k*(w2+30)+(w2-im.width)//2; y=(TH-im.height)//2
    put(a,L2,INK,x,y); put(a,G2,INK,x,y); put(a,R2,BLUE,x,y)
a[70:TH-70,TW//2]=FAINT; studies.append(('3  Two views: on the globe / in the sky',a))
# 4 sky from the edge — dither fade, figure on clean paper
a=canvas(); sk=sky.resize((TW,int(sky.height*TW/sky.width)),Image.LANCZOS).crop((0,0,TW,TH)) if sky.height*TW/sky.width>=TH else sky.resize((int(sky.width*TH/sky.height),TH),Image.LANCZOS).crop((0,0,TW,TH))
sm=B.sky_layer(sk); fade=np.tile(np.clip(np.linspace(1.0,-1.3,TW),0,1)**0.7,(TH,1))
keep=B.ordered(fade,gamma=1.0,scale=1)
im=fit(libra_globe,520,560); L,R,G=layers(im); ox2,oy2=TW-im.width-40,(TH-im.height)//2
a[sm&keep]=FAINT; put(a,L,INK,ox2,oy2); put(a,G,INK,ox2,oy2); put(a,R,BLUE,ox2,oy2)
studies.append(('4  Sky from the edge: fades out before the figure',a))
# 5 detail — one pan, large, bleeding off
a=canvas(); det=load('DP232533.jpg',(1300,600,2080,1950),1.0); det=fit(det,1400,1100)
L5,R5,G5=layers(det); put(a,L5,INK,TW-600,-0 if False else 0) if False else None
h,w=L5.shape; x0,y0=TW-w+180,-120
for m,c in [(L5,INK),(G5,INK),(R5,BLUE)]:
    z=np.zeros((TH,TW),bool); ys=slice(max(0,y0),min(TH,y0+h)); xs=slice(max(0,x0),min(TW,x0+w))
    z[ys,xs]=m[ys.start-y0:ys.stop-y0, xs.start-x0:xs.stop-x0]; a[z]=c
studies.append(('5  Detail: one pan of the scales, cropped hard',a))
# 6 one material — sky stipple fills the frame, figure re-set as stipple
a=canvas(); a[sm]=FAINT
im=fit(cancer_sky,560,600); L,R,G=layers(im); ox3,oy3=(TW-im.width)//2,(TH-im.height)//2
sil=ndi.binary_dilation(ndi.binary_fill_holes(ndi.binary_closing(L|R|G,iterations=12)),iterations=10)
z=np.zeros((TH,TW),bool); z[oy3:oy3+im.height,ox3:ox3+im.width]=sil; a[z&sm]=GROUND
put(a,B.dotted(L,2)|ndi.binary_erosion(L,iterations=1),INK,ox3,oy3); put(a,G,INK,ox3,oy3); put(a,R,BLUE,ox3,oy3)
studies.append(('6  One material: sky and figure in the same stipple',a))

# sheet
pad=24; cap=40
sheet=Image.new('RGB',(3*TW+4*pad,2*(TH+cap)+3*pad),(226,231,240)); d=ImageDraw.Draw(sheet)
try: font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',24)
except: font=None
for i,(t,a) in enumerate(studies):
    x=pad+(i%3)*(TW+pad); y=pad+(i//3)*(TH+cap+pad)
    sheet.paste(Image.fromarray(a),(x,y+cap)); d.text((x,y+6),t,fill=INK,font=font)
    Image.fromarray(a).save(S+f'study{i+1}.png')
sheet.save(S+'studies.png'); sheet.resize((sheet.width//2,sheet.height//2),Image.LANCZOS).save(S+'studies_s.png')
print('ok')
