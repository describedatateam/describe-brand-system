"""
build.py — the reference dashboard for .describe( data apps.

    python3 apps/build.py            writes apps/out/dashboard.html (+ dashboard-dark.html)
    python3 apps/build.py --render   also apps/out/png/dashboard-{light,dark}.png

One static page built from ui/ui.css, the tokens and apps/app.css: nav, a
header whose title is the finding, four KPI tiles with sparklines, a chart
panel with the chart kit's instrument furniture, a flagged-lines table, and a
method strip. Every figure comes from decisions/uci_audit.json. The Streamlit
version of the same page is apps/streamlit_app.py.
"""

from __future__ import annotations

import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "templates"))
sys.path.insert(0, os.path.join(ROOT, "charts", "kit"))

import kit as K  # noqa: E402

OUT = os.path.join(HERE, "out")
AUDIT = json.load(open(os.path.join(ROOT, "decisions", "uci_audit.json"), encoding="utf-8"))
MONTHS = ["Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov"]
SRC = "Online Retail dataset (UCI, public), Dec 2010 to Nov 2011"


def sparkline(values, story_from=None, w=240, h=44, pad=4):
    """The tile's own series: context grey, the story stretch in active,
    a dot on the latest value. No axes: the tile's value is the reading."""
    lo, hi = min(values), max(values)
    xs = [pad + (w - 2 * pad) * i / (len(values) - 1) for i in range(len(values))]
    ys = [h - pad - (h - 2 * pad) * (v - lo) / ((hi - lo) or 1) for v in values]
    pts = lambda a, b: " ".join(f"{x:.1f},{y:.1f}" for x, y in list(zip(xs, ys))[a:b])
    s = story_from if story_from is not None else len(values) - 1
    return (f'<svg class="kpi__spark spark" viewBox="0 0 {w} {h}" preserveAspectRatio="none" aria-hidden="true">'
            f'<line class="base" x1="0" y1="{h - 0.5}" x2="{w}" y2="{h - 0.5}"/>'
            f'<polyline class="ctx" points="{pts(0, s + 1)}"/>'
            f'<polyline class="story" points="{pts(s, None)}"/>'
            f'<circle class="end" cx="{xs[-1]:.1f}" cy="{ys[-1]:.1f}" r="3.2"/></svg>')


def chart_svg(mode: str) -> str:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from describe_charts import mpl as D

    D.apply(mode)
    m = AUDIT["monthly_net_gbp"]
    v = [m[k] / 1e6 for k in m]
    x = list(range(12))
    low = min(range(9), key=lambda k: v[k])
    fig, ax = plt.subplots(figsize=(7.4, 3.3))
    D.context(ax, x[:9], v[:9])
    D.story(ax, x[8:], v[8:])
    ax.set_xticks(x, MONTHS)
    ax.set_ylim(0, 1.6)
    D.measuring_edge(ax, "x", minor=0)
    D.index_mark(ax, 11, v[11], f"Nov £{v[11]:.2f}M", side="left")
    D.callout(ax, low, v[low], 1, dx=10, dy=-26)
    D.units(ax, y="£ million, net")
    for t in ax.get_xticklabels() + ax.get_yticklabels():
        t.set_fontfamily(D.FONTS["mono"])
    buf = io.StringIO()
    fig.savefig(buf, format="svg", transparent=True, bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)
    s = buf.getvalue()
    return s[s.index("<svg"):]


def page(mode: str) -> str:
    a = AUDIT
    m = a["monthly_net_gbp"]
    v = list(m.values())
    nov_vs_oct = v[11] / v[10] - 1
    low = min(range(9), key=lambda k: v[k])
    rel = lambda p: os.path.relpath(os.path.join(ROOT, p), OUT).replace(os.sep, "/")

    kpis = [
        ("Net revenue", f"£{a['year_net_gbp'] / 1e6:.2f}<small>M</small>",
         f'<span class="pos d-num">+{nov_vs_oct * 100:.1f}%</span> November vs October', sparkline(v, 9)),
        ("Customers with an ID", f"{a['customers_known']:,}",
         f"{a['customers_for_half']} of them bring in half the revenue", ""),
        ("Sales value with no customer ID", f"{a['missing_customer_value_share'] * 100:.1f}<small>%</small>",
         f"{a['missing_customer_lines_clean']:,} sale lines carry no ID; they count in revenue, not in customers", ""),
        ("Lines flagged as outliers", f'<span class="d-outlier">{len(a["flagged_lines"])}</span>',
         "robust z &gt; 7 on line value; all three were cancelled", ""),
    ]
    tiles = "".join(
        f'<div class="kpi"><span class="kpi__label">{l}</span><span class="kpi__value">{val}</span>'
        f'<span class="kpi__note">{note}</span>{spark}</div>' for l, val, note, spark in kpis)

    rows = "".join(
        f'<tr><td>{r["Description"].replace(" ,", ",").capitalize()}</td>'
        f'<td class="num">{r["Quantity"]:,}</td>'
        f'<td class="num"><span class="d-outlier">{r["val"]:,.0f}</span></td></tr>'
        for r in sorted(a["flagged_lines"], key=lambda r: -r["val"]))

    steps = [(f"{a['rows']:,}", "rows as exported"), (f"−{a['duplicates']:,}", "duplicates"),
             (f"−{a['cancellation_lines']:,}", "cancellations"), (f"−{a['nonproduct_lines']:,}", "postage, fees"),
             (f"−{a['zero_or_negative_lines']:,}", "zero or negative"), (f"{a['clean_sale_lines']:,}", "clean sale lines")]

    return f"""<!doctype html>
<html lang="en" data-theme="{mode}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Store health · .describe( reference dashboard</title>
<link rel="stylesheet" href="{rel('tokens/dist/tokens.css')}">
<link rel="stylesheet" href="{rel('ui/ui.css')}">
<link rel="stylesheet" href="{rel('apps/app.css')}">
<style>{K.font_css(OUT)}</style></head>
<body style="margin:0">
<section class="pg app">
<nav class="d-nav app__nav" aria-label="Dashboard">
  <a class="d-nav__brand" href="#">{K.lockup("compact")}</a>
  <div class="d-nav__links">
    <a class="d-nav__link" href="#" aria-current="page">Overview</a>
    <a class="d-nav__link" href="#">Orders</a>
    <a class="d-nav__link" href="#">Customers</a>
    <a class="d-nav__link" href="#">Data quality</a>
  </div>
</nav>
<main class="app__main">
  <header class="app__head">
    <div>
      <span class="app__eyebrow">Store health</span>
      <h1 class="app__title" style="margin:8px 0 10px">Sep to Nov brought in {a['sep_nov_share'] * 100:.0f}% of the year.</h1>
      <p class="app__dek" style="margin:0">Net revenue after duplicates, cancellations, postage and fees are taken out. Twelve full months.</p>
    </div>
    <div class="app__filters">
      <span class="d-chip" data-state="live">Dec 2010 – Nov 2011</span>
      <span class="d-chip">All 38 countries</span>
      <button class="d-btn d-btn--sm d-btn--quiet" type="button">Export</button>
    </div>
  </header>

  <section class="kpis" aria-label="Key figures">{tiles}</section>

  <div class="grid2">
    <div class="d-panel">
      <div class="d-panel__head"><span class="d-panel__title">Net revenue by month</span>
        <span class="d-panel__meta">n = {a['window_sale_lines']:,} lines</span></div>
      <div class="d-panel__body">
        <div class="chart">{chart_svg(mode)}</div>
        <div class="notes">
          <div class="note"><b>01</b><span>{MONTHS[low]} was the low point at £{v[low] / 1e6:.2f}M, a third of November.</span></div>
        </div>
      </div>
    </div>
    <div class="d-panel">
      <div class="d-panel__head"><span class="d-panel__title">Flagged order lines</span>
        <span class="d-panel__meta">robust z &gt; 7</span></div>
      <div class="d-tablewrap">
        <table class="d-table">
          <thead><tr><th scope="col">Product</th><th scope="col" class="num">Units</th>
            <th scope="col" class="num">Value, £</th></tr></thead>
          <tbody>{rows}</tbody>
          <caption>n = {len(a['flagged_lines'])} of {a['clean_sale_lines']:,} lines · median line £9.90</caption>
        </table>
      </div>
      <div class="d-panel__body" style="font-size:13.5px;color:var(--body);line-height:1.5">
        The value is circled, not removed. Each line was cancelled the same day, so it never counts as revenue.
      </div>
    </div>
  </div>

  <div class="d-panel d-panel--edge">
    <div class="d-panel__head"><span class="d-panel__title">From export to clean lines</span>
      <span class="d-panel__meta">4 checks</span></div>
    <div class="d-panel__body method">{K.process(steps, 1340, 100, active=5, value_size=22, label_size=13.5)}</div>
  </div>

  <footer class="provenance">
    <span><span class="n">n = {a['window_sale_lines']:,} sale lines</span> · Source: {SRC}. Computed 24 Oct 2026.</span>
    <span>Outliers: {a['outlier_rule']}</span>
  </footer>
</main>
</section>
</body></html>"""


def build() -> list[str]:
    os.makedirs(OUT, exist_ok=True)
    paths = []
    for mode, name in (("light", "dashboard.html"), ("dark", "dashboard-dark.html")):
        p = os.path.join(OUT, name)
        open(p, "w", encoding="utf-8").write(page(mode))
        paths.append(p)
    return paths


if __name__ == "__main__":
    ps = build()
    import describe_streamlit
    os.makedirs(os.path.join(HERE, ".streamlit"), exist_ok=True)
    cfg = os.path.join(HERE, ".streamlit", "config.toml")
    open(cfg, "w", encoding="utf-8").write(describe_streamlit.config_toml())
    ps_out = ps + [cfg]
    print("\n".join(ps_out))
    if "--render" in sys.argv:
        from render import render
        for p, mode in zip(ps, ("light", "dark")):
            for f in render(p, os.path.join(OUT, "png"), prefix=f"dashboard-{mode}-", viewport=(1440, 1000)):
                print(f)
