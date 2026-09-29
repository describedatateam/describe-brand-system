"""
shoot.py — render /home/claude/website/site.html the way a visitor sees it.

    python3 /home/claude/website/shoot.py [tag]

Google Fonts is blocked in this workspace, so the harness injects the real
brand fonts from local files (Fraunces, Readex Pro, Vazirmatn, Amiri,
IBM Plex Mono). The published page loads them from Google Fonts instead.

Writes to /home/claude/website/shots/:
    <tag>-desktop-light.png  <tag>-desktop-dark.png  (1280 wide, full page)
    <tag>-mobile-light.png   <tag>-mobile-dark.png   (390 wide, full page)
and prints: page height, horizontal overflow at 390px, console errors.
"""
import asyncio
import sys

from playwright.async_api import async_playwright

F = 'file:///home/claude/decisions/fonts/'
FONTS = f"""
@font-face{{font-family:'Fraunces';src:url('{F}Fraunces%255BSOFT,WONK,opsz,wght%255D.ttf');font-weight:100 900}}
@font-face{{font-family:'Readex Pro';src:url('{F}ReadexPro%255BHEXP,wght%255D.ttf');font-weight:160 700}}
@font-face{{font-family:'Vazirmatn';src:url('{F}Vazirmatn%255Bwght%255D.ttf');font-weight:100 900}}
@font-face{{font-family:'Amiri';src:url('{F}Amiri-Regular.ttf');font-weight:400}}
@font-face{{font-family:'IBM Plex Mono';src:url('{F}IBMPlexMono-Regular.ttf');font-weight:400}}
@font-face{{font-family:'IBM Plex Mono';src:url('{F}IBMPlexMono-Medium.ttf');font-weight:500}}
"""
SKELETON = ('<!doctype html><html><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
            '<style>' + FONTS + '</style></head><body>' + '{}' + '</body></html>')


async def main(tag):
    body = open('/home/claude/website/site.html', encoding='utf-8').read()
    open('/home/claude/website/_preview.html', 'w', encoding='utf-8').write(SKELETON.replace('{}', body, 1))
    out = '/home/claude/website/shots/'
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for name, vw, vh in (('desktop', 1280, 900), ('mobile', 390, 844)):
            for theme in ('light', 'dark'):
                pg = await b.new_page(viewport={'width': vw, 'height': vh})
                errs = []
                pg.on('pageerror', lambda e: errs.append(str(e)))
                pg.on('console', lambda m: m.type == 'error' and errs.append(m.text))
                await pg.goto('file:///home/claude/website/_preview.html')
                await pg.evaluate(f"document.documentElement.setAttribute('data-theme','{theme}')")
                await pg.wait_for_timeout(700)
                await pg.screenshot(path=f'{out}{tag}-{name}-{theme}.png', full_page=True)
                sw = await pg.evaluate('document.documentElement.scrollWidth')
                h = await pg.evaluate('document.documentElement.scrollHeight')
                print(f'{name}-{theme}: height {h}px, scrollWidth {sw}px (viewport {vw}), errors {errs}')
                await pg.close()
        await b.close()


if __name__ == '__main__':
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'v'))
