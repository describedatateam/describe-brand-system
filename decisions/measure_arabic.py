"""measure_arabic.py — the three Arabic tokens in type/typography.css,
measured instead of guessed.

--ar-scale       Amiri display size relative to Fraunces display
--ar-body-scale  Vazirmatn body size relative to Readex Pro body
--ar-w-body      Vazirmatn weight whose stem matches Readex Pro 300

Method: render at 1000 px with HarfBuzz shaping (raqm), measure ink.
Size: match the Arabic body height (the height of short, ascender-free
letter shapes) to the Latin x-height. Weight: match the vertical stem of
Latin 'l' to Arabic alef, after the size correction.
"""
from PIL import Image, ImageDraw, ImageFont
import numpy as np, json
F = 'fonts/'
S = 1000

def font(path, axes=None):
    f = ImageFont.truetype(F + path, S, layout_engine=ImageFont.Layout.RAQM)
    if axes is not None:
        f.set_variation_by_axes(axes)
    return f

def ink(f, text, rtl=False):
    im = Image.new('L', (S * 6, S * 3), 0)
    ImageDraw.Draw(im).text((S // 2, S), text, font=f, fill=255,
                            direction='rtl' if rtl else None)
    a = np.asarray(im) > 128
    ys, xs = np.where(a)
    return a, ys.min(), ys.max(), xs.min(), xs.max()

def h(f, t, rtl=False):
    _, y0, y1, _, _ = ink(f, t, rtl); return int(y1 - y0 + 1)

def stem(f, t, rtl=False):
    a, y0, y1, x0, x1 = ink(f, t, rtl)
    band = range(y0 + (y1 - y0) // 3, y1 - (y1 - y0) // 3)
    return float(np.median([a[y, x0:x1 + 1].sum() for y in band]))

# The core band: in running text, the rows where ink is dense (>= 35% of the
# densest row). For Latin that band is the x-height; for Arabic it is the
# main writing band. Matching the two bands matches perceived size — single
# letters don't work, because Arabic has no single "x" to stand for the rest.
LAT = 'the quick brown fox measures your data'
ARB = 'من البيانات إلى القرار نقيس ما يحدث فعلا'

def core(f, text, rtl=False):
    a, y0, y1, _, _ = ink(f, text, rtl)
    prof = a[y0:y1 + 1].sum(1).astype(float)
    pk = int(prof.argmax()); thr = 0.35 * prof.max()
    lo = pk
    while lo > 0 and prof[lo - 1] >= thr: lo -= 1
    hi = pk
    while hi < len(prof) - 1 and prof[hi + 1] >= thr: hi += 1
    return hi - lo + 1

def ar_body(f):
    return float(core(f, ARB, True)), {'text': ARB}

out = {}
# display: Fraunces 300, opsz 72, SOFT 0, WONK 0  vs  Amiri Regular
fr = font('Fraunces%5BSOFT,WONK,opsz,wght%5D.ttf', [72, 300, 0, 0])
am = font('Amiri-Regular.ttf')
xh_fr = core(fr, LAT)
ab_am, det_am = ar_body(am)
out['ar_scale'] = xh_fr / ab_am
out['display_detail'] = {'fraunces_x': xh_fr, 'amiri_body': ab_am, 'amiri_letters': det_am}

# body: Readex Pro 300 (HEXP 0)  vs  Vazirmatn
rx = font('ReadexPro%5BHEXP,wght%5D.ttf', [300, 0])
xh_rx = core(rx, LAT)
vz = font('Vazirmatn%5Bwght%5D.ttf', [300])
ab_vz, det_vz = ar_body(vz)
body_scale = xh_rx / ab_vz
out['ar_body_scale'] = body_scale
out['body_detail'] = {'readex_x': xh_rx, 'vazirmatn_body': ab_vz, 'vazirmatn_letters': det_vz}

# weight: Readex 300 'l' stem vs Vazirmatn alef, scaled by body_scale
st_l = stem(rx, 'l')
cands = {}
for w in (200, 250, 300, 350, 400):
    cands[w] = stem(font('Vazirmatn%5Bwght%5D.ttf', [w]), 'ا', True) * body_scale
best = min(cands, key=lambda w: abs(cands[w] - st_l))
out['ar_w_body'] = best
out['weight_detail'] = {'readex_l_stem': st_l, 'vazirmatn_alef_stem_scaled': cands}
print(json.dumps(out, indent=2, ensure_ascii=False, default=float))
json.dump(out, open('arabic_tokens.json', 'w'), indent=2, ensure_ascii=False, default=float)
