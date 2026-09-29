"""
uci_retail.py — the homepage proof, recomputed from the canonical file.

Source: UCI Machine Learning Repository, "Online Retail" (id 352),
Chen, Sain & Guo (2012). https://archive.ics.uci.edu/dataset/352/online+retail
Download: https://archive.ics.uci.edu/static/public/352/online+retail.zip

    python3 uci_retail.py "Online Retail.xlsx"   → uci_audit.json

Cleaning is a waterfall, each step counted, so the totals reconcile:
    rows → − exact duplicates → − cancellation lines → − postage/fees/manual
    → − zero-price or negative-quantity lines → clean sale lines
Cancellations are then netted against the month they fall in, so an order
that was placed and cancelled contributes nothing.
"""
import json
import sys

import numpy as np
import pandas as pd

NONPROD = {'POST', 'D', 'M', 'BANK CHARGES', 'AMAZONFEE', 'DOT', 'CRUK', 'C2', 'PADS', 'B', 'S', 'm'}


def main(path):
    df = pd.read_excel(path, dtype={'InvoiceNo': str, 'StockCode': str})
    steps = {'rows': len(df)}
    d = df[~df.duplicated()]
    steps['duplicates'] = steps['rows'] - len(d)
    canc = d.InvoiceNo.str.startswith('C')
    steps['cancellation_lines'] = int(canc.sum())
    keep = d[~canc]
    np_ = keep.StockCode.isin(NONPROD)
    steps['nonproduct_lines'] = int(np_.sum())
    keep = keep[~np_]
    ok = (keep.UnitPrice > 0) & (keep.Quantity > 0)
    steps['zero_or_negative_lines'] = int((~ok).sum())
    sale = keep[ok].copy()
    steps['clean_sale_lines'] = len(sale)
    assert steps['rows'] - steps['duplicates'] - steps['cancellation_lines'] - steps['nonproduct_lines'] \
        - steps['zero_or_negative_lines'] == steps['clean_sale_lines'], 'waterfall does not reconcile'

    sale['val'] = sale.Quantity * sale.UnitPrice
    c = d[canc & ~d.StockCode.isin(NONPROD)].copy()
    c['val'] = c.Quantity * c.UnitPrice
    both = pd.concat([sale, c])
    win = both[(both.InvoiceDate >= '2010-12-01') & (both.InvoiceDate < '2011-12-01')]
    monthly = win.groupby(win.InvoiceDate.dt.to_period('M')).val.sum()

    cust = win[win.CustomerID.notna()].groupby('CustomerID').val.sum()
    cust = cust[cust > 0].sort_values(ascending=False)
    half = int(((cust.cumsum() / cust.sum()) < 0.5).sum()) + 1

    lv = np.log10(sale.val)
    med = lv.median()
    mad = 1.4826 * np.median(np.abs(lv - med))
    z = (lv - med) / mad
    flagged = sale[z > 7][['InvoiceNo', 'Description', 'Quantity', 'UnitPrice', 'val', 'InvoiceDate']]

    # the chart's window, counted with the same rules, so its n is stated for the period it plots
    in_win = lambda x: x[(x.InvoiceDate >= '2010-12-01') & (x.InvoiceDate < '2011-12-01')]  # noqa: E731
    wsale, wcanc = in_win(sale), in_win(c)
    wmiss = wsale.CustomerID.isna()
    window_counts = {
        'window_sale_lines': len(wsale),
        'window_cancellation_lines': len(wcanc),
        'window_missing_customer_lines': int(wmiss.sum()),
        'window_missing_customer_value_share': round(wsale.loc[wmiss, 'val'].sum() / wsale.val.sum(), 4),
        'window_left_out_sale_lines': len(sale) - len(wsale),
        # the same share on the chart's base: net revenue (sale lines plus their cancellations),
        # split by whether the line carries a customer ID
        'window_missing_customer_net_share': round(win.loc[win.CustomerID.isna(), 'val'].sum() / monthly.sum(), 5),
        'window_sale_value_gbp': round(wsale.val.sum(), 2),
    }
    assert window_counts['window_sale_lines'] + window_counts['window_left_out_sale_lines'] == steps['clean_sale_lines']

    out = {**steps,
           'window': '2010-12-01 .. 2011-11-30 (December 2011 is a partial month and is left out)',
           'monthly_net_gbp': {str(k): round(v, 2) for k, v in monthly.items()},
           'year_net_gbp': round(monthly.sum(), 2),
           'sep_nov_share': round(monthly['2011-09':'2011-11'].sum() / monthly.sum(), 4),
           'missing_customer_lines_clean': int(sale.CustomerID.isna().sum()),
           'missing_customer_value_share': round(sale.loc[sale.CustomerID.isna(), 'val'].sum() / sale.val.sum(), 4),
           'customers_known': int(len(cust)), 'customers_for_half': half,
           'outlier_rule': f'robust z > 7 on log10(line value); median line £{10 ** med:.2f}',
           'flagged_lines': [{k: (str(v) if k == 'InvoiceDate' else v) for k, v in r.items()}
                             for r in flagged.to_dict('records')],
           **window_counts}
    json.dump(out, open('uci_audit.json', 'w'), indent=2, default=float)
    print(json.dumps({k: v for k, v in out.items() if k != 'monthly_net_gbp'}, indent=2, default=float))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'Online Retail.xlsx')
