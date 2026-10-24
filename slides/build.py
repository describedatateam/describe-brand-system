"""
build.py — the .describe( slide template, 1920 × 1080.

    python3 slides/build.py            writes slides/out/deck.html
    python3 slides/build.py --render   also deck.pdf and one PNG per slide

Eight layouts, each a function you can copy into a client deck: title,
section, big number, chart, outliers, method, statement and close. The sample
content is the canonical Online Retail audit (decisions/uci_audit.json):
every figure on a slide is computed there, nothing is typed in.

The enrichment layer (templates/ENRICHMENT.md) is built in: the measuring
edge carries the slide's position, construction geometry sits behind the
headline figures, dither and illustration only on navy section slides.
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
W, H = 1920, 1080
AUDIT = json.load(open(os.path.join(ROOT, "decisions", "uci_audit.json"), encoding="utf-8"))
SRC = "Source: Online Retail dataset (UCI, public), Dec 2010 to Nov 2011. Analysis by .describe("
MONTHS = ["Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov"]
TOTAL = 8

CSS = """
.pg{padding-left:calc(var(--pad-x) + 24px)}
.s-title .display{max-width:1180px}
.s-kicker{display:flex;gap:28px;align-items:center}
.s-cols{display:grid;grid-template-columns:1.55fr 1fr;gap:96px;align-items:start}
.s-row{display:grid;grid-template-columns:64px 1fr 300px;gap:36px;align-items:center;padding:30px 0;border-top:var(--hair) solid var(--rule)}
.s-row:last-child{border-bottom:var(--hair) solid var(--rule)}
.s-chart svg{width:100%;height:auto;display:block}
"""


def edge(i: int, dark: bool = False) -> str:
    """The deck's spine: a measuring edge with this slide's position seated on it."""
    return (f'<div class="edge-slot">{K.measuring_edge(H - 2 * 92, active_at=(i - 1) / (TOTAL - 1), count=36, major_every=5)}'
            f'</div>')


def foot(src: str = "", right: str | None = None) -> str:
    right = right if right is not None else K.lockup("compact")
    return f'<div class="foot"><div class="src">{src}</div>{right}</div>'


def chart_svg() -> str:
    """The monthly chart, drawn by the chart kit with its instrument furniture."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from describe_charts import mpl as D

    D.apply("light")
    m = AUDIT["monthly_net_gbp"]
    v = [m[k] / 1e6 for k in m]
    x = list(range(12))
    fig, ax = plt.subplots(figsize=(5.9, 3.15))
    D.context(ax, x[:9], v[:9])
    D.story(ax, x[8:], v[8:])
    ax.set_xticks(x, MONTHS)
    ax.set_ylim(0, 1.6)
    D.measuring_edge(ax, "x", minor=0)
    D.index_mark(ax, 11, v[11], f"Nov £{v[11]:.2f}M", side="left")
    D.callout(ax, 4, v[4], 1, dx=10, dy=-26)
    D.callout(ax, 9, v[9], 2, dx=-12, dy=26)
    D.units(ax, y="£ million, net")
    for t in ax.get_xticklabels() + ax.get_yticklabels():
        t.set_fontfamily(D.FONTS["mono"])
    buf = io.StringIO()
    fig.savefig(buf, format="svg", transparent=True, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)
    s = buf.getvalue()
    return s[s.index("<svg"):]


# ---------------------------------------------------------------------------
# The eight layouts
# ---------------------------------------------------------------------------
def s_title(i):
    return K.page(
        K.construction(W, H, 1500, 610, 470)
        + edge(i, dark=True)
        + f"""<div class="s-kicker"><span class="label">Profit snapshot</span><span class="label">Sample deck</span></div>
<div class="display" style="margin-top:150px">See your real profit,<br><span class="em">not just your sales.</span></div>
<div class="lede" style="margin-top:44px;max-width:900px">What a year of store orders says once refunds, cancellations and test orders are taken out.</div>"""
        + foot('<span class="label">describe.team · October 2026</span>'),
        theme="dark", cls="s-title")


def s_section(i):
    return K.page(
        K.dither_layer(W, H, kind="glow", cx=0.78, cy=0.5, hi=0.30)
        + edge(i, dark=True)
        + f"""<div class="row" style="flex:1;align-items:center;gap:120px">
  <div class="col" style="flex:1">
    <span class="label">Section 02</span>
    <div class="opener" style="margin-top:36px">The evidence,<br>and the story told about it.</div>
    <div class="lede" style="margin-top:40px;max-width:760px">Every figure that follows states its rows, its source and the test that flagged it.</div>
  </div>
  {K.art("cygnus", OUT, {"lines": "ink", "stars": "active"}, "width:560px;flex:none")}
</div>"""
        + foot('<span class="label">Cygnus, after al-Sufi · The Met</span>'),
        theme="dark")


def s_number(i):
    m = AUDIT["monthly_net_gbp"]
    share = AUDIT["sep_nov_share"]
    vals = list(m.values())
    return K.page(
        edge(i)
        + f"""<span class="label">Net revenue · Dec 2010 to Nov 2011</span>
<div class="row" style="margin-top:56px;align-items:center;gap:110px">
  <div style="flex:none;margin-left:20px">{K.gauge(share, 520, label="SHARE OF YEAR")}</div>
  <div class="col" style="flex:1">
    <div class="num num--accent" style="font-size:240px">{share * 100:.0f}%</div>
    <div class="h2" style="margin-top:28px">of the year's net revenue came in three months: Sep, Oct and Nov.</div>
  </div>
</div>
<div style="height:120px;margin-top:auto;margin-bottom:28px;opacity:1">{K.data_cells(vals, 1560, 120, rows=8, highlight=(9, 10, 11), cols_per=4)}</div>"""
        + foot(SRC + f". Net £{AUDIT['year_net_gbp'] / 1e6:.2f}M over 12 full months."))


def s_chart(i):
    m = AUDIT["monthly_net_gbp"]
    v = list(m.values())
    low = min(range(9), key=lambda k: v[k])
    return K.page(
        edge(i)
        + f"""<span class="label">Net revenue by month</span>
<div class="h2" style="margin-top:28px;max-width:1300px">The year turned in September; November alone was 15% of it.</div>
<div class="s-cols" style="margin-top:48px">
  <div class="s-chart">{chart_svg()}</div>
  <div class="stack" style="padding-top:40px">
    {K.callout(1, f"{MONTHS[low]} was the low point: £{v[low] / 1e6:.2f}M, a third of November.")}
    {K.callout(2, f"From September the run rate stepped up to £{v[9] / 1e6:.2f}M a month and kept rising.")}
  </div>
</div>"""
        + foot(f"n = {AUDIT['window_sale_lines']:,} sale lines. " + SRC + "."))


def s_outliers(i):
    rule = "robust z > 7"
    rows = "".join(
        f"""<div class="s-row">
  {K.outlier_ring(54, rule)}
  <div><div class="num void" style="font-size:96px">£{r['val'] / 1000:,.0f}K</div>
       <div class="body" style="margin-top:10px">{r['Description'].replace(' ,', ',').capitalize()} · {r['Quantity']:,} units</div></div>
  <div style="text-align:right"><div class="label">Invoice</div><div class="num" style="font-size:44px;margin-top:8px">{r['InvoiceNo']}</div></div>
</div>""" for r in sorted(AUDIT["flagged_lines"], key=lambda r: -r["val"]))
    return K.page(
        edge(i)
        + f"""<span class="label">The three biggest order lines</span>
<div class="row" style="margin-top:28px;gap:96px;align-items:flex-start">
  <div class="col" style="flex:1">
    <div class="h2">The three biggest sales never happened.</div>
    <div style="margin-top:44px">{rows}</div>
  </div>
  <div class="col" style="width:420px;flex:none;padding-top:24px">
    {K.art("cygnus-outside", OUT, {"lines": "ink", "stars": "active", "outside": "mark"})}
    <div class="body" style="margin-top:28px">Each line sits more than seven robust deviations above a median line of £9.90, and each was cancelled the same day.</div>
  </div>
</div>"""
        + foot(f"Outlier test: {AUDIT['outlier_rule']}. " + SRC + "."))


def s_method(i):
    a = AUDIT
    steps = [(f"{a['rows']:,}", "rows as exported"),
             (f"−{a['duplicates']:,}", "exact duplicates"),
             (f"−{a['cancellation_lines']:,}", "cancellations"),
             (f"−{a['nonproduct_lines']:,}", "postage, fees"),
             (f"−{a['zero_or_negative_lines']:,}", "zero or negative"),
             (f"{a['clean_sale_lines']:,}", "clean sale lines")]
    return K.page(
        K.construction(W, H, 1720, 120, 300)
        + edge(i)
        + f"""<span class="label">Method</span>
<div class="h2" style="margin-top:28px;max-width:1250px">Four checks stand between the export and a number you can decide with.</div>
<div style="margin-top:150px">{K.process(steps, 1560, 150, active=5)}</div>
<div class="row" style="margin-top:110px;gap:72px">
  <div class="col" style="flex:1">{K.callout(1, "Duplicates are rows identical in every field, kept once.")}</div>
  <div class="col" style="flex:1">{K.callout(2, "Cancellations are the invoices whose number starts with C.")}</div>
  <div class="col" style="flex:1">{K.callout(3, "Postage, bank charges and manual adjustments are not products.")}</div>
</div>"""
        + foot(SRC + "."))


def s_statement(i):
    a = AUDIT
    return K.page(
        K.construction(W, H, 470, 520, 400)
        + edge(i)
        + f"""<span class="label">Customers</span>
<div class="row" style="flex:1;align-items:center;gap:120px">
  <div class="num num--accent" style="font-size:300px;width:640px;text-align:center;flex:none">{a['customers_for_half']}</div>
  <div class="col" style="flex:1">
    <div class="opener">customers brought in half of the revenue.</div>
    <div class="lede" style="margin-top:40px;max-width:780px">Out of {a['customers_known']:,} with a customer ID. {a['missing_customer_value_share'] * 100:.0f}% of sales value has no ID at all.</div>
  </div>
</div>"""
        + foot(SRC + "."),
        theme="brass")


def s_close(i):
    return K.page(
        K.orbit_fill(W, H, pitch=150, r=34).replace('class="geo layer"', 'class="geo layer fade-left"', 1)
        + K.dither_layer(W, H, kind="rise", hi=0.32)
        + f"""<div class="col" style="flex:1;justify-content:center;max-width:1100px">
  <span class="label">Next step</span>
  <div class="opener" style="margin-top:32px">Ask for a Profit Snapshot.</div>
  <div class="lede" style="margin-top:36px">Send your store's order export. We send back what you keep after costs, returns and cash on delivery.</div>
  <div class="h3 em" style="margin-top:56px">info@describe.team</div>
</div>"""
        + foot('<span class="label">describe.team</span>', K.lockup("primary")),
        theme="dark")


LAYOUTS = [s_title, s_section, s_number, s_chart, s_outliers, s_method, s_statement, s_close]


def build() -> str:
    os.makedirs(OUT, exist_ok=True)
    pages = [f(i) for i, f in enumerate(LAYOUTS, 1)]
    html = K.page_doc(pages, OUT, W, H, "slides", ".describe( slide template").replace(
        "</style>", CSS + "</style>", 1)
    path = os.path.join(OUT, "deck.html")
    open(path, "w", encoding="utf-8").write(html)
    return path


if __name__ == "__main__":
    p = build()
    print(p)
    if "--render" in sys.argv:
        from render import render
        for f in render(p, os.path.join(OUT, "png"), os.path.join(OUT, "deck.pdf"), prefix="slide-"):
            print(f)
