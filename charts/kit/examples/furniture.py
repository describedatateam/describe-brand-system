"""
furniture.py — the instrument furniture on a real chart.

    python3 charts/kit/examples/furniture.py   → examples/out/07-mpl-furniture-{light,dark}.png

measuring_edge(), index_mark() and callout() on the Online Retail monthly
net revenue (decisions/uci_audit.json, the canonical audit). Nothing invented.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(KIT))
sys.path.insert(0, KIT)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from describe_charts import mpl as D

AUDIT = json.load(open(os.path.join(ROOT, "decisions", "uci_audit.json"), encoding="utf-8"))
MONTHS = ["Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov"]


def furniture(mode):
    D.apply(mode)
    m = AUDIT["monthly_net_gbp"]
    v = [m[k] / 1e6 for k in m]
    x = list(range(12))
    low = min(range(9), key=lambda k: v[k])
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    D.context(ax, x[:9], v[:9])
    D.story(ax, x[8:], v[8:])
    ax.set_xticks(x, MONTHS)
    ax.set_ylim(0, 1.6)
    D.measuring_edge(ax, "x", minor=0)            # B02: the axis as a ruled edge
    D.index_mark(ax, 11, v[11], f"Nov £{v[11]:.2f}M", side="left")   # B04 + C02
    D.callout(ax, low, v[low], 1, dx=10, dy=-30)    # E05: the note sits beside the chart
    D.units(ax, y="£ million, net")
    D.finish(fig, ax, f"Sep to Nov brought in {AUDIT['sep_nov_share'] * 100:.0f}% of the year",
             n=f"n = {AUDIT['window_sale_lines']:,} sale lines, 12 months",
             source="Online Retail dataset (UCI), canonical audit in decisions/uci_audit.json",
             dek=f"Net revenue by month, Dec 2010 to Nov 2011. 01: {MONTHS[low]}, the low point.",
             computed="24 Oct 2026",
             path=os.path.join(HERE, "out", f"07-mpl-furniture-{mode}.png"))
    plt.close(fig)


if __name__ == "__main__":
    for mode in ("light", "dark"):
        furniture(mode)
        print(f"07-mpl-furniture-{mode}.png")
