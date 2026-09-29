# Illustration

The .describe( illustration layer: historical scientific drawings, reduced to
one bit and coloured by the page. It exists to warm up a precise, technical
system without decorating it. Every image has one job, and it appears only
where that job applies.

```
python3 illustrations/export_bitmaps.py    # al-Sufi figures, astrolabe plate, sky band
python3 illustrations/export_more.py       # comet, orbit, moon, eclipse, Scorpio
python3 illustrations/hero_field.py        # the homepage hero background
```

---

## §1 The vocabulary

An image is chosen for what it means, never for how it looks. This table is
the whole vocabulary; `jev/catalogue.json` holds the same meanings as text so
a classifier can apply them consistently.

| Image | Means | Use it for |
|---|---|---|
| **Libra**, the scales | Fairness; weighing evidence; testing whether something is real | "Testing whether it's real"; any fair comparison |
| **Cygnus**, stars first | Evidence versus the story told about it | The evidence section; About |
| **Cygnus**, the two outside stars | Outliers kept and labelled, not deleted | Data cleaning |
| **Cancer**, two views | The same data from two viewpoints | Method; bilingual pages |
| **Astrolabe plate** | An instrument read the same way every time | Dashboards |
| **Hero sky** | Atmosphere only | The homepage hero background. Nothing else |
| **None** | — | Forms, prices, legal, contact, report interiors |

**Report interiors stay clinical.** Illustration belongs on the web, social,
covers and dividers; interior pages carry charts.

---

## §2 The treatment

1. **One bit.** Every pixel is ink or paper. No greys, no photographic tone.
2. **Layers, not pictures.** Each illustration ships as separate masks:
   `lines`, `stars`, `outside`, and sometimes `dotted`. The page colours each
   one from a token, so one file set serves paper and navy.
3. **Colour by meaning.**
   - `lines` take ink.
   - al-Sufi's `stars` take active blue: they are the measurements.
   - `outside` stars take ink, except where the page is about outliers.
     There they carry the coral outlier marker (ring and dot), which is the
     only coral in the illustration layer.
   - The hero sky takes `--faint`.
4. **Stars are redrawn, not traced.** Each red star is found on the scan and
   redrawn as a clean disc at its measured centre and size. The size variation
   is al-Sufi's.
5. **Two kinds of source, two methods.**
   - Pen drawings and engravings: flatten the paper, then threshold.
   - Tonal plates: blur out the print screen, then ordered (Bayer) dither.
     Never error-diffusion noise; the screen should read as engraving.
6. **Never stack two drawings.** A figure is never laid over a sky or over
   another figure. Tested and rejected (see `studies/`): the figure floats
   and the two skies compete.
7. **The hero sky carries text.** It is set between 3% and 34% ink and never
   heavier, with the stars kept as clean paper points.

---

## §3 On the web

```html
<div class="art" style="--ar:1900/2187">
  <span style="--c:var(--ink);   --m:url(cygnus_lines.png)"></span>
  <span style="--c:var(--active);--m:url(cygnus_stars.png)"></span>
</div>
```

```css
.art{position:relative;aspect-ratio:var(--ar)}
.art span{position:absolute;inset:0;background:var(--c);
  -webkit-mask:var(--m) center/100% 100% no-repeat;
          mask:var(--m) center/100% 100% no-repeat}
```

Dither must not be scaled. The hero sky is masked at its natural size
(`mask-size:auto`), because resampling an ordered dither turns it into a
moiré grey.

---

## §4 Rights

**Public domain only.** Nothing marked non-commercial or "usage conditions
apply". Every file is listed in `PROVENANCE.md` and `bitmaps/manifest.json`
with its source.

Still to confirm before publishing:

- The astrolabe plate: British Library Or 14270, exact record.
- The comet, the orbit, the moon and the eclipse: British Library Flickr
  scans; source books to identify.
- Scorpio (`DP1.jpg`): source unknown. Do not publish.

Confirmed:

- The al-Sufi pages: The Met, object 446297, public domain.
- The Milky Way chart (hero sky, `bitmaps/hero-night/`): British Library
  Flickr scan 11241855653, https://www.flickr.com/photos/britishlibrary/11241855653.
  Source book identified by Wafa'a on 2026-09-28: *L'Espace céleste et la
  nature tropicale, description physique de l'univers*, by Emmanuel Liais
  (1826–1900), preface by Jacques Babinet (1794–1872), drawings by Yan'
  Dargent (1824–1899), Paris, 1865. Every contributor died more than 120 years
  ago, so the work is public domain in every jurisdiction; a faithful scan of
  a flat public-domain page adds no new copyright. Credit it on the site as:
  "Sky after Yan' Dargent, in E. Liais, *L'Espace céleste*, 1865. British
  Library."

---

## §5 Rejected, and why

| Tried | Why it went |
|---|---|
| Victorian book engravings (soldiers, cats, lizards) | No link to measurement; the soldiers carry British military connotations for a Gaza-based agency |
| Marbled endpapers | Decorative; turn to noise in one bit |
| A figure over a sky backdrop | Two drawings, two skies, one floats |
| The astrolabe cut into the dithered sky (mark or plate) | Didn't read; the hero keeps the sky alone |
| Religious text (`Or 14270_0161`) | Sacred text is not decoration |
