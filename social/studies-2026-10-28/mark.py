# The .describe( star mark: six arms, one colour (brass 400), and an optional tail that
# continues one arm exactly along the brand sight axis (θ = 40.6°, charts/kit SIGHT).
import math
BRASS='#BF8F3C'; THETA=40.6
def star_svg(size=64,tail=0,stroke=11,color=BRASS):
    """size = arm span; tail = extra length along θ, measured from the arm tip."""
    r=size/2; L=r+tail; pad=stroke
    # canvas: centre at bottom-left enough for the tail up-right
    cx=r+pad; w=cx+L*math.cos(math.radians(THETA))+pad; cy=L*math.sin(math.radians(THETA))+pad if tail else r+pad
    h=cy+r+pad
    lines=[]
    for k in range(3):
        a=math.radians(THETA+60*k)
        lines.append((cx-r*math.cos(a),cy+r*math.sin(a),cx+r*math.cos(a),cy-r*math.sin(a)))
    if tail:
        a=math.radians(THETA)
        x1,y1,x2,y2=lines[0]
        lines[0]=(x1,y1,cx+L*math.cos(a),cy-L*math.sin(a))  # one continuous stroke: arm + tail
    p=''.join(f"<line x1='{a:.2f}' y1='{b:.2f}' x2='{c:.2f}' y2='{d:.2f}'/>" for a,b,c,d in lines)
    return w,h,cx,cy,f"<svg xmlns='http://www.w3.org/2000/svg' width='{w:.0f}' height='{h:.0f}' viewBox='0 0 {w:.2f} {h:.2f}'><g stroke='{color}' stroke-width='{stroke}' stroke-linecap='round'>{p}</g></svg>"
