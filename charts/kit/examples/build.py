"""
build.py — render the kit's example charts and report from real sample data.

    python3 charts/kit/examples/build.py        → charts/kit/examples/out/

Data (nothing invented, CHARTS.md §1):
  * Stocks.csv — monthly closes, Yahoo Finance via matplotlib sample data,
    loaded and audited by charts/examples.py
  * Gapminder — life expectancy by country, 1952–2007, via plotly.express

Plotly PNG export needs Chrome. If kaleido cannot find one, set
BROWSER_PATH to a Chrome or Chromium binary.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.dirname(HERE)
sys.path[:0] = [KIT, os.path.dirname(KIT)]          # describe_charts, charts/examples.py
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px

import describe_charts
from describe_charts import mpl as D
from describe_charts import plotly_theme as P
from describe_charts.report import Report
from examples import NAMES, STOCKS, STOCKS_SRC, signed   # same data, same audit as the specimen

COMPUTED = "17 Oct 2026"          # pinned so a rebuild only diffs when the data or the kit changes
GAP_SRC = "Gapminder, via plotly.express.data.gapminder()"
MIDDLE_EAST = ["Bahrain", "Egypt", "Iran", "Iraq", "Israel", "Jordan", "Kuwait", "Lebanon", "Oman",
               "Saudi Arabia", "Syria", "Turkey", "West Bank and Gaza", "Yemen, Rep."]
WORDS = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen".split()
out = lambda name: os.path.join(OUT, name)


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
BASE = pd.Timestamp("2010-01-01")
d = STOCKS.loc[BASE:]
listed = [c for c in d.columns if not c.startswith("^") and not np.isnan(d.loc[BASE, c])]
not_listed = [c for c in d.columns if not c.startswith("^") and c not in listed]   # Dell, 2016
idx = d[listed + ["^GSPC"]] / d.loc[BASE, listed + ["^GSPC"]] * 100
growth = (idx.iloc[-1] - 100)
top = growth[listed].idxmax()
bench = growth["^GSPC"]
beat = [c for c in listed if growth[c] > bench]

g = px.data.gapminder()
me = g[g.country.isin(MIDDLE_EAST)]
life = me.pivot(index="year", columns="country", values="lifeExp")
gain = (life.loc[2007] - life.loc[1952]).sort_values()
world_gain = (g[g.year == 2007].set_index("country").lifeExp
              - g[g.year == 1952].set_index("country").lifeExp).median()
least, most = gain.index[0], gain.index[-1]


# ---------------------------------------------------------------------------
# matplotlib
# ---------------------------------------------------------------------------
def mpl_indexed(mode):
    D.apply(mode)
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    for c in listed + ["^GSPC"]:
        if c != top:
            D.context(ax, idx.index, idx[c])
    D.story(ax, idx.index, idx[top])
    ax.set_yscale("log")
    ax.set_yticks([50, 100, 200, 500, 1000, 2000, 3000], ["50", "100", "200", "500", "1,000", "2,000", "3,000"])
    ax.minorticks_off()
    ends = idx.iloc[-1].sort_values()
    for c in [top, "^GSPC", ends.index[0]]:
        D.label_end(ax, idx.index[-1], idx[c].iloc[-1], NAMES[c], story=(c == top))
    D.units(ax, y="Index, 2010 = 100")
    D.finish(fig, ax,
             f"{NAMES[top]} grew {idx[top].iloc[-1] / 100:.0f}-fold from 2010, the most of {WORDS[len(listed)]} stocks",
             dek=(f"Adjusted monthly close, indexed to January 2010, log scale. S&P 500 {signed(bench, 0)} over the same period.\n"
                  f"{', '.join(NAMES[c] for c in not_listed)} is not shown: listed in 2016, it has no January 2010 price."),
             n=f"n = {len(idx)} months × {len(listed) + 1} series",
             source=STOCKS_SRC, computed=COMPUTED)
    fig.savefig(out(f"01-mpl-indexed-{mode}.png"))
    return fig


def mpl_ranked():
    D.apply("light")
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    D.ranked_bars(ax, [NAMES[c] for c in listed], [growth[c] for c in listed],
                  highlight=[NAMES[c] for c in beat], fmt="{:+,.0f}%")
    D.benchmark(ax, bench, f"S&P 500 {signed(bench, 0)}", axis="x")
    D.units(ax, x="Change since 2010, %")
    D.finish(fig, ax,
             f"{WORDS[len(beat)].capitalize()} of {WORDS[len(listed)]} stocks beat the S&P 500 from 2010 to mid-2022",
             dek="Change in adjusted close, January 2010 to June 2022. Blue bars beat the benchmark (dashed).",
             n=f"n = {len(listed)} series ranked; Dell not applicable (listed 2016)",
             source=STOCKS_SRC, computed=COMPUTED)
    fig.savefig(out("02-mpl-ranked-light.png"))
    return fig


def dropin():
    """The one-line change: the same untouched analysis code, before and after."""
    legacy = "monthly = STOCKS.loc['2018':, ['AAPL', 'MSFT', 'IBM']].rename(columns=NAMES)\n" \
             "ax = monthly.plot(title='Monthly close, 2018–2022')\n" \
             "ax.set_ylabel('USD')\n"
    plt.rcdefaults()
    exec(legacy, {"STOCKS": STOCKS, "NAMES": NAMES})
    plt.gcf().savefig(out("00-dropin-before.png"), dpi=150, bbox_inches="tight")
    plt.close("all")
    describe_charts.use()                    # ← the only line added
    exec(legacy, {"STOCKS": STOCKS, "NAMES": NAMES})
    plt.gcf().savefig(out("00-dropin-after.png"), dpi=150)
    plt.close("all")


# ---------------------------------------------------------------------------
# Plotly
# ---------------------------------------------------------------------------
def plotly_life(mode):
    P.apply(mode)
    long = me.sort_values("year")
    fig = px.line(long, x="year", y="lifeExp", color="country", markers=False)
    P.emphasise(fig, least)
    fig.update_layout(showlegend=False, width=900, height=520)
    for c in (least, most):
        fig.add_annotation(x=2007, y=life.loc[2007, c], text=c, showarrow=False, xanchor="left", xshift=6,
                           font=dict(color=describe_charts.palette(mode)["ink" if c == least else "body"]))
    fig.update_xaxes(range=[1950, 2015], dtick=10)
    P.finish(fig, f"{least}'s life expectancy gained {gain[least]:.0f} years, the least of {WORDS[len(gain)]} Middle East countries",
             dek=f"Life expectancy at birth, 1952–2007, every five years. {least} stalls after 1987; {most} gained most ({gain[most]:.0f} years).",
             n=f"n = {len(gain)} countries × {life.shape[0]} survey years", source=GAP_SRC, computed=COMPUTED,
             units=("", "Years"))
    return fig


def plotly_gains():
    P.apply("light")
    s = gain.sort_values()
    fig = px.bar(x=s.values, y=s.index, orientation="h", text=[f"+{v:.0f}" for v in s.values])
    fig.update_traces(marker_color=[describe_charts.palette()["story" if c == most else "context"] for c in s.index],
                      textposition="outside", textfont=dict(family="IBM Plex Mono", size=12),
                      hovertemplate="%{y}: +%{x:.1f} years<extra></extra>")
    fig.update_layout(width=900, height=560, hovermode="closest", yaxis=dict(showgrid=False, title=None),
                      xaxis=dict(showgrid=True, title=None, range=[0, 44]))
    P.benchmark(fig, world_gain, f"World median +{world_gain:.0f}", axis="x")
    P.finish(fig, f"{most} added {gain[most]:.0f} years of life expectancy between 1952 and 2007, the most in the region",
             dek=f"Change in life expectancy at birth, 1952 to 2007. Dashed: the median of all {g.country.nunique()} countries.",
             n=f"n = {len(gain)} countries", source=GAP_SRC, computed=COMPUTED, units=("Years gained", None))
    return fig


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
def report(figs):
    r = Report("Sample report: two datasets, one visual language",
               dek="A worked example of the .describe( report template, built from public sample data "
                   "so every number can be reproduced offline.",
               client="the .describe( brand system", issued="17 October 2026")
    r.section("Summary")
    r.text(f"Between January 2010 and June 2022, **{WORDS[len(beat)]} of {WORDS[len(listed)]}** large technology "
           f"stocks outgrew the S&P 500, which rose {signed(bench, 0)}. {NAMES[top]} grew most.")
    r.stats([(f"{idx[top].iloc[-1] / 100:.0f}×", f"{NAMES[top]} since Jan 2010", "n = 150 months"),
             (signed(bench, 0), "S&P 500 since Jan 2010", "the benchmark"),
             (f"+{gain[most]:.0f} yrs", f"{most}, life expectancy 1952–2007", f"n = {len(gain)} countries")])
    r.section("Markets")
    r.figure(figs["indexed"])
    r.figure(figs["ranked"])
    tbl = pd.DataFrame({"Series": [NAMES[c] for c in listed + not_listed],
                        "Jan 2010": [d.loc[BASE, c] for c in listed + not_listed],
                        "Jun 2022": [d[c].iloc[-1] for c in listed + not_listed],
                        "Change, %": [growth[c] if c in listed else np.nan for c in listed + not_listed]})
    r.table(tbl.sort_values("Change, %", ascending=False, na_position="last"),
            caption="Adjusted close, USD. Dell has no 2010 price, so no change is computed.",
            n=f"n = {len(listed) + len(not_listed)} series", source=STOCKS_SRC)
    r.section("Life expectancy")
    r.text(f"Every Middle East country in the Gapminder set gained at least {gain.min():.0f} years. "
           f"{least} gained least, and its curve flattens after 1987.")
    r.figure(figs["life"])
    r.figure(figs["gains"])
    r.save_html(out("report.html"))
    r.save_pdf(out("report.pdf"))


if __name__ == "__main__":
    dropin()
    figs = {"indexed": mpl_indexed("light"), "ranked": mpl_ranked()}
    mpl_indexed("dark")
    figs["life"] = plotly_life("light")
    figs["gains"] = plotly_gains()
    figs["life"].write_image(out("04-plotly-life-light.png"), scale=2)
    figs["gains"].write_image(out("05-plotly-gains-light.png"), scale=2)
    plotly_life("dark").write_image(out("06-plotly-life-dark.png"), scale=2)
    figs["life"].write_html(out("04-plotly-life-light.html"), include_plotlyjs="cdn")
    D.apply("light"); P.apply("light")
    report(figs)
    for f in sorted(os.listdir(OUT)):
        print(f"{os.path.getsize(out(f)) // 1024:>6} KB  {f}")
