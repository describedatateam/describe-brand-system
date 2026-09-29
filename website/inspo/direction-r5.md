# Direction for round 5 (founder feedback after round 4)

Test renders are in `inspo/r5/`: `final-d.png` (1280), `final-m.png` (390) and `final-m2x.png` (390 @2x). Checked by pixel count, the sky area has exactly **2 colours** at 1× and at 2×.

## 1. Choose B, the night plate, set in an aperture

**Why B:**
- It is her own treatment.
- Navy and off-white are both brand colours.
- The band is the same navy in both themes, so dark mode needs no second design.
- It is one ink on one ground, so it passes the one-colour test.
- A (faint on paper) is the treatment she said wasn't working. It reads as noise, not sky.

**Text never sits on the sky.** I rendered the headline over the plate at natural size (1× is large: the dots are 4–10px), and the 45° screen and dotted boundaries run through every glyph. So the sky goes in an **aperture**: a hard-edged window beside the text, not a full-bleed background. It is the instrument open where it is looking.

**Desktop (≥ 1000px):**
- A navy band (#092052 in both themes) 600px tall, under the nav, full-bleed.
- Text column: left at the content edge, max 624px wide, top padding 88px, on plain navy.
- Sky window: from `left: round(down, max(736px, 50% + 96px), 1px)` to the viewport's right edge, full band height.
- Mask: `mask: url(lit) -800px -250px / 2400px 1200px no-repeat`, measured from the window's own left edge. At 1280 this shows plate x 800–1344, y 250–850: the rising spur of the Milky Way, one dotted boundary and bright stars. Wider screens reveal more to the right.

**Mobile (< 1000px):**
- A sky strip 240px tall, full width, at the top of the band.
- Mask: `-820px -300px`, the same region as desktop, cropped on the right.
- Text sits below the strip on plain navy: 40px top padding, 48px bottom padding, 16px side gutters. Band height is auto (about 630px).

**Pixel perfect:**
- Every offset and size is an integer px.
- The window's left edge is rounded as above, so it never lands on a half pixel.
- `@media (min-resolution: 2dppx)` swaps in `hero-night_lit@2x.png` at the same CSS size.
- At 1.25 or 1.5 dppx no mask can stay crisp. Accept that; the guarantee is for 1× and 2×.

**Contrast:**
- Text is #F6F8FC on #092052, about 15:1, fixed in both themes. It never sits on the plate.
- The CTA stays #0F58E5 with white text.
- The page spine starts below the band.
- The mark and rulers never go on the sky.

## 2. Hero rulers: their own band directly below the sky

Content width, ground colour, 96px top and bottom padding (64px on mobile). Rows from top to bottom:

1. **Caption:** "The worked example, UCI Online Retail", then 32px space.
2. **Figures:**
   - `541,909` (112px, `--body`) sits left, with its label 16px above.
   - `522,568` (84px, `--ink`) sits on the same baseline, **right-aligned to the blue index tick**, with its label 16px above.
   - On mobile, `522,568` moves to the end, 40px below the value grid.
3. **Main ruler:** 48px below the figures' descenders. Tick labels 8px above the rule.
   - **Remove** the dimension bracket under it.
   - Nothing else touches the tail.
4. **Magnifier zone:** 112px tall (80px on mobile) and **empty**. The only things in it are two dashed hairlines (`--faint`, 3 4) from the tail's two ends to the vernier's two ends. They stop 8px short of each rule and never cross a label.
5. **Vernier:** spans the **full content width**. The scale is then 541,909 ÷ 19,341 = **×28 at every width**, so the scale label never changes.
   - Its label row sits 12px above the rule: "19,341 set aside" on the left, "Scale ×28" on the right.
   - The segment ticks drop 8px below the rule.
6. **Values:** 24px below the vernier, in one row on desktop.
   - Each value and its label is left-aligned at its own segment's start. No leaders, no stagger.
   - The segments are 322, 566, 142 and 153px wide at 1184px, and every pair fits with 16px to spare.
   - Mobile keeps the numbered 2×2 grid.

## 3. Space around numbers: at least half the cap height on all sides

"Clear" means the distance to any other text, rule, leader or wedge. A figure's own label may sit closer, at the gap given.

| Tier | Figures | Clear above and below | Clear to the sides | Own label |
|---|---|---|---|---|
| T1 | hero figures 84–112px (56px on mobile) | 48 (24) | 32 | 16 (12) |
| T2 | section numerals 96px (56px) | 40 (24) | 24 | tally row 24 (16) below baseline |
| T3 | findings and *Where we are*, 56–64px | 24 | 16 | 16 |
| T4 | service figures, 36–44px | 16 | 24 between figures | 12 |
| T5 | ruler values and stage numbers, 24–28px | 12 | 12 | 8 |

Everywhere:
- Mono labels are at least 8px from any rule.
- Leaders stop 4px short of text.
- No text sits in the path of a projection line.

### Figures that violate the rule now (round 4)

**Desktop:**
1. `541,909`: 30px down to the tick labels (needs 48).
2. `522,568`: sits inside the projection path, with the bracket 40px above it.
3. Vernier values: the leader ticks touch `−5,268` and `−2,327` (about 4px). The `−2,495` leader runs 6px from "POSTAGE AND FEES".
4. Section numerals 01–08: the tally row is 18px below the numeral (needs 24).
5. Services `$30 · 4 · 2` and `1–2`: the labels are 8px under the baseline (needs 12). "From" is 4px from `$30`.
6. *Where we are* `1 · 1 · 0`: the wedge is 8px from its numeral (needs 16). The label is 10px under (needs 16). The figures are 22px under the top rule (needs 24).
7. Chart: "37.5% of the money" is 6px under its bracket (needs 8).

**Mobile:**
8. `541,909`: its label is 8px above (needs 12), and the tick labels are 14px below (needs 24).
9. `522,568`: 20px under the value grid (needs 40).
10. Section heads: the tick row is 18px above the numeral (needs 24), and the tally crowds the numeral's baseline.
11. Reconciliation ruler: "−24,754 DEC 2011, PARTIAL" wraps onto the line of "497,814 IN THE WINDOW". Put the labels on two rows at 8px each, one above the rule and one below.
12. Services figures: same as item 5.

Check all of these at 390 and 1280, in both themes.
