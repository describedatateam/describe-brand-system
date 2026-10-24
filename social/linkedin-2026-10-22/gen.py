# Images for the LinkedIn posts scheduled 25-26 Oct 2026 (same grammar as social/linkedin-2026-10/gen.py)
B='/home/claude/describe-brand-system'
F=B+'/decisions/fonts/'
lock_dark=open(B+'/wordmark/lockup-horizontal-compact-dark.svg').read()
lock_light=open(B+'/wordmark/lockup-horizontal-compact-light.svg').read()
NAVY,BLUE,CORAL,GREY,LG,OFF='#092052','#0F58E5','#E5484D','#64748B','#CBD5E1','#F6F8FC'
css=f"""
@font-face{{font-family:Fraunces;src:url('file://{F}Fraunces%255BSOFT,WONK,opsz,wght%255D.ttf')}}
@font-face{{font-family:Readex;src:url('file://{F}ReadexPro%255BHEXP,wght%255D.ttf')}}
@font-face{{font-family:Plex;src:url('file://{F}IBMPlexMono-Regular.ttf');font-weight:400}}
@font-face{{font-family:Plex;src:url('file://{F}IBMPlexMono-Medium.ttf');font-weight:500}}
*{{margin:0;box-sizing:border-box}}
html,body{{width:1080px;height:1350px}}
.page{{width:1080px;height:1350px;padding:96px 88px 80px;display:flex;flex-direction:column;position:relative;overflow:hidden;background:{OFF};color:{NAVY};font-family:Readex;font-weight:300}}
.dark{{background:{NAVY};color:{OFF}}}
h1{{font-family:Fraunces;font-weight:300;font-variation-settings:'SOFT' 0,'WONK' 0;font-size:84px;line-height:1.06;letter-spacing:-1.5px}}
.lbl{{font-family:Plex;font-weight:500;font-size:22px;letter-spacing:3px;text-transform:uppercase;color:{GREY}}}
.dark .lbl{{color:#8A99B0}}
.mono{{font-family:Plex;font-weight:500}}
.sub{{font-size:34px;line-height:1.4;color:{GREY}}}
.dark .sub{{color:#C9D3E6}}
.foot{{margin-top:auto;display:flex;justify-content:space-between;align-items:flex-end;gap:40px}}
.foot svg{{height:46px;width:auto}}
.src{{font-size:20px;color:{GREY};max-width:600px;line-height:1.4}}
.dark .src{{color:#8A99B0}}
.ring{{position:absolute;border-radius:50%;border:2px solid}}
.row{{border-top:2px solid {LG};padding:30px 0;display:flex;gap:36px;align-items:baseline}}
.dark .row{{border-color:#1E3A6B}}
"""
def page(body,dark=False,src=''):
    lock=lock_dark if dark else lock_light
    return f"<div class='page {'dark' if dark else ''}'>{body}<div class='foot'><div class='src'>{src}</div>{lock}</div></div>"
def doc(p): return f"<!doctype html><html><head><meta charset='utf-8'><style>{css}</style></head><body>{p}</body></html>"
out={}
# C1 company: the agent suggests, you approve
checks=[('01','What each product earned after returns'),('02','How many of its orders were refused or sent back'),('03','What it sold in the same weeks last year')]
rows=''.join(f"<div class='row'><div class='mono' style='font-size:30px;color:#8A99B0'>{n}</div><div style='font-size:38px;line-height:1.35;color:#C9D3E6'>{t}</div></div>" for n,t in checks)
out['c1']=doc(page(f"""
<div class='ring' style='width:1100px;height:1100px;right:-560px;top:-420px;border-color:#1B3470'></div>
<div class='lbl'>AI agents for stores</div>
<h1 style='margin-top:36px;font-size:96px'>The agent suggests.<br><span style='color:#4F86F7'>You approve.</span></h1>
<div style='margin-top:64px;border:2px solid #3A5487;border-radius:14px;padding:30px 34px;display:flex;justify-content:space-between;align-items:center'>
<div><div class='lbl' style='font-size:18px'>Suggested action</div><div style='font-size:38px;margin-top:10px'>Put 40 products on clearance</div></div>
<div class='mono' style='font-size:26px;border:2px solid #4F86F7;color:#4F86F7;border-radius:10px;padding:14px 24px'>Approve?</div></div>
<div class='lbl' style='margin-top:64px;margin-bottom:8px'>Before you click, know</div>{rows}
""",dark=True,src='Example: Lightspeed AI previews each change and waits for approval (Oct 2026).'))
# C2 company: where returns hide
hide=[('01','Sent back','Products returned after delivery'),('02','Refused at the door','Cash-on-delivery orders that never paid'),('03','Hidden in sales','Refunds sitting in the same export as sales')]
rows=''.join(f"<div class='row'><div class='mono' style='font-size:30px;color:{CORAL}'>{n}</div><div><div style='font-size:44px'>{a}</div><div style='font-size:28px;color:{GREY};margin-top:6px'>{b}</div></div></div>" for n,a,b in hide)
out['c2']=doc(page(f"""<div class='lbl'>Gulf online stores</div>
<h1 style='margin-top:32px'>Returns hide in three places.</h1>
<div style='margin-top:72px'>{rows}</div>
<div style='margin-top:20px;border-top:2px solid {LG};padding-top:36px'><div class='lbl'>Three numbers to track</div>
<div style='display:flex;gap:18px;margin-top:22px;flex-wrap:wrap'>
{''.join(f"<div class='mono' style='font-size:24px;background:#E8EEFB;color:{BLUE};border-radius:10px;padding:14px 20px'>{t}</div>" for t in ['Return rate by product','Refused COD share','Revenue after returns'])}
</div></div>""",src='No returns platform needed. A clean orders export is enough.'))
# P1 personal: what I changed
def col(tag,title,lines,accent,bg):
    l=''.join(f"<div style='font-size:30px;margin-top:16px;color:{GREY}'>{x}</div>" for x in lines)
    return f"<div style='flex:1;background:{bg};border-radius:16px;padding:36px'><div class='lbl' style='color:{accent}'>{tag}</div><div style='font-family:Fraunces;font-weight:300;font-size:52px;line-height:1.1;margin-top:18px'>{title}</div>{l}</div>"
out['p1']=doc(page(f"""<div class='lbl'>Building .describe( in public</div>
<h1 style='margin-top:32px'>This week I changed what I'm offering.</h1>
<div style='display:flex;gap:28px;margin-top:64px'>
{col('Before','$50 profit breakdown',['~40 stores emailed','A few auto-replies','0 booked'],GREY,'#EDF1F7')}
{col('Now','Free Black Friday baseline',['12 stores so far','Feedback in return','Too early to tell'],BLUE,'#E8EEFB')}
</div>
<div class='sub' style='margin-top:56px'>A deadline everyone already feels beats a nice idea with no date.</div>
<div class='mono' style='font-size:26px;color:{BLUE};margin-top:20px'>White Friday · 27 Nov</div>""",src='Outreach from Oct 6 to Oct 20, 2026.'))
# P2 personal: 9 days to 1, and the COD wait
steps=['Order','Delivered','Refused?','Cash in bank']
tl=''.join(f"<div style='flex:1;text-align:center'><div style='width:26px;height:26px;border-radius:50%;margin:0 auto;background:{CORAL if s=='Refused?' else '#4F86F7'}'></div><div style='font-size:26px;margin-top:16px;color:#C9D3E6'>{s}</div></div>" for s in steps)
out['p2']=doc(page(f"""
<div class='ring' style='width:1000px;height:1000px;right:-520px;top:-380px;border-color:#1B3470'></div>
<div class='lbl'>UAE tourist VAT refunds</div>
<div style='display:flex;align-items:baseline;gap:30px;margin-top:40px'>
<div class='mono' style='font-size:150px;color:#8A99B0'>9</div><div style='font-size:40px;color:#8A99B0'>days</div>
<div class='mono' style='font-size:70px;color:#8A99B0'>→</div>
<div class='mono' style='font-size:190px;color:#4F86F7'>1</div>
<div style='font-size:40px;color:#C9D3E6'>business day</div></div>
<h1 style='margin-top:110px;font-size:80px'>Now measure your own wait: cash on delivery.</h1>
<div style='position:relative;margin-top:120px'><div style='position:absolute;left:12%;right:12%;top:12px;height:2px;background:#3A5487'></div><div style='display:flex;position:relative'>{tl}</div></div>
<div class='mono' style='font-size:34px;color:#4F86F7;margin-top:56px;text-align:center'>Order to cash: ? days</div>
""",dark=True,src='Source: The National, 21 Oct 2026 (Federal Tax Authority and Planet).'))
for k,v in out.items(): open(k+'.html','w').write(v)
