# Critique, phase 2 round 1

**GRADE: 8/10.** Sent back.

This is a strong, disciplined page. The copy is down to 1,062 words, every section is within budget and there are no banned words. The bitmaps are gone. The graphics come from one system: rulers, wedges, tallies and the spine. Every figure checks against `uci_audit.json`. What stops it being a 9 is a scope error in the proof chart's provenance, in the one place .describe( is judged, plus one visible craft inconsistency in Services.

## Checks run

- `shoot.py critic-p2r1` produced no errors. Light and dark were checked at 1280 and 390.
- `a11y_check.py`: `under nav: []`, `small: []`, table headers are 10.5px mono, and the tooltip stays with a focused bar after scroll (`True`) at both widths.
- `wordcount.py`: 1,062 in total. By section: hero 45, who 99, services 204, method 93, proof 199, where 30, about 140, FAQ 130, contact 77.
- Overflow: page `scrollWidth` equals the viewport at 320, 360 and 390, in light and dark, and with the menu open.
- Tab order is logical: skip link, brand, nav, hero CTA, source link, 12 bars, flag, table toggle, 4 FAQs, copy, mail, form, footer. There are no traps and nothing lands under the nav.
- Tooltip: hover and focus both work, and it follows a focused bar on scroll. The flag announces its rule.
- Table twin: every value is there, the total is £9,331,596, and the flag note sits in the June row.
- Form, empty submit: both errors show, `aria-invalid` is set, and focus moves to the email field. With a bad email and a good message, only the email error shows. With valid input, the banner reads "This preview doesn't send yet. Nothing was sent…", takes focus, and the URL does not change. The page never claims the message was sent.
- Reduced motion: `scroll-behavior:auto`, the caret doesn't blink, and tooltip and chevron transitions are off. Only 0.12s colour fades remain, which is fine.
- Contrast: every text node on the page passes. The lowest is 4.56:1, the dark-mode chart unit labels. Nothing is coral text.
- Numbers: every figure on the page, in the SVGs and in the ARIA labels matches the JSON: the monthly values, shares, 37.5%, 234, 1 in 18, £77,184, 13%, 14.7%, 131,418, the ledger, and £38,970. I checked "16 minutes" against the raw file (541431 at 10:01, C541433 at 10:17).

## By criterion

- **(a) Brand fit and the 7-point test: 9.** It isn't a generic startup page. Everything in it measures or counts. The mark stays at logo size. Coral appears only for the June flag. It survives one colour, because the Sep–Nov bracket carries the story. The Arabic appears once, large, and `rtl`.
- **(b) Graphics: 8.5.** The hero ruler with its vernier (to scale at ×16 and ×25), the calendar-to-revenue rule, the wedges (with 0 as an empty slot) and the spine all read as one system. Weak points: the hero doesn't say whose file it is until a caption below the fold, and the section tallies mostly decorate.
- **(c) Copy: 8.5.** It is short and plain. A few restated premises remain.
- **(d) Layout and craft: 8.** Light and dark both hold. The Services spec row mixes three patterns. The desktop proof grid leaves a hole, and the chart text shrinks at 320px.
- **(e) Chart and data honesty: 7.5.** The chart's stated n and one finding use the whole file, not the chart's window.
- **(f) Accessibility: 8.5.** The a11y checks pass. The tooltip can't be dismissed with Escape, one error message is wrong, and there's a small table scroller at 320px.

## MUST FIX

1. **Proof chart provenance states the wrong n.** The provenance line says "n = 522,568 sale lines, net of cancellations". That is the whole file, including 1–9 Dec 2011. The chart plots Dec 2010 to Nov 2011, which is **497,814 sale lines with 8,321 cancellation lines netted** (recomputed with `uci_retail.py`'s own rules). This breaks CHARTS rule 3.
   - Fix: add `window_sale_lines` and `window_cancellation_lines` to `uci_audit.json` via `uci_retail.py`.
   - Then state n for the window, and add "December 2011 (partial) left out". That also gives the twin note's phrase "outside the window" something to refer to.
2. **"Also in the year" mixes scopes.** 234 and 1 in 18 are for the window. 14.7% and 131,418 lines are for the whole file; the window values are **14.6%** and **123,628**. Recompute for the window and add the values to the audit, or retitle the list and state each figure's scope.
3. **The Services spec row uses three different patterns.**
   - S01 reads "$30 / from", which is backwards for both sight and screen reader. Put "from" first.
   - S03 fakes a value with an inline-styled 15px ink "Priced per project" label that doesn't align with "weeks".
   - S02 uses a dashed box.
   - Fix: use one value-over-label pattern with shared baselines. Set S03's pricing like S02's placeholder style or as a label, with no inline style.

## SHOULD FIX

- Let Escape dismiss the chart tooltip (WCAG 1.4.13).
- When the email is malformed, the error still says "Add an email…". Change it to "Check the address".
- At 320px:
  - The mobile chart scales to 250px, so its labels render at 7.3–8px.
  - The table twin's Share column is clipped inside a scroller that isn't labelled or focusable.
  - Fix: draw a narrower variant, or tighten table padding by about 43px, or add `tabindex=0 role=region aria-label` to the scroller.
- Hero: name the file before the number, not only in the caption. On mobile, the −5,268 leader is about 2px long, so lengthen it.
- Desktop proof: the findings column ends about 380px above the chart panel. Balance the two, for example by moving the quote up.
- Lone figures use `tabular-nums` through `.fr`, but CHARTS §6 asks for proportional figures on a lone number.
- Copy: "Pick the one that matches your problem" restates "Three ways in". "actually" in the proof heading is filler.

## WHAT WOULD MAKE IT A 10

- Every number on the page ties back to one reconciled ledger, from the hero rows through the chart's n to the findings, with its scope stated.
- The hero states its argument: a leader from 522,568 to the active index ("count before analysing").
- The findings become data images too: 234 of 4,284 and 14.6% drawn as short rulers in the same system.
- Leaders replace the remaining explanatory sentences in Services.
- 320px gets the same care as 390px.
