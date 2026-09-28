import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        for vw,vh in ((390,844),(1280,900)):
            pg=await b.new_page(viewport={'width':vw,'height':vh},reduced_motion='reduce')
            await pg.goto('file:///home/claude/website/_preview.html'); await pg.wait_for_timeout(500)
            r=await pg.evaluate("""()=>{
              const o={};
              const s=[...document.querySelectorAll('svg.dsc-chart')].filter(s=>s.getBoundingClientRect().width>0)[0];
              o.hitW=Math.min(...[...s.querySelectorAll('.c-hit')].map(h=>h.getBoundingClientRect().width)).toFixed(2);
              o.svgW=s.getBoundingClientRect().width;
              o.th=[...document.querySelectorAll('.twin__table thead th')].map(t=>getComputedStyle(t).fontSize+' '+getComputedStyle(t).fontFamily.split(',')[0]);
              o.small=[...document.querySelectorAll('a,button,summary,input,textarea')].filter(e=>{const r=e.getBoundingClientRect();return r.width>0&&r.height>0&&(r.height<24||r.width<24)&&!e.classList.contains('skip')&&!e.closest('.vh')}).map(e=>e.tagName+'.'+e.className+' '+Math.round(e.getBoundingClientRect().width)+'x'+e.getBoundingClientRect().height.toFixed(1)+' "'+e.textContent.trim().slice(0,30)+'"');
              return o;}""")
            print(vw,r)
            # focus test: tab through, check nothing focused sits under the nav
            under=[]; frames=set()
            for i in range(60):
                await pg.keyboard.press('Tab'); await pg.wait_for_timeout(60)
                info=await pg.evaluate("""()=>{const a=document.activeElement;if(!a||a===document.body)return null;
                  const r=a.getBoundingClientRect();const n=document.getElementById('nav').getBoundingClientRect();
                  const cs=getComputedStyle(a);const af=getComputedStyle(a,'::after');
                  return {t:a.tagName+'.'+(a.className.baseVal??a.className),top:r.top,navB:n.bottom,inNav:!!a.closest('#nav'),
                    ol:cs.outlineColor+' '+cs.outlineStyle, frame:af.content!=='none'&&af.backgroundImage!=='none',
                    tip:document.getElementById('tip').classList.contains('on')}}""")
                if not info: continue
                if 'skip' not in info['t'] and not info['inNav'] and info['top']<info['navB']-1: under.append((info['t'],round(info['top'])))
                frames.add((info['t'][:40],'frame' if info['frame'] else info['ol']))
                if 'c-hit' in info['t'] and vw==1280 and not under:
                    await pg.mouse.wheel(0,40); await pg.wait_for_timeout(120)
                    ok=await pg.evaluate("document.getElementById('tip').classList.contains('on')")
                    print('tooltip after scroll while focused:',ok); await pg.mouse.wheel(0,-40)
            print('under nav:',under[:5]); 
            for f in sorted(frames): print('  ',f)
            await pg.close()
        await b.close()
asyncio.run(main())
