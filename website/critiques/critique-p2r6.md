# Critique, phase 2 round 6 (final)

**GRADE: 9/10.** The loop ends. The round-5 blocker is fixed and I verified it independently. There are no regressions anywhere on the page, in light or dark, on desktop or mobile. What's left is one wide-screen composition nit and some polish.

## Designer's claims, checked myself

| Claim | Verified | Evidence |
|---|---|---|
| 3× sky mask on <1000px at 3dppx | **Yes** | The binary sweep below shows 0.00% non-binary pixels at 320, 360, 375, 390, 414, 428, 430, 768 and 999px, all at 3×. The 8× zoom shows clean one-device-pixel screen lines. The @3x file is a true 7200×3600 render, not an upscale: it matches the nearest-upscaled 1× only 83% of the time. |
| Every density cropped, with asserts | **Yes** | `build.py` crops to plate (800,250)–(1820,850) for 1× and 2×, and (820,300)–(1820,540) for 3×. It asserts that each source is the full plate at its density, that the phone strip fits inside the crop, and that each tag is embedded once. No width shows an empty strip: all eighths of the window are lit at every tested width, from 320 to 3840. |
| Page weight 505 KB | **Yes** | `site.html` is 517,923 bytes (506 KB), down from 1,102 KB. |
| Window capped at 1020px | **Yes, but see SHOULD FIX 1** | Above 2076px the window floats: at 2560 there is a 164px navy gap on the right, and at 3840 an 804px gap. |
| Nav opaque | **Yes** | `.top{background:var(--ground)}`. Scrolled over the band, there's no ghosting in either theme. |
| overlap_check enforces all five tiers | **Yes** | T5 covers the hero vernier values and the stage numbers, with no own-label exemption, so the check is stricter than the spec. 29 figures pass at 11 widths from 320 to 2560. |
| 412 @2.625×: 99.75% binary | **Yes** | 0.25% non-binary at 412 @2.625 and 0.17% at 393 @2.75. It's nearest-neighbour, and no bitmap can be exact at a fractional ratio. Accepted. |
| 3× desktop uses 2× with pixelated | **Yes** | 0.00% non-binary at 1000, 1280 @3 and 1280/1536 @1.25 (0.13%). |

## Sky binary sweep (my probe; non-binary % of window pixels)

| Density | Widths tested | Non-binary |
|---|---|---|
| 1× | 320, 999, 1000, 1280, 1920, 2076, 2560, 3840 | 0.00% |
| 2× | 320, 768, 999, 1000, 1280, 1440, 1512, 1920, 2560 | 0.00% |
| 3× | 320, 360, 375, 390, 414, 428, 430, 768, 999, 1000, 1280 | 0.00% |
| 2.625× / 2.75× | 412 / 393 | 0.25% / 0.17% |
| 1.25× | 1280, 1536 | 0.13% |

## Regression sweep

- **Scripts:** `shoot.py` produced no errors. `a11y_check`: under nav `[]`, small `[]`, table headers 10.5px, tooltip after scroll `True`. `overlap_check` passes. `pixel_check` passes, now including 3× at 375 and 390, and 2560 @1×. `wordcount`: 1,056.
- **Layout and interaction:**
  - No horizontal scroll at 320, 360 or 390px, including with the menu open.
  - Tab order is unchanged.
  - The tooltip works on hover and focus, and Escape closes it.
  - The table twin is complete, and fits exactly at 320px.
- **Form and copy button:**
  - An empty submit shows both errors and focuses the email field.
  - A malformed email gets the "Check the address" message.
  - A valid submit shows the "This preview doesn't send yet… Nothing was sent" banner, and the URL doesn't change.
  - The copy button works.
- **Contrast:** no text below 4.5:1 or 9px at 1280, 390 or 320px, in either theme.
- **Numbers:** every figure on the page matches `uci_audit.json`.
- **Visual pass:**
  - Full-page light and dark at 1280 and 390: the hero band, rulers band, services, method, proof (reconciliation ruler, chart and finding rulers), where-we-are, about, FAQ, contact, motto and footer are all intact.
  - The CTA focus frame is off-white on navy in both themes.

## By criterion

- **(a) Brand fit and the 7-point test: 9.5.**
- **(b) Graphics: 9.**
- **(c) Copy: 9.**
- **(d) Layout and craft: 9.** Only the wide-screen float remains.
- **(e) Chart and data honesty: 9.5.**
- **(f) Accessibility and robustness: 9.5.** The sky is exact at every integer density.

## MUST FIX

None.

## SHOULD FIX (exact, for the coordinator)

1. **Wide-screen window float (above 2076px).** `max-inline-size:1020px` with both `left` and `right` set makes the browser drop `right`, so the window stops short of the viewport edge and its right edge aligns to nothing. Anchor it right instead. In `template.html`, in the `@media (min-width:1000px)` rule for `.hero__sky`, replace the whole rule with:

   ```css
   .hero__sky{position:absolute;inset-block:0;right:0;
     left:max(round(down, max(736px, 50% + 96px), 1px), calc(100% - 1020px))}
   ```

   Remove `max-inline-size:1020px`. Every value stays whole-pixel for an integer viewport, and the mask offset (−800px −250px from the window's left edge) still shows plate x 800–1820.

   Then add 3840 @1× to `pixel_check.py`, and assert `bandR − (x + w) == 0` there, so a gap can't come back.
2. **Leave a note on density coverage.** In `pixel_check.py`, the 412 @2.625 and 1280 @3 lines print "(info)". Leave that behaviour, but add a one-line comment that fractional densities are best-effort by design, so a future reader doesn't treat them as failures.

## WHAT WOULD MAKE IT A 10

- The wide-screen anchor fix above.
- Then a real-device look at the sky on one iPhone (3×) and one mid-range Android (2.625×) in daylight. Chromium emulation proves the pixels are binary, but not how the 45° screen reads on OLED at arm's length.
