import json, sys
B='/home/claude/describe-brand-system'
F=B+'/decisions/fonts/'
fig=json.load(open(B+'/site/proof/figures.json'))
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
.src{{font-size:20px;color:{GREY};max-width:560px;line-height:1.4}}
.dark .src{{color:#8A99B0}}
.ring{{position:absolute;border-radius:50%;border:2px solid}}
"""
def page(body,dark=False,src=''):
    lock=lock_dark if dark else lock_light
    return f"<div class='page {'dark' if dark else ''}'>{body}<div class='foot'><div class='src'>{src}</div>{lock}</div></div>"
def doc(pages): return f"<!doctype html><html><head><meta charset='utf-8'><style>{css}</style></head><body>{''.join(pages)}</body></html>"
SRC='Source: Online Retail dataset (UCI, public), 542,014 rows, Dec 2010 to Dec 2011. Analysis by .describe('
out={}
# Post 1
out['post1']=doc([page(f"""
<div class='ring' style='width:1100px;height:1100px;right:-520px;top:-380px;border-color:#1B3470'></div>
<div class='ring' style='width:760px;height:760px;right:-350px;top:-210px;border-color:#1B3470'></div>
<div class='lbl' style='margin-top:40px'>Online stores</div>
<h1 style='margin-top:140px;font-size:110px'>Years of sales data.<br><span style='color:#4F86F7'>Not enough trust</span><br>to decide with it.</h1>
<div style='margin-top:120px;display:flex;flex-direction:column;gap:28px;font-size:38px;color:#C9D3E6'>
<div><span class='mono' style='color:#8A99B0;margin-right:22px'>01</span>Refunds mixed in with sales</div>
<div><span class='mono' style='color:#8A99B0;margin-right:22px'>02</span>Shipping counted as revenue</div>
<div><span class='mono' style='color:#8A99B0;margin-right:22px'>03</span>One cancelled order makes a best-seller</div></div>
""",dark=True)])
# Post 2
rows=fig['largest_sale_lines'][:3]
names={'581483':'Paper craft, little birdie','541431':'Ceramic storage jars','556444':'Wicker picnic baskets'}
r=''.join(f"""<div style='border-top:2px solid {LG};padding:26px 0;display:flex;justify-content:space-between;align-items:baseline'>
<div><div class='mono' style='font-size:92px;color:{CORAL};text-decoration:line-through;text-decoration-thickness:4px'>£{round(x['value']/1000)}K</div>
<div style='font-size:30px;color:{GREY};margin-top:6px'>{names[x['invoice']]}</div></div>
<div style='text-align:right'><div class='lbl'>Cancelled after</div><div class='mono' style='font-size:56px;margin-top:8px'>{x['minutes_later']} min</div></div></div>""" for x in rows)
out['post2']=doc([page(f"""<div class='lbl'>The 3 biggest order lines</div>
<h1 style='margin-top:32px'>The three biggest sales never happened.</h1>
<div style='margin-top:56px'>{r}</div>
<div class='sub' style='margin-top:8px;border-top:2px solid {LG};padding-top:28px'>Count them and they top your revenue, your product ranking and your customer list.</div>""",src=SRC)])
# Post 3
t1=round(fig['top_1pct_share_of_identified_net']*100); t20=round(fig['top_20pct_share_of_identified_net']*100); n=fig['identified_customers']
def bar(lbl,pct,col,who):
    return f"""<div style='margin-top:44px'><div style='display:flex;justify-content:space-between;align-items:baseline'><div style='font-size:34px'>{who}</div><div class='mono' style='font-size:72px;color:{col}'>{pct}%</div></div>
<div style='height:30px;background:#E2E8F0;margin-top:14px'><div style='height:100%;width:{pct}%;background:{col}'></div></div><div style='font-size:24px;color:{GREY};margin-top:10px'>{lbl}</div></div>"""
out['post3']=doc([page(f"""<div class='lbl'>Share of revenue</div>
<h1 style='margin-top:32px'><span class='mono' style='font-size:150px;letter-spacing:-4px;color:{BLUE}'>43</span> customers.<br>30% of revenue.</h1>
{bar(f'of revenue from identified customers',t1,BLUE,'Top 1% of customers (43)')}
{bar('of revenue from identified customers',t20,NAVY,f'Top 20% of customers ({round(n*0.2):,})')}
<div class='sub' style='margin-top:48px'>{n:,} customers ordered that year. Could you name your top 10?</div>""",src=SRC)])
# Post 4
months=[m for m in fig['monthly'] if m['month']!='2011-12']
mx=max(m['net'] for m in months)
MN=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
bars=''
for m in months:
    hi=m['month'] in ('2011-09','2011-10','2011-11'); h=m['net']/mx*560
    lab=f"<div class='mono' style='font-size:22px;color:{BLUE if hi else GREY};margin-bottom:8px'>£{m['net']/1e6:.2f}M</div>" if hi else ''
    bars+=f"<div style='flex:1;display:flex;flex-direction:column;justify-content:flex-end;align-items:center'>{lab}<div style='width:100%;height:{h}px;background:{BLUE if hi else LG}'></div><div class='mono' style='font-size:20px;color:{GREY};margin-top:12px'>{MN[int(m['month'][5:])-1]}</div></div>"
share=round(fig['sep_nov_share_of_net']*100)
out['post4']=doc([page(f"""<div class='lbl'>Net revenue by month</div>
<h1 style='margin-top:32px'>Sep, Oct and Nov brought in <span style='color:{BLUE}'>{share}%</span> of the year.</h1>
<div style='margin-top:64px;height:660px;display:flex;gap:14px;align-items:flex-end;border-bottom:2px solid {NAVY}'>{bars}</div>
<div style='display:flex;justify-content:space-between;font-size:22px;color:{GREY};margin-top:10px' class='mono'><span>Dec 2010</span><span>Nov 2011</span></div>""",src=SRC+'. Net of returns.')])
# Carousel
nums=[('Net revenue','Sales minus returns, cancellations and discounts.','The only revenue number worth reporting.'),
('Gross profit margin','Net revenue minus product cost, as a % of net revenue.','Sales can grow while profit shrinks.'),
('Number of orders','Completed orders, not cart sessions.','Tells you if growth is more buyers or bigger baskets.'),
('Average order value','Net revenue divided by orders.','Bundles and free-shipping thresholds move this.'),
('Return and cancellation rate','Returned or cancelled value as a % of sales.','A rising rate eats margin quietly.'),
('Returning-customer revenue','Share of revenue from people who bought before.','Cheaper to grow than new customers.'),
('Top-10 customer share','Share of revenue from your 10 biggest customers.','High share means high risk if one leaves.'),
('Ad spend per order','Total ad spend divided by orders it brought in.','Compare it with profit per order, not revenue.')]
pages=[page(f"""<div class='ring' style='width:1100px;height:1100px;right:-520px;top:-380px;border-color:#1B3470'></div>
<div class='lbl' style='margin-top:40px'>Monthly review</div><h1 style='margin-top:48px;font-size:110px'>8 numbers every online store should check monthly.</h1>
<div class='sub' style='margin-top:48px'>Not 40. Not a dashboard nobody opens. Eight.</div><div class='lbl' style='margin-top:auto;margin-bottom:40px;color:#4F86F7'>Swipe →</div>""",dark=True)]
for i,(a,b,c) in enumerate(nums,1):
    pages.append(page(f"""<div class='mono' style='font-size:200px;color:{BLUE};line-height:1'>{i:02d}</div>
<h1 style='margin-top:56px;font-size:92px'>{a}</h1>
<div style='margin-top:64px;border-top:2px solid {LG};padding-top:36px'><div class='lbl'>What it is</div><div style='font-size:40px;line-height:1.4;margin-top:14px'>{b}</div></div>
<div style='margin-top:40px;border-top:2px solid {LG};padding-top:36px'><div class='lbl'>Why it matters</div><div style='font-size:40px;line-height:1.4;margin-top:14px'>{c}</div></div>
<div class='mono' style='margin-top:auto;margin-bottom:36px;font-size:22px;color:{GREY}'>{i} / 8</div>"""))
pages.append(page(f"""<div class='lbl' style='margin-top:40px'>Your store</div><h1 style='margin-top:48px;font-size:100px'>Which one don't you track yet?</h1>
<div class='sub' style='margin-top:56px'>We turn your store's order export into these numbers, cleaned and checked.</div>
<div class='mono' style='margin-top:56px;font-size:44px;color:#4F86F7'>describe.team</div>""",dark=True))
out['post5']=doc(pages)
for k,v in out.items(): open(k+'.html','w').write(v)
