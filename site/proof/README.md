# Worked example — Online Retail

`analysis.py` recomputes every figure the homepage quotes from the raw CSV and
writes `figures.json`. The CSV is not committed (see `NOTICE.md`): it is the
Kaggle copy of the UCI Online Retail data, 542,014 rows, Dec 2010 – 9 Dec 2011.

```
python3 analysis.py "Online Retail Dataset.csv"
```

## Checked against the May 2026 report (`ECommerce_Sales_Analysis_Describe.pdf`)

**Holds.** 542,014 rows · 5,270 duplicates · 1,454 missing descriptions ·
534,232 rows after cleaning = 524,980 sales + 9,252 returns · gross sales
10,662,950 · 19,960 orders · AOV 534.22 · 38 countries · customer 14646 at
about 280K.

**Needs correcting in the report.**

| Report says | Data says |
|---|---|
| Figures in € | The data is in **£**. Every money figure changes symbol, not value. |
| Cleaning = duplicates, descriptions | Also drops **1,058 rows priced ≤ 0**. Without that step the count is 535,290, not 534,232. |
| "3 transactions exceed €35K — segment for account management" | All three were **reversed within 16 minutes**: 581483 (C581484, 12 min), 541431 (C541433, 16 min), 556444 (credited through `M` on C556445, 3 min — a keying error, 60 sets at the 60-piece price). Their customers net to about zero. |
| "Paper Craft & Storage Jars dominate volume" | Those are the two cancelled orders. Net of returns, the top items are WW2 Gliders, Jumbo Bag Red Retrospot, Popcorn Holder, Assorted Colour Bird Ornament, 72 Retrospot Cake Cases. |
| "Monthly revenue grew from €100K to €1.35M — 13×", "growth across both years" | No month is near 100K. Net monthly revenue runs £0.49M–£1.46M; the data covers 13 months, and the last holds 9 days. With one year there is no way to separate growth from season. |
| 4,223 products | Not reproducible. The raw file has 4,093 stock codes and 4,220 descriptions; after cleaning, 3,962 stock codes. |
| "0 edge cases" | True after cleaning, but only because the undocumented price ≤ 0 filter removed the 474 negative-quantity rows with no `C` invoice. Separately, £395K of "sales" are postage, manual and fee lines (`DOT`, `POST`, `M`, `AMAZONFEE`) or a bad-debt adjustment (`A563185`) — not product revenue. |

## Not the homepage's source

The homepage proof uses `decisions/uci_retail.py`, which works from the
canonical UCI file (541,909 rows) and leaves out the partial December. This
folder audits the May 2026 deck against the Kaggle file it was built from;
use the table above to correct the deck.
