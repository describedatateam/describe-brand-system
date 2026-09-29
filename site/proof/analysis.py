"""Online Retail worked example — every figure the site quotes, from the raw file.

    python3 analysis.py "path/to/Online Retail Dataset.csv"

Writes figures.json next to this script. The dataset itself is not committed
(see NOTICE.md); it is the Kaggle copy of the UCI Online Retail data, 542,014
rows, InvoiceDate as DD/MM/YYYY H:MM, prices in pounds sterling.

The cleaning reproduces the May 2026 report exactly, with its one undocumented
step made explicit:

    542,014  raw rows
    - 5,270  exact duplicate rows
    - 1,454  rows with no Description
    - 1,058  rows with UnitPrice <= 0         (not stated in the report)
    = 534,232  = 524,980 sales + 9,252 returns

Returns are kept and netted, not dropped. That matters: the three largest
"sales" in the file were each reversed within the hour, and only netting
makes them disappear the way they did in the business.
"""
import json
import sys
from pathlib import Path

import pandas as pd

SRC = Path(sys.argv[1] if len(sys.argv) > 1 else "Online Retail Dataset.csv")
OUT = Path(__file__).with_name("figures.json")

raw = pd.read_csv(SRC, dtype={"InvoiceNo": str, "StockCode": str, "CustomerID": "string"})
steps = {"raw": len(raw)}

d = raw.drop_duplicates()
steps["duplicates"] = steps["raw"] - len(d)
n = len(d)
d = d.dropna(subset=["Description"])
steps["no_description"] = n - len(d)
n = len(d)
d = d[d.UnitPrice > 0].copy()
steps["price_le_zero"] = n - len(d)
steps["clean"] = len(d)

d["dt"] = pd.to_datetime(d.InvoiceDate, format="%d/%m/%Y %H:%M")
d["rev"] = d.Quantity * d.UnitPrice
d["is_return"] = d.InvoiceNo.str.startswith("C") | (d.Quantity < 0)
sales, returns = d[~d.is_return], d[d.is_return]
steps["sales_rows"], steps["return_rows"] = len(sales), len(returns)
assert steps["sales_rows"] + steps["return_rows"] == steps["clean"]

orders = sales.InvoiceNo.nunique()
last_day = d.dt.max()

monthly = (d.set_index("dt").groupby([pd.Grouper(freq="MS"), "is_return"]).rev.sum()
           .unstack(fill_value=0).rename(columns={False: "sales", True: "returns"}))
monthly["net"] = monthly.sales + monthly.returns

# Largest single sale lines, and the credit that reversed each one. Matched on
# customer and value, not stock code: 556444 was a keying error (60 sets at
# the 60-piece price) credited back through the manual code "M".
top_lines = sales.nlargest(3, "rev")
reversed_lines = []
for _, r in top_lines.iterrows():
    credit = returns[(returns.CustomerID == r.CustomerID)
                     & ((returns.rev + r.rev).abs() < 0.01)
                     & (returns.dt >= r["dt"])].head(1)
    c = credit.iloc[0] if len(credit) else None
    reversed_lines.append({
        "invoice": r.InvoiceNo, "description": r.Description.strip(),
        "quantity": int(r.Quantity), "value": round(r.rev, 2),
        "date": r["dt"].strftime("%Y-%m-%d %H:%M"),
        "reversed_by": None if c is None else c.InvoiceNo,
        "minutes_later": None if c is None else int((c["dt"] - r["dt"]).total_seconds() // 60),
    })

in_sep_nov = lambda f: f[(f.dt >= "2011-09-01") & (f.dt < "2011-12-01")].rev.sum()
sep_nov = in_sep_nov(sales)
non_product = sales[~sales.StockCode.str.match(r"^\d{5}")].rev.sum()

by_cust = d.dropna(subset=["CustomerID"]).groupby("CustomerID").rev.sum().sort_values(ascending=False)
top1 = max(1, len(by_cust) // 100)

by_desc = lambda frame: (frame.groupby(frame.Description.str.strip()).Quantity.sum()
                         .nlargest(5).astype(int).to_dict())

figures = {
    "currency": "GBP",
    "period": [d.dt.min().strftime("%Y-%m-%d"), last_day.strftime("%Y-%m-%d")],
    "cleaning": steps,
    "gross_sales": round(sales.rev.sum(), 2),
    "returns_value": round(returns.rev.sum(), 2),
    "net_revenue": round(d.rev.sum(), 2),
    "orders": int(orders),
    "aov_gross": round(sales.rev.sum() / orders, 2),
    "countries": int(d.Country.nunique()),
    "sep_nov_share_of_gross": round(sep_nov / sales.rev.sum(), 4),
    "sep_nov_share_of_net": round(in_sep_nov(d) / d.rev.sum(), 4),
    "identified_customers": int(len(by_cust)),
    "top_1pct_customers": top1,
    "top_1pct_share_of_identified_net": round(by_cust.head(top1).sum() / by_cust.sum(), 4),
    "top_20pct_share_of_identified_net": round(by_cust.head(len(by_cust) // 5).sum() / by_cust.sum(), 4),
    "rows_missing_customer_id_kept": int(d.CustomerID.isna().sum()),
    "non_product_lines_in_sales": round(non_product, 2),
    "monthly": [{"month": m.strftime("%Y-%m"), "sales": round(r.sales, 2),
                 "returns": round(r.returns, 2), "net": round(r.net, 2)}
                for m, r in monthly.iterrows()],
    "partial_last_month_days": int(last_day.day),
    "largest_sale_lines": reversed_lines,
    "top_products_by_units_gross": by_desc(sales),
    "top_products_by_units_net": by_desc(d),
}
OUT.write_text(json.dumps(figures, indent=2, ensure_ascii=False) + "\n")
print(json.dumps({k: v for k, v in figures.items() if k != "monthly"}, indent=2, ensure_ascii=False))
