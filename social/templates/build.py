"""
build.py — the .describe( social templates.

    python3 social/templates/build.py            writes social/templates/out/*.html
    python3 social/templates/build.py --render   also one PNG per post and carousel.pdf

A six-card carousel at 4:5 (1080 × 1350) whose cards double as single-post
templates: cover, big number, outliers, chart, method and close. The big
number card is also built at 1:1 (1080 × 1080) and 9:16 (1080 × 1920) to show
how a layout moves between formats: the type and the elements stay, the
spacing absorbs the difference.

Figures come from decisions/uci_audit.json; nothing is typed in. Coral appears
only as the outlier ring, with its test in the source line.
"""

from __future__ import annotations

import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "templates"))
sys.path.insert(0, os.path.join(ROOT, "charts", "kit"))

import kit as K  # noqa: E402

OUT = os.path.join(HERE, "out")
AUDIT = json.load(open(os.path.join(ROOT, "decisions", "uci_audit.json"), encoding="utf-8"))
SRC = "Source: Online Retail dataset (UCI, public), Dec 2010 to Nov 2011. Analysis by .describe("
MONTHS = ["Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov"]
N = 6

CSS = """
.pg .foot{gap:32px}
.top{display:flex;justify-content:space-between;align-items:center}
.vrow{display:grid;grid-template-columns:48px 1fr;gap:28px;align-items:center;padding:22px 0;border-top:var(--hair) solid var(--rule)}
.vrow:last-child{border-bottom:var(--hair) solid var(--rule)}
.step{display:grid;grid-template-columns:28px 1fr auto;gap:28px;align-items:baseline;padding:20px 0}
.step__dot{width:18px;height:18px;border-radius:50%;border:2.5px solid var(--ink);align-self:center;background:var(--pg-ground)}
.step--on .step__dot{background:var(--accent);border-color:var(--accent)}
.steps{position:relative}
.steps::before{content:"";position:absolute;left:8px;top:40px;bottom:40px;width:1.5px;background:var(--dim)}
.s-chart svg{width:100%;height:auto;display:block}
"""


def top(i: int, label: str) -> str:
    """Label left, the carousel position as a tally right."""
    return f'<div class="top"><span class="label">{label}</span>{K.tally(i, N, height=24, pitch=11, w=3)}</div>'


def foot(src: str = "") -> str:
    return f'<div class="foot"><div class="src">{src}</div>{K.lockup("compact")}</div>'


def chart_svg() -> str:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from describe_charts import mpl as D

    D.apply("light")
    m = AUDIT["monthly_net_gbp"]
    v = [m[k] / 1e6 for k in m]
    x = list(range(12))
    fig, ax = plt.subplots(figsize=(4.2, 3.15))
    ax.bar(x, v, color=[D.C()["story"] if k >= 9 else D.C()["context"] for k in x], width=0.68)
    ax.set_xticks(x, [mm[0] for mm in MONTHS])
    ax.set_ylim(0, 1.6)
    D.measuring_edge(ax, "x", minor=0)
    D.index_mark(ax, 11, v[11], f"£{v[11]:.2f}M", side="left", length=30)
    D.units(ax, y="£ million, net")
    for t in ax.get_xticklabels() + ax.get_yticklabels():
        t.set_fontfamily(D.FONTS["mono"])
    buf = io.StringIO()
    fig.savefig(buf, format="svg", transparent=True, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)
    s = buf.getvalue()
    return s[s.index("<svg"):]


# ---------------------------------------------------------------------------
def cover(W, H):
    return K.page(
        K.dither_layer(W, H, kind="glow", cx=0.75, cy=0.62, hi=0.30)
        + top(1, "Online stores")
        + f"""<div class="opener" style="margin-top:96px">Years of sales data.<br><span class="em">Not enough trust</span> to decide with it.</div>
<div style="margin-top:auto;display:flex;justify-content:flex-end">{K.art("libra", OUT, {"lines": "ink", "stars": "active"}, "width:640px;margin-right:-40px")}</div>
<div class="label" style="margin-top:28px;margin-bottom:8px;color:var(--active)">Swipe →</div>"""
        + foot('<span class="label">Libra, after al-Sufi · The Met</span>'),
        theme="dark")


def number(W, H, i=2):
    a = AUDIT
    big = 380 if H >= 1350 else 300
    r = 330 if H >= 1350 else 280
    cy = 520 if H > 1400 else (430 if H >= 1350 else 380)
    return K.page(
        K.construction(W, H, W * 0.36, cy + (H - 1350) * 0.25 if H > 1350 else cy, r)
        + top(i, "Customers")
        + f"""<div class="grow col" style="justify-content:center">
  <div class="num num--accent" style="font-size:{big}px;margin-left:-12px">{a['customers_for_half']}</div>
  <div class="h2" style="margin-top:36px">customers brought in half of the revenue.</div>
  <div class="lede" style="margin-top:32px">Out of {a['customers_known']:,} with a customer ID. Could you name your top 10?</div>
</div>"""
        + foot(SRC + "."))


def outliers(W, H, i=3):
    rule = "robust z > 7"
    rows = "".join(
        f"""<div class="vrow">{K.outlier_ring(44, rule)}
<div style="display:flex;justify-content:space-between;align-items:baseline;gap:24px">
  <div><div class="num void" style="font-size:88px">£{r['val'] / 1000:,.0f}K</div>
  <div class="body" style="margin-top:8px;font-size:26px">{r['Description'].replace(' ,', ',').capitalize()}</div></div>
  <div style="text-align:right;flex:none"><div class="label">Invoice</div><div class="num" style="font-size:36px;margin-top:6px">{r['InvoiceNo']}</div></div>
</div></div>""" for r in sorted(AUDIT["flagged_lines"], key=lambda r: -r["val"]))
    return K.page(
        top(i, "The 3 biggest order lines")
        + f"""<div class="h2" style="margin-top:40px">The three biggest sales never happened.</div>
<div style="margin-top:48px">{rows}</div>
<div class="lede" style="margin-top:36px;font-size:32px">Count them and they top your revenue, your product ranking and your customer list.</div>"""
        + foot(f"Flagged by {AUDIT['outlier_rule']}. " + SRC + "."))


def chart(W, H, i=4):
    share = AUDIT["sep_nov_share"]
    return K.page(
        top(i, "Net revenue by month")
        + f"""<div class="h2" style="margin-top:40px">Sep, Oct and Nov brought in <span class="em">{share * 100:.0f}%</span> of the year.</div>
<div class="s-chart" style="margin-top:56px">{chart_svg()}</div>"""
        + foot(f"n = {AUDIT['window_sale_lines']:,} sale lines. " + SRC + "."))


def method(W, H, i=5):
    a = AUDIT
    steps = [(f"{a['rows']:,}", "rows as exported", False),
             (f"−{a['duplicates']:,}", "exact duplicates", False),
             (f"−{a['cancellation_lines']:,}", "cancellations", False),
             (f"−{a['nonproduct_lines']:,}", "postage and fees", False),
             (f"−{a['zero_or_negative_lines']:,}", "zero or negative", False),
             (f"{a['clean_sale_lines']:,}", "clean sale lines", True)]
    rows = "".join(
        f'<div class="step{" step--on" if on else ""}"><span class="step__dot"></span>'
        f'<span class="body" style="font-size:32px">{lab}</span>'
        f'<span class="num{" num--accent" if on else ""}" style="font-size:48px">{val}</span></div>'
        for val, lab, on in steps)
    return K.page(
        K.construction(W, H, W + 60, 260, 360)
        + top(i, "Method")
        + f"""<div class="h2" style="margin-top:40px">Four checks before a number you can decide with.</div>
<div class="steps" style="margin-top:56px">{rows}</div>"""
        + foot(SRC + "."),
        theme="brass")


def close(W, H, i=6):
    return K.page(
        K.orbit_fill(W, H, pitch=130, r=30).replace('class="geo layer"', 'class="geo layer fade-up"', 1)
        + top(i, "Your store")
        + """<div class="opener" style="margin-top:96px">Which of these would you rather know than guess?</div>
<div class="lede" style="margin-top:44px">We turn your store's order export into numbers you can check, cleaned and sourced.</div>
<div class="h3 em" style="margin-top:64px">describe.team</div>"""
        + foot(),
        theme="dark")


def build() -> list[str]:
    os.makedirs(OUT, exist_ok=True)
    paths = []
    sets = {
        "carousel-4x5": (1080, 1350, [cover, number, outliers, chart, method, close]),
        "number-1x1": (1080, 1080, [number]),
        "number-9x16": (1080, 1920, [number]),
    }
    for name, (W, H, fns) in sets.items():
        pages = [f(W, H) for f in fns]
        html = K.page_doc(pages, OUT, W, H, "social", f".describe( social · {name}").replace(
            "</style>", CSS + "</style>", 1)
        p = os.path.join(OUT, f"{name}.html")
        open(p, "w", encoding="utf-8").write(html)
        paths.append(p)
    return paths


if __name__ == "__main__":
    ps = build()
    print("\n".join(ps))
    if "--render" in sys.argv:
        from render import render
        for p in ps:
            name = os.path.splitext(os.path.basename(p))[0]
            pdf = os.path.join(OUT, "carousel.pdf") if name.startswith("carousel") else None
            for f in render(p, os.path.join(OUT, "png"), pdf, prefix=name + "-"):
                print(f)
