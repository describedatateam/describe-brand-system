# .describe( shape kit: modules on a 100-unit cell, drawn from the wordmark's "(" curve, the cursor bar and the asterisk.
import random
def M(name,c):
    s={
    'quarter':f"<path d='M0 100 A100 100 0 0 1 100 0 L100 100 Z' fill='{c}'/>",
    'paren':f"<path d='M70 0 A70 70 0 0 0 70 100 L100 100 A100 100 0 0 1 100 0 Z' transform='translate(-30 0)' fill='{c}'/>",
    'half':f"<path d='M0 50 A50 50 0 0 1 100 50 Z' fill='{c}'/>",
    'pill':f"<rect x='10' y='30' width='80' height='40' rx='20' fill='{c}'/>",
    'cursor':f"<rect x='42' y='0' width='16' height='100' fill='{c}'/>",
    'dot':f"<circle cx='50' cy='50' r='26' fill='{c}'/>",
    'ring':f"<circle cx='50' cy='50' r='34' fill='none' stroke='{c}' stroke-width='14'/>",
    'star':f"<path d='M50 0 C55 40 60 45 100 50 C60 55 55 60 50 100 C45 60 40 55 0 50 C40 45 45 40 50 0Z' fill='{c}'/>",
    'asterisk':''.join(f"<rect x='44' y='4' width='12' height='92' rx='6' fill='{c}' transform='rotate({a} 50 50)'/>" for a in (0,60,120)),
    'bars':''.join(f"<rect x='0' y='{y}' width='100' height='10' fill='{c}'/>" for y in (5,25,45,65,85)),
    'steps':f"<path d='M0 100 V70 H30 V40 H60 V10 H100 V100Z' fill='{c}'/>",
    'cross':f"<path d='M38 0H62V38H100V62H62V100H38V62H0V38H38Z' fill='{c}'/>",
    'leaf':f"<path d='M0 100 A100 100 0 0 1 100 0 A100 100 0 0 1 0 100Z' fill='{c}'/>",
    'grid':''.join(f"<rect x='{x}' y='{y}' width='16' height='16' fill='{c}'/>" for x in (8,42,76) for y in (8,42,76)),
    'wave':f"<path d='M0 60 C25 20 75 100 100 60 V100 H0Z' fill='{c}'/>",
    'bracket2':f"<path d='M100 0 A100 100 0 0 0 0 100 L30 100 A70 70 0 0 1 100 30Z' fill='{c}'/>",
    }[name]
    return s
NAMES=['quarter','paren','half','pill','cursor','dot','ring','star','asterisk','bars','steps','cross','leaf','grid','wave','bracket2']
def cell(name,c,x,y,size,rot=0,bg=None):
    sc=size/100
    b=f"<rect width='100' height='100' fill='{bg}'/>" if bg else ''
    return f"<g transform='translate({x} {y}) scale({sc}) rotate({rot} 50 50)'>{b}{M(name,c)}</g>"
def board(w,h,cols,colors,bg,pad=0.18,labels=True,font='Plex',lab='#64748B'):
    size=w/cols; out=[]; k=0
    rows=int(h//size)
    for j in range(rows):
        for i in range(cols):
            n=NAMES[k%len(NAMES)]; c=colors[k%len(colors)]
            p=size*pad
            out.append(cell(n,c,i*size+p,j*size+p,size-2*p))
            if labels: out.append(f"<text x='{i*size+p}' y='{(j+1)*size-4}' font-family='{font}' font-size='13' fill='{lab}' letter-spacing='1'>{k+1:02d} {n.upper()}</text>")
            k+=1
    return f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{rows*size}' viewBox='0 0 {w} {rows*size}'>{''.join(out)}</svg>"
def pattern(w,h,size,names,colors,bgs,seed=4):
    r=random.Random(seed); out=[]
    for j in range(int(h//size)+1):
        for i in range(int(w//size)+1):
            out.append(cell(r.choice(names),r.choice(colors),i*size,j*size,size,r.choice([0,90,180,270]),bg=r.choice(bgs)))
    return f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}' viewBox='0 0 {w} {h}'>{''.join(out)}</svg>"
