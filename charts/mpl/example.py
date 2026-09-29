"""example.py — Fig. 03 (S&P 500 outlier months) through the matplotlib bridge.
    python3 example.py  → example-returns.png"""
import os, sys
import numpy as np
import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from examples import STOCKS, month, signed          # same data, same audit
import mpl_describe as D

D.use()
r = STOCKS["^GSPC"].pct_change().dropna() * 100
mu, sd = r.mean(), r.std()
out = r[((r - mu) / sd).abs() > 3]
fig, ax = plt.subplots(figsize=(7.2, 4.2))
ax.hist(r, bins=np.arange(-18, 15, 1.0), color=D.C["context"], rwidth=0.88)
for v in (mu - 3 * sd, mu + 3 * sd):
    D.benchmark(ax, v, "−3σ" if v < 0 else "+3σ", axis="x")
for t, v in out.items():
    D.outlier(ax, v, 3.2, rule="|z| > 3")
D.outlier(ax, out.min(), 3.2, rule="|z| > 3", label="Three months\npast −3σ", dx=4, dy=95)
ax.set_xlabel("MONTHLY RETURN, %", loc="right")
ax.set_ylabel("MONTHS", loc="top", rotation=0, labelpad=-20)
D.finish(fig, ax, "Three months in 32 years fell more than three standard deviations",
         n=f"n = {len(r)} monthly returns",
         source="Yahoo Finance via matplotlib sample data (Stocks.csv)",
         dek=f"S&P 500 monthly returns, Feb 1990 – Jun 2022. Mean {signed(mu, 2)}, sd {sd:.2f}%.\n"
             + ", ".join(f"{month(t)} ({signed(v)})" for t, v in out.items()),
         path=os.path.join(HERE, "example-returns.png"))
print("example-returns.png")
