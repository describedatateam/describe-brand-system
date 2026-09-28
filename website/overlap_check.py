"""
overlap_check.py — label collisions inside every graphic, and clear space around
every big figure, at every width that matters.

    python3 /home/claude/website/overlap_check.py      (run shoot.py first: it writes _preview.html)

Widths: 320, 360, 390, 420, 768, 1280 px, light and dark.

1. Labels (every visible inline <svg>):
     OVERLAP   two labels whose ink boxes intersect
     OUTSIDE   a label that runs past its graphic's left or right edge
2. Clear space (founder, round 5; tiers from inspo/direction-r5.md). Every figure
   set in Fraunces must keep, to any other text, rule, leader or wedge:

     tier  figures                        above/below     sides   own label
     T1    hero figures (.rows__fig)      48 (24 mobile)  32      16 (12)
     T2    section numerals               40 (24)         24      tally 24 (16) below
     T3    findings, "Where we are"       24              16      16
     T4    service figures (.spec__v)     16              24      12
     T5    ruler values (hero vernier),   12              12      8
           stage numbers (Method)

     CLEAR     a gap smaller than its tier ("mobile" = viewport < 1000px)

Boxes are INK boxes, not line boxes: each run of text is measured with canvas
font metrics (actual ascent/descent of its own glyphs) and placed on its real
baseline, so line-gap space never counts. Obstacles are text, SVG strokes,
CSS borders and absolutely positioned pseudo-element rules.
Exemption: the page spine's section tick (.sech::before at >= 1000px) sits in
the margin by design, 24px outside the content edge; it is not an obstacle.
Exit status is 1 if anything is found.
"""
import asyncio
import sys

from playwright.async_api import async_playwright

WIDTHS = (320, 360, 390, 420, 768, 1280)
TOL = 0.5   # px of intersection allowed on each axis (anti-aliasing)

PROBE = r"""
(tol) => {
  const W = innerWidth, mobile = W < 1000;
  const vis = el => { if (el.closest('.vh')) return false; const r = el.getBoundingClientRect(); const cs = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && cs.display !== 'none' && +cs.opacity !== 0; };
  const cv = document.createElement('canvas').getContext('2d');
  const inkOf = (el, txt) => { const cs = getComputedStyle(el);
    cv.font = `${cs.fontStyle} ${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
    try { cv.letterSpacing = cs.letterSpacing === 'normal' ? '0px' : cs.letterSpacing; } catch (e) {}
    const m = cv.measureText(txt);
    return { fa: m.fontBoundingBoxAscent, fd: m.fontBoundingBoxDescent, a: m.actualBoundingBoxAscent, d: m.actualBoundingBoxDescent }; };
  // ink boxes for an HTML text node, one per line
  const htmlInk = node => { const el = node.parentElement, rg = document.createRange(); rg.selectNodeContents(node);
    const m = inkOf(el, node.textContent.trim());
    return [...rg.getClientRects()].filter(r => r.width > 0).map(r => { const base = r.top + m.fa * r.height / (m.fa + m.fd);
      return { l: r.left, r: r.right, t: base - m.a, b: base + m.d, txt: node.textContent.trim(), el }; }); };
  const svgInk = t => { const r = t.getBoundingClientRect(), m = inkOf(t, t.textContent), k = r.height / (m.fa + m.fd);
    const base = r.top + m.fa * k; return { l: r.left, r: r.right, t: base - m.a * k, b: base + m.d * k, txt: t.textContent.trim(), el: t, svg: true }; };
  const name = el => { const s = el.closest('svg'); const c = (s ? s : el).getAttribute('class') || el.tagName;
    const sec = el.closest('section[id]'); return (sec ? '#' + sec.id + ' ' : '') + c.split(' ').slice(0, 3).join('.'); };
  const out = [];

  // ---- 1. labels inside graphics
  let nLab = 0, nG = 0;
  document.querySelectorAll('svg').forEach(s => {
    if (!vis(s) || s.classList.contains('d-icon') || s.closest('.d-icon')) return;
    const items = [...s.querySelectorAll('text')].filter(t => t.textContent.trim() && vis(t)).map(svgInk);
    if (!items.length) return; nG++; nLab += items.length;
    const box = s.getBoundingClientRect(), g = name(s);
    for (let i = 0; i < items.length; i++) { const a = items[i];
      if (a.l < box.left - tol || a.r > box.right + tol)
        out.push(`OUTSIDE  ${g}: "${a.txt}" spans ${a.l.toFixed(1)}–${a.r.toFixed(1)}, graphic ${box.left.toFixed(1)}–${box.right.toFixed(1)}`);
      for (let j = i + 1; j < items.length; j++) { const b = items[j];
        const ox = Math.min(a.r, b.r) - Math.max(a.l, b.l), oy = Math.min(a.b, b.b) - Math.max(a.t, b.t);
        if (ox > tol && oy > tol) out.push(`OVERLAP  ${g}: "${a.txt}" × "${b.txt}" (${ox.toFixed(1)} × ${oy.toFixed(1)} px)`); } }
  });

  // ---- 2. clear space around big figures
  // [selector, tier, above/below, sides, own label, own-label selector, scope]; T1-T4 apply from 28px
  const TIERS = [
    ['.rows__fig .fr', 'T1', mobile ? 24 : 48, 32, mobile ? 12 : 16, '.lab', '.rows__fig'],
    ['.sech__num', 'T2', mobile ? 24 : 40, 24, mobile ? 16 : 24, 'svg.tally', '.sech__n'],
    ['.findings .fr', 'T3', 24, 16, 16, 'p', 'li'],
    ['.count .fr', 'T3', 24, 16, 16, '.k', 'li'],
    ['.spec__v', 'T4', 16, 24, 12, '.spec__k', 'li'],
    ['svg.hr text.fr', 'T5', 12, 12, 8, null, null],
    ['.stages .cnt .fr', 'T5', 12, 12, 8, null, null],
  ];
  const obstaclesIn = root => { const o = [];
    const tw = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    for (let n; (n = tw.nextNode());) { const p = n.parentElement;
      if (!n.textContent.trim() || !p || p.closest('svg, script, style, .vh, [hidden]') || !vis(p)) continue;
      htmlInk(n).forEach(b => o.push(b)); }
    root.querySelectorAll('svg').forEach(s => { if (!vis(s) || s.classList.contains('d-icon')) return;
      s.querySelectorAll('text').forEach(t => { if (vis(t) && t.textContent.trim()) o.push(svgInk(t)); });
      s.querySelectorAll('line, path, circle, polyline').forEach(e => { if (!vis(e)) return;
        if (e.closest('.c-flag') && e.classList.contains('c-focusring')) return;
        const r = e.getBoundingClientRect(); o.push({ l: r.left, r: r.right, t: r.top, b: r.bottom, txt: '<' + e.tagName + '.' + (e.getAttribute('class') || '') + '>', el: e }); }); });
    root.querySelectorAll('*').forEach(e => { if (e.closest('svg') || !vis(e)) return; const cs = getComputedStyle(e), r = e.getBoundingClientRect();
      const bw = side => parseFloat(cs['border' + side + 'Width']) || 0;
      const col = side => cs['border' + side + 'Color'], seen = side => bw(side) > 0 && cs['border' + side + 'Style'] !== 'none' && !/rgba\(.*, 0\)$/.test(col(side));
      if (seen('Top')) o.push({ l: r.left, r: r.right, t: r.top, b: r.top + bw('Top'), txt: 'border-top of ' + e.className, el: e });
      if (seen('Bottom')) o.push({ l: r.left, r: r.right, t: r.bottom - bw('Bottom'), b: r.bottom, txt: 'border-bottom of ' + e.className, el: e });
      if (seen('Left')) o.push({ l: r.left, r: r.left + bw('Left'), t: r.top, b: r.bottom, txt: 'border-left of ' + e.className, el: e });
      if (seen('Right')) o.push({ l: r.right - bw('Right'), r: r.right, t: r.top, b: r.bottom, txt: 'border-right of ' + e.className, el: e });
      for (const ps of ['::before', '::after']) { const p = getComputedStyle(e, ps);
        if (p.content === 'none' || p.position !== 'absolute' || p.display === 'none') continue;
        if (!mobile && e.classList.contains('sech')) continue;     // the spine's section tick: margin device, exempt
        if (p.backgroundImage === 'none' && /rgba\(.*, 0\)$|transparent/.test(p.backgroundColor)) continue;
        const L = r.left + (parseFloat(p.left) || 0), T = r.top + (parseFloat(p.top) || 0);
        o.push({ l: L, r: L + parseFloat(p.width), t: T, b: T + parseFloat(p.height), txt: e.className + ps, el: e }); } });
    return o; };
  let nFig = 0; const cache = new Map();
  for (const [sel, tier, V, H, OWN, ownSel, boxSel] of TIERS) {
    document.querySelectorAll(sel).forEach(f => {
      if (!vis(f) || (tier !== 'T5' && parseFloat(getComputedStyle(f).fontSize) < 28)) return; nFig++;
      const sec = f.closest('section[id]'); if (!cache.has(sec)) cache.set(sec, obstaclesIn(sec));
      const mine = [];
      if (f instanceof SVGElement) mine.push(svgInk(f));
      else { const tw = document.createTreeWalker(f, NodeFilter.SHOW_TEXT);
        for (let n; (n = tw.nextNode());) if (n.textContent.trim()) mine.push(...htmlInk(n)); }
      const F = { l: Math.min(...mine.map(b => b.l)), r: Math.max(...mine.map(b => b.r)), t: Math.min(...mine.map(b => b.t)), b: Math.max(...mine.map(b => b.b)) };
      // SVG ruler values: their own labels are the mono texts beside them (the name after, the 1-4 index before)
      const own = f instanceof SVGElement ? null : (f.closest(boxSel) ? f.closest(boxSel).querySelector(ownSel) : null);
      const svgOwn = f instanceof SVGElement ? [f.previousElementSibling, f.nextElementSibling].filter(e => e && e.tagName === 'text' && e.classList.contains('mo')) : [];
      const label = `${tier} "${f.textContent.trim()}"`;
      for (const o of cache.get(sec)) {
        if (o.el === f || f.contains(o.el) || o.el.contains(f)) continue;
        const isOwn = (own && (o.el === own || own.contains(o.el))) || svgOwn.includes(o.el);
        const ox = Math.min(F.r, o.r) - Math.max(F.l, o.l), oy = Math.min(F.b, o.b) - Math.max(F.t, o.t);
        if (ox > tol && oy > tol) { out.push(`CLEAR    #${sec.id} ${label} touches ${o.txt.slice(0, 40)}`); continue; }
        if (ox > tol) { const gap = o.b <= F.t + tol ? F.t - o.b : o.t - F.b, need = isOwn ? OWN : V;
          if (gap < need - tol) out.push(`CLEAR    #${sec.id} ${label}: ${gap.toFixed(1)}px ${o.b <= F.t + tol ? 'above' : 'below'} to "${o.txt.slice(0, 40)}" (needs ${need})`); }
        else if (oy > tol && !isOwn) { const gap = o.l >= F.r - tol ? o.l - F.r : F.l - o.r;
          if (gap < H - tol) out.push(`CLEAR    #${sec.id} ${label}: ${gap.toFixed(1)}px to the side of "${o.txt.slice(0, 40)}" (needs ${H})`); }
      }
    });
  }
  return { graphics: nG, labels: nLab, figures: nFig, out };
}
"""


async def main():
    bad = 0
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for w in WIDTHS:
            for theme in ('light', 'dark'):
                pg = await b.new_page(viewport={'width': w, 'height': 900})
                await pg.goto('file:///home/claude/website/_preview.html')
                await pg.evaluate(f"document.documentElement.setAttribute('data-theme','{theme}')")
                await pg.evaluate("document.querySelectorAll('details').forEach(d => d.open = true)")
                await pg.wait_for_timeout(400)
                r = await pg.evaluate(PROBE, TOL)
                if theme == 'light' or r['out']:
                    print(f'{w:>5}px {theme:<5}  {r["graphics"]} graphics, {r["labels"]} labels, {r["figures"]} figures: '
                          f'{"clean" if not r["out"] else str(len(r["out"])) + " problem(s)"}')
                for line in r['out']:
                    print('         ' + line)
                bad += len(r['out'])
                await pg.close()
        await b.close()
    print('overlap_check:', 'PASS' if not bad else f'FAIL ({bad})')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    asyncio.run(main())
