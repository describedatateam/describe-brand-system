from engine import *
F='../../decisions/fonts/'
W,H=1080,980
im=Image.new('RGB',(W,H),hexrgb('#F4EEE2')); d=ImageDraw.Draw(im)
ink=hexrgb('#092052'); pale=hexrgb('#B9C3D8'); blue=hexrgb('#0F58E5')
rows=34; step=14
def ridge(x,k):
    t=k/rows
    return (90*np.exp(-((x-0.62)/0.16)**2)+55*np.exp(-((x-0.25)/0.12)**2)+18*np.sin(x*19+k*0.4))*(0.25+t)
hl=21
for k in range(rows):
    t=k/(rows-1); size=int(11+t*9)
    font=ImageFont.truetype(F+'IBMPlexMono-Medium.ttf',size)
    y0=120+k*(H-200)/rows
    x=0
    while x<W:
        xf=x/W; y=y0-ridge(xf,k)
        col=blue if k==hl else lerp(pale,ink,t**0.8)
        ch=str(int(rng.random()*10))
        if k==hl or rng.random()>0.15*(1-t): d.text((x,y),ch,font=font,fill=col)
        x+=size*0.62
im.save('v2.png')
