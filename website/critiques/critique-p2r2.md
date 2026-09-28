# Critique, phase 2 round 2

**GRADE: 8/10.** Sent back, but it's close. All three round-1 blockers are fixed, and the fixes are sound. What remains is one mislabelled base on a new finding ruler, and one mobile regression in the hero. Both are cheap to fix.

## Round-1 items, checked myself

| Round-1 item | Status | Evidence |
|---|---|---|
| M1: chart n | **Fixed** | `uci_retail.py` now computes the window counts and asserts 497,814 + 24,754 = 522,568. My independent recomputation gives the same 497,814 and 8,321. The provenance line reads "n = 497,814 sale lines, Dec 2010 – Nov 2011, 8,321 cancellations netted. December 2011 (partial) left out". |
| M2: findings period | **Fixed** | Retitled "Same twelve months". 14.6% and 123,628 are now window values (they match my recomputation). |
| M3: Services spec row | **Fixed** | One value-over-label pattern: "From $30 / price", "To be set / price and timeline", "Per project / price". No inline style. |
| Esc closes tooltip | **Fixed** | Escape hides it. It stays hidden on scroll and comes back on the next focus. |
| Malformed email message | **Fixed** | "Check the address, for example name@company.com." |
| 320px chart | **Fixed** | A narrower chart is drawn below 375px. Its smallest text is 9.5px. |
| 320px table | **Fixed, 1px short** | The scroller is now focusable (`tabindex=0`, region, label). The table is 257px wide in a 256px box, so there is still 1px of scroll. |
| Hero names the file first | **Fixed** | "The worked example, UCI Online Retail:" now sits above the number. A bracket ties 522,568 to the clean span. |
| Mobile −5,268 leader | **Regressed** | The mobile leaders were removed. See M2 below. |
| Proof layout hole | **Fixed** | The quote moved into the findings column, and the two columns now balance. |
| Proportional lone figures | **Fixed** | |
| Copy trims | **Fixed** | 1,055 words in total. Services is down to 197. |

## Re-run checks

- `a11y_check`: under nav `[]`, small `[]`, table headers 10.5px, tooltip after scroll `True`.
- No horizontal scroll at 320, 360 or 390px, in light and dark, and with the menu open.
- Tab order is unchanged and logical.
- Form: the page never claims a message was sent.
- Reduced motion: only colour fades remain.
- Contrast: every text node passes at 1280, 390 and 320px, in both themes.
- Every figure on the page matches `uci_audit.json`.
- Known gap: at 320px the month hit targets are 19.3px wide. I accept this under the WCAG 2.5.8 exception, because an equivalent control is on the page: the focusable table.

## By criterion

- **(a) Brand fit: 9.**
- **(b) Graphics: 8.5.** The finding rulers are a real gain: 234 of 4,284 projected onto half the revenue is the s3 idea done small. The mobile hero lost its leaders, though.
- **(c) Copy: 9.**
- **(d) Layout and craft: 9.** The proof block balances, the spec row is consistent, and 320px is handled.
- **(e) Chart and data honesty: 8.** One finding ruler names the wrong base.
- **(f) Accessibility: 9.**

## MUST FIX

1. **The 14.6% ruler says "NET REVENUE", but it isn't.** `window_missing_customer_value_share` divides by the value of the window's sale lines before cancellations (£9,633,406), not by the £9,331,596 net that the chart and table show. As a share of net revenue it would be 15.1%.
   - Option 1: relabel the ruler's right end "SALE VALUE" and the sentence "of sale value (before cancellations)".
   - Option 2: compute a net-based share in `uci_retail.py` and keep the label.
2. **The mobile hero vernier's segments are no longer identified.** At 390px the four figures sit in a 2×2 grid, with no leaders or other link to the segments they measure, so the magnified tail reads as four unlabelled blocks. Restore a link:
   - short leaders into the grid; or
   - a small index mark (1–4) on each segment, repeated beside its figure.

## SHOULD FIX

- At 320px the table overflows its box by 1px, which triggers a pointless scroll. Trim 1px of padding.
- The "234 OF 4,284 CUSTOMERS" label sits at the far right end, over the unfilled part of the ruler. Anchor it near the ink segment, or at the left end.
- The wedges were dropped from "4 days" and "2 revisions". INSPO listed them there. That's acceptable, but it's now a deliberate departure from INSPO; note it in the build.

## WHAT WOULD MAKE IT A 10

- Every denominator on the page is named and ties to the same ledger.
- The mobile hero reads as clearly as the desktop one.
- Label placement on the finding rulers is as precise as the chart's.
- Beyond that, the page is ready.
