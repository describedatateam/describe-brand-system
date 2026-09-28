# Round 1 visual feedback (p2r1)

## Top 5 changes, ranked

1. **The section tick reads as a minus sign.** At rest, every desktop head reads "−01" to "−08", because `.sech::before` sits at mid-numeral height (top 34px) and ends about 10px from the digit. Move it to the numeral's cap top (about 12px) and cut it to 9px, so it stays at least 16px clear. Only `.is-here` gets the long blue tick and the dot.
2. **Too much blue.** Eight blue tally rows run down the page, on top of the nav, CTA and chart. At rest, draw the done ticks in `--body`. Only the current section's tally row turns `--active`, and only while `.is-here`. That keeps one blue stroke per composition.
3. **Hero order is off.** At 144px, `541,909` outweighs the H1, and the CTA floats alone at the far right.
   - Put the CTA under the subline, left-aligned.
   - Cap the figure at 112px on desktop.
   - Put "19,341 set aside" left-aligned on the vernier's left end and "Scale ×16" at its right end. Don't stack both against the projection line.
4. **Mobile vernier is cramped.** Four staggered leader levels with the scale label left bottom-left. Below 600px:
   - Drop the leaders.
   - Put the scale label directly above the vernier.
   - Under it, set the four figures and labels in a 2×2 grid, in left-to-right order.
5. **Take the wedges off services.** In "$30 ⁝4 ‖2" the wedge sits over "days", apart from its numeral. Only service 01 gets wedges, so the three columns don't match. Keep the plain figure and label row. Wedges stay only in Method and *Where we are*.

Also: in dark mode the chart's context bars are a neutral grey, so set them to `--body`. In About, the second H2-size line ("A number doesn't have to be wrong…") competes with the section title; drop it to about 40px.

## What's working (keep)
- The to-scale hero ruler and vernier.
- The method stages as wedges on a tick rule, on desktop and in the mobile vertical list.
- The dashed zero slot.
- The spine's active state.
- The mobile tick row on each section head.
- The equal-weight Arabic/English pair.
- Proof figures as big numerals.
- The page is at 1,062 words and doesn't look like a startup page. Dark mode holds.

## Departures
1. Coral only on the bar chart: **accept**. That's the one place it should be.
2. s3 merged under the month axis: **accept**. It reads as one figure.
3. Spine drawn with CSS gradients: **accept**, once the tick is fixed.
4. Rulers in percent x and pixel y: **accept**. Crisp at 390 and 1280.
5. No "section n of 8" label: **accept**. The tally carries it.
6. Wedges in services: **reject** (see change 5).
