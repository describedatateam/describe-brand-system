# Critique, phase 2 round 5 (after the founder's round-4 feedback)

**GRADE: 8/10.** Sent back with one blocker. This is the best round so far. The navy band with its sky window is a strong, on-brand hero. The rulers now read on their own, and the clear-space tiers hold everywhere I measured. The blocker is that the founder's "pixel perfect" requirement fails at 3 dppx, the density of most current phones. It's a cheap fix, and it also cuts page weight.

## Checks run

- `shoot.py critic-p2r5`: no errors.
- `a11y_check`: under nav `[]`, small `[]`, table headers 10.5px, tooltip after scroll `True`.
- `overlap_check`: passes at 320, 360, 390, 420, 768 and 1280px. I also ran it at 1000, 1100, 1199, 1440 and 1920px; it passes there too.
- `pixel_check`: passes, 2 colours at 1× and 2×, 1280 and 390px, light and dark.
- `wordcount`: 1,056.
- My own probes found no regressions:
  - no horizontal scroll at 320–390px, including with the menu open;
  - logical tab order;
  - Escape closes the tooltip;
  - the form never claims a message was sent;
  - no text under 4.5:1 or under 9px at 1280, 390 or 320px, in either theme, including the hero text on navy;
  - every figure on the page matches `uci_audit.json`;
  - ×28 = 541,909 ÷ 19,341 = 28.02, so the label is correct at every width.

## The founder's three points

1. **Room around numbers: resolved.** Tiers T1–T4 are enforced by the checker and pass at 11 widths. I also inspected T5 (ruler values and stage numbers) by eye; it has comfortable space, but the checker doesn't cover it (see SHOULD FIX).
2. **The rulers colliding: resolved.**
   - Each ruler now reads alone: full file, then 112px of empty space, then the ×28 vernier across the full width.
   - Only the two dashed projections cross the gap, and they stop short of the rules and labels.
   - 522,568 is right-aligned to the blue index tick and shares a baseline with 541,909. The pairing is obvious.
   - On mobile, the 1–4 index grid and 522,568 set 40px below it read cleanly.
3. **The sky pixel-perfect and safe: safe, but pixel-perfect only at 1× and 2×.**
   - Safe: no text, figure or ruler sits on the plate. The hero text is #F6F8FC on #092052, about 15:1.
   - Pixel-perfect: I measured the sky window myself.

| Width | dppx | Colours | Non-binary pixels |
|---|---|---|---|
| 1000, 1001, 1100, 1281, 1366, 1440, 1920, 2560 | 1 | 2 | 0% |
| 1440 | 2 | 2 | 0% |
| **390, 375** | **3** | **43** | **34%** |
| 412 | 2.625 | 200 | 31% |
| 1280 | 1.5 | 48 | 60% |

At 3 dppx the 2× mask is resampled by 1.5. The fine 45° screen goes soft and bands unevenly: exactly the grey edge pixels the founder ruled out. The direction document accepted fractional ratios like 1.25 and 1.5, but 3× is an integer ratio. It's also the density of nearly every current iPhone and many Android phones, which is how most people will first see this hero.

## Composition of the sky window

- **1280:** a 544px window against a 624px text column. Balanced. The spur of the Milky Way rises through the window and a dotted boundary curves across it. It reads as an instrument's aperture, not wallpaper.
- **1440:** the window is 624px, equal to the text column. The best proportion.
- **1920:** the text column sits at the content edge, with 336px of plain navy to its left; the window is 864px. It still works, and the empty navy reads as deliberate.
- **2560:** the window is 1184px and shows plate x 800–1984. The plate is 2400px wide, so above about 3,390px it runs out and a blank navy strip would appear at the right. That's an edge case; clamp the window's width.
- **1000:** a 264px sliver. It still reads as a window, but only just.
- **390:** the 240px strip at the top shows the densest part of the Milky Way. Below it, the text has 40px of padding, and the CTA ends at 634px, above the fold on a 390×844 screen. Good.
- **Test 6 (one colour):** passes. The plate is one ink on one ground.
- **Test 2 (real relationship):** passes. It's a star chart with constellation boundaries: orientation.
- The plate is loud, with 35% of the window lit, but it's the founder's own treatment, it sits beside the text rather than under it, and nothing else on the page competes with it.

## Nav, focus and dark mode with the navy band

- **Focus:** the CTA's four-corner sighting frame switches to off-white inside the band. It's clearly visible at 1280 and 390px, in both themes.
- **Nav:** it sits on the ground colour above the band, and the mobile menu opens over the band cleanly in both themes. **One flaw:** the sticky nav is 92% opaque with a blur. When you scroll over the band, the white headline ghosts through it, and in light mode the bright sky shows as grey blotches.
- **Dark mode:** the band stays at brand navy #092052 with local tokens. On the darker dark-mode ground it reads as a slightly raised navy panel. That's coherent. The text, CTA and sky are identical in both themes, as intended.

## Page weight

`site.html` is 1,102 KB, of which 923 KB is the two sky masks as base64: 221 KB for the 1× mask and 702 KB for the 2×. Because they're inline, every visitor downloads both, including 1× screens. The page only ever shows plate x 800 to about 1990 and y 250–850 on desktop, and x 820–1820 by y 300–540 on mobile. Cropping the masks to x 800–2400 by y 250–850 (a third of the area), with the offsets adjusted to match, should cut roughly 600 KB. That makes room for a 3× mobile crop.

## By criterion

- **(a) Brand fit and the 7-point test: 9.5.** The navy band makes the brand unmistakable. It passes the one-colour test, and the sky has a real relationship to orientation.
- **(b) Graphics: 9.** The rulers are resolved, and the page reads as one system from the sky to the chart.
- **(c) Copy: 9.**
- **(d) Layout and craft: 9.** The clear space holds everywhere; the sticky-nav ghosting is a nit.
- **(e) Chart and data honesty: 9.5.**
- **(f) Accessibility and robustness: 8.** Contrast, focus and forms are all good. The 3× rendering fails the stated pixel requirement.

## MUST FIX

1. **The sky isn't pixel-perfect at 3 dppx.** 34% of the window's pixels are grey at 390px and 375px, 3×. Add `@media (min-resolution: 3dppx)`, and ideally `(max-width: 999px)` as well, with either option below.
   - **Best:** a 3× mask of just the mobile crop: 1000×240 CSS px, so 3000×720 device px, 1-bit.
   - **Stopgap:** keep the 1× mask and add `image-rendering: pixelated`. I tested this: Chromium honours it on masks and gives exactly 2 colours at 3×. WebKit support for pixelated masks is unverified, which is why the 3× asset is the robust fix.

   Add dppx 3 to `pixel_check.py`. Optionally apply `pixelated` for 2.625 and 1.5 too, so those at least stay binary.

## SHOULD FIX

- **Crop both masks** to the region ever shown, as above. It saves about 600 KB and pays for the 3× crop.
- **Make the sticky nav opaque**, at least while it's over the band. Use `background: var(--ground)` with no transparency, which also removes the ghosting.
- **Clamp the window's width**, e.g. `max-inline-size: 1600px` measured from the window's left edge, so very wide screens never show the plate's edge.
- **Add T5** (ruler values and stage numbers, 12px clear) to `overlap_check.py`, so all five tiers are enforced rather than eyeballed.

## WHAT WOULD MAKE IT A 10

- The sky crisp at every integer density (1×, 2× and 3×), with the page back under about 500 KB.
- An opaque nav.
- All five clear-space tiers machine-checked.
- Beyond that, this is the page the founder asked for.
