# Critique, phase 2 round 3

**GRADE: 8/10.** Sent back. One blocker remains, and it is new this round: the new reconciliation ruler's labels collide at every phone width. Everything else is at 9 or better. Fixing that one collision without regressions should reach 9.

## The 15.0% vs 15.1% question: the designer is right

I recomputed from `online_retail.pkl` with `uci_retail.py`'s rules, Dec 2010 – Nov 2011.

| Quantity | Value |
|---|---|
| Net revenue (sales + cancellations) | £9,331,596.08 |
| No-ID value, sale lines only | £1,408,406.32 (123,628 lines) |
| No-ID value, cancellation lines | −£4,135.15 (161 lines) |
| No-ID value, net | £1,404,271.17 |
| **Net / net** | **0.15049 → 15.0%** |
| Sales-only no-ID / net (my round-2 figure) | 0.15093 → 15.1% |
| Sales-only / sales-only (round 2 page) | 0.14620 → 14.6% |

My 15.1% divided a sales-only numerator by a net denominator, so it mixed two bases. **15.0% is correct**: the numerator and the denominator are both net, on the same base as the chart. `uci_audit.json` now carries `window_missing_customer_net_share: 0.15049`, computed in `uci_retail.py`, and the page prints 15.0%.

## Round-2 items, checked myself

| Item | Status | Evidence |
|---|---|---|
| M1: "NET REVENUE" label | **Fixed** | 15.0% is now a share of net revenue. The sentence says "of net revenue". |
| M2: mobile tail identity | **Fixed** | The segments are indexed 1–4, and each index repeats beside its figure. Checked in light and dark at 390px. It reads clearly. |
| 320px table overflow | **Fixed** | Table 256px, box 256px. |
| 234 label placement | **Fixed** | "Half the revenue" now sits at the ink segment, with "4,284 customers" at the end. |
| INSPO departure (no wedges on service facts) | Accepted | Not raised again. |

## Re-run checks

- `a11y_check`: under nav `[]`, small `[]`, table headers 10.5px, tooltip after scroll `True`.
- No horizontal scroll at 320, 360 or 390px, in light and dark, and with the menu open.
- Escape dismisses the tooltip. The form never claims a message was sent. The malformed-email message is correct.
- No text fails contrast, and none is under 9px, at 1280, 390 or 320px in either theme.
- Every figure on the page matches `uci_audit.json`, including 24,754, 497,814, 8,321 and 15.0%.
- 1,055 words in total.

## By criterion

- **(a) Brand fit: 9.**
- **(b) Graphics: 9.** The reconciliation ruler (522,568 → −24,754 → 497,814) closes the ledger from the hero to the chart's n. That's exactly the "one ledger" idea.
- **(c) Copy: 9.**
- **(d) Layout and craft: 8.** There's a label collision on phones (M1).
- **(e) Chart and data honesty: 9.5.** Every base is named, and the numbers reconcile end to end.
- **(f) Accessibility: 9.**

## MUST FIX

1. **The reconciliation ruler's labels overlap at every phone width I tested (320, 360, 390 and 420px).**
   - "497,814 IN THE WINDOW" runs into "−24,754 DEC 2011, PARTIAL". At 390px it renders as "497,814 IN THE WIN−24,754…".
   - I found it with a bounding-box probe and confirmed it in a crop. It's the first graphic of the proof on the primary mobile width.
   - Fix, below about 640px, either way:
     - stack the two labels on separate lines, the right-hand one below the other; or
     - shorten them to "497,814 IN WINDOW" and "−24,754 DEC 2011".
   - Add a collision assert to the build, since the same probe caught this at once.

## SHOULD FIX

- **Ruler before title.** On desktop the reconciliation ruler sits above the chart title inside the panel, so a mono provenance strip leads the figure. CHARTS says the title is the finding. Move the ruler between the title and the plot, or down beside the provenance line.
- **"(123,628 lines)" beside a net share.** The net share also nets 161 no-ID cancellation lines. Say "123,628 sale lines" so the count and the share read on the same base.
- **Hero label at 320px.** "CANCELLATIONS NETTED" ends 2px past the hero SVG's right edge. It stays inside the gutter and isn't clipped, but it's tight.

## WHAT WOULD MAKE IT A 10

- Label collisions checked automatically at every width.
- The chart panel ordered as title → reconciliation → plot → provenance.
- Otherwise, this is the page: one ledger from the file's 541,909 rows to every figure, every base named, and graphics that measure something real.
