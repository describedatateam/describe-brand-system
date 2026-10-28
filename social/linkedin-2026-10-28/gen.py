# Images for the LinkedIn posts scheduled 28-29 Oct 2026 (same grammar as social/linkedin-2026-10/gen.py)
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
# C3 company (28 Oct): Power BI Desktop save-and-share
steps=[('01','Help → About','Check your version'),('02','Update Desktop','Microsoft Store or download'),('03','Save one report','to SharePoint, confirm it works'),('04','Tell the team','so everyone updates')]
rows=''.join(f"<div class='row'><div class='mono' style='font-size:30px;color:{BLUE}'>{n}</div><div><div style='font-size:42px'>{a}</div><div style='font-size:28px;color:{GREY};margin-top:6px'>{b}</div></div></div>" for n,a,b in steps)
out['c3']=doc(page(f"""<div class='lbl'>Power BI note · Oct 2026</div>
<h1 style='margin-top:32px'>Built March 2026 or earlier? <span style='color:{CORAL}'>Save &amp; share breaks.</span></h1>
<div class='sub' style='margin-top:30px'>Files still open. Saving to OneDrive and SharePoint doesn't.</div>
<div style='margin-top:56px'>{rows}</div>
<div class='mono' style='font-size:26px;color:{BLUE};margin-top:28px'>10 minutes</div>""",src='Source: Microsoft Learn, Power BI Desktop support policy.'))
# P3 personal (29 Oct): free snapshot, the first conversation
gets=['Revenue net of returns','Top products','Best customers','The season']
chips=''.join(f"<div style='font-size:44px;border-top:2px solid {LG};padding:34px 0;display:flex;gap:30px'><span style='display:inline-block;width:22px;height:22px;border-radius:50%;background:{BLUE};margin-top:16px;flex:none'></span>{g}</div>" for g in gets)
out['p3']=doc(page(f"""<div class='lbl'>Building .describe( in public</div>
<h1 style='margin-top:32px'>The hardest part isn't the analysis.<br><span style='color:{BLUE}'>It's the first conversation.</span></h1>
<div class='lbl' style='margin-top:72px;margin-bottom:10px'>Free sales snapshot, from your own data</div>{chips}
<div class='mono' style='font-size:30px;color:{BLUE};margin-top:44px'>In a few days · Arabic or English</div>""",src='Open to any online store.'))
# C4 company (29 Oct): data centres vs dashboards
def layer(tag,items,col,bg,bd):
    l=''.join(f"<div style='font-size:32px;margin-top:14px;color:{col}'>{x}</div>" for x in items)
    return f"<div style='background:{bg};border:2px solid {bd};border-radius:16px;padding:34px 38px'><div class='lbl'>{tag}</div>{l}</div>"
out['c4']=doc(page(f"""
<div class='ring' style='width:1100px;height:1100px;right:-580px;top:-430px;border-color:#1B3470'></div>
<div class='lbl'>The Gulf, 2026</div>
<h1 style='margin-top:32px'>The Gulf is building the data centres.<br><span style='color:#4F86F7'>Who builds the dashboards?</span></h1>
<div style='margin-top:64px'>{layer('Infrastructure layer',['<span class="mono" style="color:#4F86F7">80%+</span> of regional capacity in UAE + KSA by 2030','<span class="mono" style="color:#4F86F7">150 MW</span> first phase of Stargate UAE'],'#C9D3E6','#0E2A63','#1E3A6B')}</div>
<div style='margin-top:26px'>{layer('The layer a business touches',['An export from Salla, Zid or Shopify','A spreadsheet cleaned by hand every month','<span style="color:#F08A8D">A report the team half-trusts</span>'],'#C9D3E6','transparent','#3A5487')}</div>
<div class='sub' style='margin-top:56px'>Gigawatts don't fix that. A clean dataset and one honest dashboard do.</div>
""",dark=True,src='Sources: S&amp;P Global; G42.'))
for k,v in out.items(): open(k+'.html','w').write(v)
