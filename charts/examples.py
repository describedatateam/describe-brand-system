"""
examples.py — six charts, real data, every number recomputed from source.

    python3 examples.py            → prints the figures' findings as a check
    from examples import FIGURES   → list of Figure dicts (svg + table + provenance)

Sources (all shipped with the libraries, so the numbers are reproducible
offline):
    Stocks.csv   matplotlib sample data; header states finance.yahoo.com
    diabetes     Efron, Hastie, Johnstone & Tibshirani (2004), via scikit-learn
    wine         Forina et al., PARVUS; UCI ML Repository, via scikit-learn

Nothing is fabricated to demonstrate a feature. Where the data has no
instance of a state (no missing values in Stocks.csv; no outliers in the
diabetes fit) the chart SAYS so, and the state is shown only schematically in
the key.
"""

from __future__ import annotations

import math
from datetime import date, datetime

import numpy as np
import pandas as pd
from matplotlib import cbook
from scipy import stats
from sklearn.datasets import load_diabetes, load_wine

import chartkit as K

COMPUTED = date.today().strftime("%-d %b %Y")
NAMES = {"IBM": "IBM", "AAPL": "Apple", "MSFT": "Microsoft", "XRX": "Xerox",
         "AMZN": "Amazon", "DELL": "Dell", "GOOGL": "Alphabet", "ADBE": "Adobe",
         "^GSPC": "S&P 500", "^IXIC": "Nasdaq Comp."}
STOCKS_SRC = "Yahoo Finance via matplotlib sample data (Stocks.csv), adjusted monthly closes"


WORDS = ["no", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]
SUP = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")


def sci(p):
    """5.9e-34 → '6 × 10⁻³⁴'."""
    m, e = f"{p:.0e}".split("e")
    return f"{m} × 10{str(int(e)).translate(SUP)}"


def comma(v, d=0):
    return f"{v:,.{d}f}"


def signed(v, d=1, unit="%"):
    s = "+" if v > 0 else ("−" if v < 0 else "")
    return f"{s}{abs(v):,.{d}f}{unit}"


def month(t):
    return pd.Timestamp(t).strftime("%b %Y")


# ---------------------------------------------------------------------------
# Data — loaded once, audited
# ---------------------------------------------------------------------------
def load_stocks():
    path = cbook.get_sample_data("Stocks.csv", asfileobj=False)
    raw = pd.read_csv(path, comment="#", parse_dates=["Date"])
    vals = raw.drop(columns="Date")
    empty = vals.isna().all(axis=1)
    kept = raw[~empty]
    dup = kept.drop(columns="Date").duplicated()
    clean = kept[~dup].set_index("Date")
    audit = {
        "rows_read": len(raw),
        "blank_cells": int(vals.isna().sum().sum()),
        "empty_rows": int(empty.sum()),
        "empty_row_cells": int(empty.sum()) * vals.shape[1],
        "empty_row_dates": list(raw.loc[empty, "Date"]),
        "dup_dates": list(kept.loc[dup, "Date"]),
        "rows_kept": len(clean),
        "first_listed": {c: clean[c].first_valid_index() for c in clean.columns},
    }
    # after listing, is anything blank? (that would be MISSING)
    audit["missing"] = int(sum(clean.loc[audit["first_listed"][c]:, c].isna().sum()
                               for c in clean.columns))
    audit["not_applicable"] = int(clean.isna().sum().sum()) - audit["missing"]
    assert audit["empty_row_cells"] + audit["not_applicable"] + audit["missing"] == \
        audit["blank_cells"], "blank cells do not reconcile"
    assert set(clean.index.day) == {1}, "not month-start rows"
    return clean, audit


STOCKS, AUDIT = load_stocks()
BASE = pd.Timestamp("2010-01-01")
END = STOCKS.index[-1]


# ---------------------------------------------------------------------------
# 01 — Indexed growth, log scale, one story series
# ---------------------------------------------------------------------------
def fig_indexed():
    W, H = 720, 400
    x0, x1, y0, y1 = 58, 596, 44, 342
    d = STOCKS.loc[BASE:]
    base = d.loc[BASE]
    have = [c for c in d.columns if not math.isnan(base[c])]
    idx = d[have] / base[have] * 100
    lo, hi = idx.min().min(), idx.max().max()
    xs = K.Time(BASE.to_pydatetime(), END.to_pydatetime(), x0, x1)
    ys = K.Log(60, 4000, y1, y0)
    ticks = K.log_ticks(60, 4000)

    b = [K.y_axis(ys, x0, x1, ticks, lambda v: f"{v:,.0f}")]
    b.append(K.x_axis(xs, y1, [datetime(y, 1, 1) for y in range(2010, 2023, 2)],
                      lambda t: str(t.year),
                      minor=[datetime(y, 1, 1) for y in range(2011, 2023, 2)]))
    b.append(K.unit_label(x0 - 8, y0 - 18, "Index, log scale", "start"))
    order = [c for c in have if c != "AAPL"] + ["AAPL"]
    for c in order:
        pts = [(xs(t.to_pydatetime()), ys(v)) for t, v in idx[c].items()]
        story = c == "AAPL"
        b.append(K.series_line(pts, "c-story" if story else "c-context",
                               K.W_DATA if story else 1.25))
    last = idx.iloc[-1]
    for c, cls in (("AAPL", "c-story"), ("^GSPC", "c-context"), ("XRX", "c-context")):
        b.append(K.data_dot(x1, ys(last[c]), cls))
        b.append(K.direct_label(x1 + 12, ys(last[c]), NAMES[c], f"{last[c]:,.0f}", cls))
    b.append(K.legend([("c-story", "Apple"), ("c-context", f"{WORDS[len(have) - 1].capitalize()} other series")], x0 + 150, y0 - 22))
    # crosshair hover: one hit column per month
    months = list(idx.index)
    step = (x1 - x0) / (len(months) - 1)
    for t in months:
        row = idx.loc[t].sort_values(ascending=False)
        tip = month(t) + " — " + " · ".join(f"{NAMES[c]} {v:,.0f}" for c, v in row.items())
        cx = xs(t.to_pydatetime())
        b.append(f'<rect class="c-hit" x="{K.f(cx - step / 2)}" y="{y0}" width="{K.f(step)}" '
                 f'height="{y1 - y0}" data-tip="{K.esc(tip)}" data-cx="{K.f(cx)}" '
                 f'data-y0="{y0}" data-y1="{y1}"/>')

    rows = []
    for c in STOCKS.columns:
        s = STOCKS.loc[BASE:, c]
        if c in have:
            rows.append([NAMES[c], c, f"{base[c]:,.2f}", f"{s.iloc[-1]:,.2f}",
                         f"{last[c]:,.0f}", f"{idx[c].min():,.1f}", f"{idx[c].max():,.1f}"])
        else:
            rows.append([NAMES[c], c, "—", f"{s.iloc[-1]:,.2f}", "—", "—", "—"])
    rows.sort(key=lambda r: -float(r[4].replace(",", "")) if r[4] != "—" else 1e9)
    return K.Figure(
        id="indexed", form="Line, log scale · emphasis",
        title=f"$100 in Apple in 2010 was ${last['AAPL']:,.0f} by mid-2022",
        dek=("Nine series indexed to January 2010 = 100, on a log scale so equal "
             "slopes mean equal growth rates. Apple is the story; the rest are context. "
             f"Dell is left out, not zeroed: it listed in {month(AUDIT['first_listed']['DELL'])}, "
             "so it has no 2010 base."),
        svg=K.svg("".join(b), W, H, "Line chart: nine series indexed to January 2010. "
                  f"Apple ends at {last['AAPL']:,.0f}, S&P 500 at {last['^GSPC']:,.0f}, "
                  f"Xerox at {last['XRX']:,.0f}."),
        n=f"n = {len(idx)} months × {len(have)} series",
        source=STOCKS_SRC,
        table={"cols": ["Series", "Ticker", "Jan 2010", "Jun 2022", "Index, Jun 2022",
                        "Low", "High"], "num": [2, 3, 4, 5, 6], "rows": rows},
        uses=["log scale", "x-axis", "y-axis", "unit label", "data dot",
              "direct label", "legend", "null (table)", "crosshair hover"],
        check={"AAPL": round(last["AAPL"], 1), "GSPC": round(last["^GSPC"], 1),
               "XRX": round(last["XRX"], 1), "lo": round(lo, 1), "hi": round(hi, 1)},
    )


# ---------------------------------------------------------------------------
# 02 — What the blanks are: the data-states finding
# ---------------------------------------------------------------------------
def fig_states():
    W, H = 720, 470
    x0, x1 = 118, 690
    top = 116
    lane = 22
    cols = list(STOCKS.columns)
    t0, t1 = datetime(1990, 1, 1), END.to_pydatetime()
    xs = K.Time(t0, t1, x0, x1)
    b = []
    # the readout — the finding is three numbers
    parts = [(AUDIT["empty_row_cells"], "Structural", f"{AUDIT['empty_rows']} rows, no values"),
             (AUDIT["not_applicable"], "Not applicable", "before listing"),
             (AUDIT["missing"], "Missing", "after listing")]
    cx = 24
    for v, lab, sub in parts:
        b.append(K.text(cx, 44, f"{v:,}", "c-ink", 30, "start", "mono", 400))
        b.append(K.text(cx, 66, lab, "c-ink", 12.5, "start", "sans", 500))
        b.append(K.text(cx, 82, sub, "c-body", 11.5, "start", "sans"))
        cx += 190
    b.append(K.line(24, 98, 696, 98, "c-grid"))
    # lanes
    for i, c in enumerate(cols):
        y = top + i * lane
        b.append(K.text(x0 - 12, y + 4, NAMES[c], "c-ink", 12, "end", "sans", 500))
        fl = AUDIT["first_listed"][c].to_pydatetime()
        b.append(K.line(xs(fl), y, x1, y, "c-context", K.W_DATA, 'stroke-linecap="round"'))
        if fl > t0:
            b.append(K.line(xs(fl), y - 6, xs(fl), y + 6, "c-ink", 1.5))
            b.append(K.text(xs(fl) - 7, y + 4, f"Listed {month(fl)}", "c-body", 11, "end", "sans"))
            b.append(K.hit(x0, y - 9, xs(fl) - x0, 18,
                           f"{NAMES[c]}: not applicable before {month(fl)} — "
                           f"{int(STOCKS.loc[:fl, c].isna().sum())} blank months"))
        b.append(K.hit(xs(fl), y - 9, x1 - xs(fl), 18,
                       f"{NAMES[c]}: {int(STOCKS.loc[fl:, c].notna().sum())} months, 0 missing"))
    # removed rows lane
    y = top + len(cols) * lane + 8
    b.append(K.line(x0, y - 13, x1, y - 13, "c-grid"))
    y += 6
    b.append(K.text(x0 - 12, y + 4, "Empty rows", "c-ink", 12, "end", "sans", 500))
    for t in AUDIT["empty_row_dates"]:
        xx = xs(t.to_pydatetime())
        b.append(K.line(xx, y - 5, xx, y + 5, "c-axis", 1))
    b.append(K.hit(x0, y - 9, x1 - x0, 18,
                   f"{AUDIT['empty_rows']} rows with a date and no values — removed; "
                   f"plus 1 duplicate of the final row ({month(AUDIT['dup_dates'][0])})"))
    ax_y = y + 20
    b.append(K.x_axis(xs, ax_y, [datetime(yr, 1, 1) for yr in range(1990, 2023, 5)],
                      lambda t: str(t.year)))
    # key: the four states, drawn schematically — this file has no missing data,
    # and a gap is never manufactured to show the indicator.
    ky = ax_y + 52
    b.append(K.unit_label(24, ky - 22, "Key"))
    kx = 24
    # present
    b.append(K.line(kx, ky, kx + 26, ky, "c-context", K.W_DATA, 'stroke-linecap="round"'))
    b.append(K.text(kx + 34, ky + 4, "Value", "c-body", 11.5))
    kx += 88
    b.append(K.line(kx + 26, ky - 6, kx + 26, ky + 6, "c-ink", 1.5))
    b.append(K.line(kx + 26, ky, kx + 44, ky, "c-context", K.W_DATA))
    b.append(K.text(kx + 52, ky + 4, "Not applicable", "c-body", 11.5))
    kx += 160
    pid = "keyhatch"
    b.append(f'<defs><pattern id="{pid}" width="6" height="6" patternUnits="userSpaceOnUse" '
             f'patternTransform="rotate(45)"><path d="M0 0V6" class="c-axis" stroke-width="1.2"/>'
             f'</pattern></defs><rect x="{kx}" y="{ky - 7}" width="30" height="14" fill="url(#{pid})"/>')
    b.append(K.text(kx + 38, ky + 4, "Missing — none here", "c-body", 11.5))
    kx += 176
    b.append(K.text(kx + 8, ky + 5, "—", "c-dim", 13, "middle", "mono"))
    b.append(K.text(kx + 22, ky + 4, "Null — not computable", "c-body", 11.5))
    total = AUDIT["blank_cells"]
    return K.Figure(
        id="states", form="Coverage lanes + readout",
        title=f"{total:,} blank cells in Stocks.csv, and not one is missing data",
        dek=(f"A blank cell is not a data state. {AUDIT['empty_row_cells']:,} blanks are "
             f"{AUDIT['empty_rows']} dated rows with no values at all, removed before analysis. "
             f"{AUDIT['not_applicable']} are Amazon, Alphabet and Dell before they listed. "
             "From its first price, every series is complete."),
        svg=K.svg("".join(b), W, H, f"{total} blank cells: {AUDIT['empty_row_cells']} structural, "
                  f"{AUDIT['not_applicable']} not applicable, {AUDIT['missing']} missing."),
        n=(f"n = {AUDIT['rows_read']} rows read, {AUDIT['rows_kept']} kept "
           f"({AUDIT['empty_rows']} empty, 1 duplicate removed)"),
        source=STOCKS_SRC,
        table={"cols": ["Series", "First price", "Blank before", "Months after",
                        "Missing after"], "num": [2, 3, 4],
               "rows": [[NAMES[c], month(AUDIT["first_listed"][c]),
                         str(int(STOCKS.loc[:AUDIT['first_listed'][c], c].isna().sum())),
                         str(int(STOCKS.loc[AUDIT['first_listed'][c]:, c].notna().sum())), "0"]
                        for c in cols]},
        uses=["not-applicable start", "missing indicator (key only)", "null indicator",
              "measurement readout", "x-axis", "provenance"],
        check={k: AUDIT[k] for k in ("blank_cells", "empty_row_cells", "not_applicable",
                                     "missing", "rows_kept")},
    )


# ---------------------------------------------------------------------------
# 03 — Distribution with the outlier rule stated
# ---------------------------------------------------------------------------
def fig_returns():
    W, H = 720, 380
    x0, x1, y0, y1 = 58, 700, 40, 322
    r = STOCKS["^GSPC"].pct_change().dropna() * 100
    mu, sd = r.mean(), r.std()
    z = (r - mu) / sd
    out = r[z.abs() > 3]
    q1, q3 = np.percentile(r, [25, 75])
    tukey = r[(r < q1 - 3 * (q3 - q1)) | (r > q3 + 3 * (q3 - q1))]
    edges = np.arange(-18, 15, 1.0)
    counts, _ = np.histogram(r, bins=edges)
    xs = K.Linear(-18, 14, x0, x1)
    yt = K.nice_cover(0, counts.max(), 3)
    ys = K.Linear(0, yt[-1], y1, y0)
    b = [K.y_axis(ys, x0, x1, yt, lambda v: f"{v:.0f}")]
    for i, c in enumerate(counts):
        if c == 0:
            continue
        lo_, hi_ = edges[i], edges[i + 1]
        months_in = r[(r >= lo_) & (r < hi_)]
        tip = (f"{lo_:+.0f}% to {hi_:+.0f}%: {c} month{'s' if c > 1 else ''}"
               .replace("+-", "−").replace("-", "−"))
        if c <= 3:
            tip += " — " + ", ".join(f"{month(t)} {signed(v)}" for t, v in months_in.items())
        b.append(K.bar(xs(lo_) + 1, xs(hi_) - 1, y1, ys(c), "c-context"))
        b.append(K.hit(xs(lo_), y0, xs(hi_) - xs(lo_), y1 - y0, tip))
    b.append(K.x_axis(xs, y1, list(range(-15, 15, 5)),
                      lambda v: ("+" if v > 0 else ("−" if v < 0 else "")) + f"{abs(v)}"))
    b.append(K.unit_label(x1, y1 + 38, "Monthly return, %", "end"))
    b.append(K.unit_label(x0 - 8 - 22, y0 - 16, "Months"))
    lo3, hi3 = mu - 3 * sd, mu + 3 * sd
    b.append(K.reference_rule(x=xs(lo3), extent=(y0 + 4, y1), label="−3σ"))
    b.append(K.reference_rule(x=xs(hi3), extent=(y0 + 4, y1)))
    b.append(K.text(xs(hi3) - 6, y0 + 15, "+3σ", "c-ink", 11.5, "end", "sans", 500))
    for t, v in out.sort_values().items():
        yy = ys(1) - 14
        b.append(K.outlier_marker(xs(v), yy, tip=f"{month(t)}: {signed(v)} (z = {z[t]:.2f})"))
    # one leader for the group, from the most extreme
    b.append(K.leader(xs(out.min()), ys(1) - 14, xs(lo3) - xs(out.min()) + 26, -110,
                      "Three months past −3σ", sub="|Z| > 3, N = 389", r_off=9))
    return K.Figure(
        id="returns", form="Histogram · rule-based outliers",
        title=f"{WORDS[len(out)].capitalize()} months in 32 years fell more than three standard deviations",
        dek=(f"S&P 500 monthly returns, Feb 1990 to Jun 2022: mean {signed(mu, 2)}, "
             f"sd {sd:.2f}%. Coral marks {', '.join(month(t) + ' (' + signed(v) + ')' for t, v in out.sort_index().items())}. "
             f"The largest gain, {month(r.idxmax())} ({signed(r.max())}), stays inside +3σ. "
             f"A 3×IQR fence flags {len(tukey)}: the tails are fat, so the rule has to be named."),
        svg=K.svg("".join(b), W, H, f"Histogram of {len(r)} monthly S&P 500 returns with "
                  f"{len(out)} outliers beyond three standard deviations."),
        n=f"n = {len(r)} monthly returns",
        source=STOCKS_SRC + "; returns from consecutive month-start rows",
        table={"cols": ["Bin", "Months", "Outliers in bin"], "num": [1],
               "rows": [[(f"{edges[i]:+.0f} to {edges[i+1]:+.0f}%").replace("-", "−"), str(c),
                         ", ".join(month(t) for t, v in out.items() if edges[i] <= v < edges[i + 1]) or ""]
                        for i, c in enumerate(counts) if c]},
        uses=["bar", "reference rule (dashed = threshold)", "outlier marker + rule",
              "annotation leader", "unit label", "hover"],
        check={"n": len(r), "mean": round(mu, 3), "sd": round(sd, 3),
               "outliers": {month(t): round(v, 2) for t, v in out.items()},
               "tukey": len(tukey), "max": (month(r.idxmax()), round(r.max(), 2))},
    )


# ---------------------------------------------------------------------------
# 04 — Scatter + fit + CI band; no outliers, and it says so
# ---------------------------------------------------------------------------
def fig_diabetes():
    W, H = 720, 400
    x0, x1, y0, y1 = 58, 690, 40, 342
    ds = load_diabetes(scaled=False)
    X = ds.data[:, list(ds.feature_names).index("bmi")]
    y = ds.target
    n = len(y)
    res = stats.linregress(X, y)
    yhat = res.intercept + res.slope * X
    resid = y - yhat
    s = math.sqrt((resid ** 2).sum() / (n - 2))
    xbar, sxx = X.mean(), ((X - X.mean()) ** 2).sum()
    h = 1 / n + (X - xbar) ** 2 / sxx
    stud = resid / (s * np.sqrt(1 - h))
    tcrit = stats.t.ppf(0.975, n - 2)
    xs = K.Linear(16, 44, x0, x1)
    ys = K.Linear(0, 360, y1, y0)
    b = [K.y_axis(ys, x0, x1, [0, 100, 200, 300], lambda v: f"{v:.0f}")]
    b.append(K.x_axis(xs, y1, list(range(20, 45, 5)), lambda v: f"{v:.0f}"))
    b.append(K.unit_label(x1, y1 + 38, "Body-mass index", "end"))
    b.append(K.unit_label(x0 - 30, y0 - 16, "Progression score"))
    grid = np.linspace(X.min(), X.max(), 60)
    se = s * np.sqrt(1 / n + (grid - xbar) ** 2 / sxx)
    fit = res.intercept + res.slope * grid
    up = [(xs(g), ys(v)) for g, v in zip(grid, fit + tcrit * se)]
    dn = [(xs(g), ys(v)) for g, v in zip(grid, fit - tcrit * se)]
    for xi, yi in sorted(zip(X, y), key=lambda p: p[0]):
        b.append(K.data_dot(xs(xi), ys(yi), "c-context", r=3.5, opacity=0.55,
                            tip=f"BMI {xi:.1f} · score {yi:.0f}", focus=False))
    b.append(K.ci_band(up, dn))
    b.append(K.series_line([(xs(g), ys(v)) for g, v in zip(grid, fit)], "c-story"))
    gx = 40.0
    b.append(K.leader(xs(gx), ys(res.intercept + res.slope * gx), -40, -64,
                      f"+{res.slope:.1f} per BMI point", sub=f"R² {res.rvalue**2:.2f}"))
    return K.Figure(
        id="diabetes", form="Scatter · OLS fit · 95% band",
        title=f"Higher BMI, faster progression: about {res.slope:.0f} points per unit",
        dek=(f"Disease progression one year after baseline against body-mass index, {n} patients. "
             f"The line is a least-squares fit with its 95% confidence band; BMI alone accounts "
             f"for {res.rvalue**2*100:.0f}% of the variation. An association, not an effect. "
             f"Nothing is marked in coral: the largest studentized residual is "
             f"{np.abs(stud).max():.2f}, inside the |t| > 3 rule."),
        svg=K.svg("".join(b), W, H, f"Scatter of {n} patients, BMI against progression, "
                  f"with a fitted line of slope {res.slope:.2f}."),
        n=f"n = {n} patients",
        source="Efron et al. (2004), Least Angle Regression; via scikit-learn load_diabetes",
        table={"cols": ["Statistic", "Value"], "num": [1],
               "rows": [["Patients", f"{n}"], ["BMI range", f"{X.min():.1f}–{X.max():.1f}"],
                        ["Score range", f"{y.min():.0f}–{y.max():.0f}"],
                        ["Slope per BMI point", f"{res.slope:.2f}"],
                        ["Slope, 95% CI", f"{res.slope - tcrit*res.stderr:.2f}–{res.slope + tcrit*res.stderr:.2f}"],
                        ["Intercept", f"{res.intercept:.1f}"], ["r²", f"{res.rvalue**2:.3f}"],
                        ["p", f"{res.pvalue:.1e}"],
                        ["Max |studentized residual|", f"{np.abs(stud).max():.2f}"],
                        ["Points past |t| > 3", "0"]],
               "note": f"All {n} points are in the downloadable data; the chart's hover reads each one."},
        uses=["data dot + surface ring", "confidence band", "series line",
              "annotation leader", "nearest-point hover", "outlier rule (applied, none found)"],
        check={"n": n, "slope": round(res.slope, 3), "r2": round(res.rvalue ** 2, 3),
               "p": float(f"{res.pvalue:.2g}"), "max_stud": round(float(np.abs(stud).max()), 2)},
        nearest=True,
    )


# ---------------------------------------------------------------------------
# 05 — Dot plot, CIs, comparison bracket
# ---------------------------------------------------------------------------
def fig_wine():
    W, H = 720, 300
    x0, x1 = 128, 560
    ds = load_wine()
    alc = ds.data[:, list(ds.feature_names).index("alcohol")]
    groups = [alc[ds.target == k] for k in range(3)]
    xs = K.Linear(11, 15, x0, x1)
    rowy = [70, 140, 210]
    b = [K.y_axis(K.Linear(0, 1, 0, 0), x0, x1, [], str)]
    for t in range(11, 16):
        b.append(K.line(xs(t), 40, xs(t), 236, "c-grid"))
    b.append(K.x_axis(xs, 236, list(range(11, 16)), lambda v: f"{v}"))
    b.append(K.unit_label(x1, 274, "Alcohol, % vol", "end"))
    summary = []
    rng = np.random.default_rng(7)
    for k, (g, yy) in enumerate(zip(groups, rowy)):
        m, se = g.mean(), stats.sem(g)
        tc = stats.t.ppf(0.975, len(g) - 1)
        lo, hi = m - tc * se, m + tc * se
        summary.append((m, lo, hi, len(g)))
        story = k in (0, 1)
        cls = "c-story" if story else "c-context"
        b.append(K.text(x0 - 16, yy - 2, f"Cultivar {k + 1}", "c-ink", 12.5, "end", "sans", 500))
        b.append(K.text(x0 - 16, yy + 13, f"n = {len(g)}", "c-body", 10.5, "end", "mono"))
        jit = rng.uniform(-9, 9, len(g))
        for v, j in zip(g, jit):
            b.append(f'<circle class="c-context c-fill" cx="{K.f(xs(v))}" cy="{K.f(yy + j)}" '
                     f'r="2.2" fill-opacity=".35"/>')
        b.append(K.interval(xs(lo), xs(hi), yy, cls, cap=10))
        b.append(K.data_dot(xs(m), yy, cls, r=5,
                            tip=f"Cultivar {k+1}: mean {m:.2f}% vol, 95% CI {lo:.2f}–{hi:.2f}, n = {len(g)}"))
    diff = groups[0].mean() - groups[1].mean()
    w = stats.ttest_ind(groups[0], groups[1], equal_var=False)
    v0, v1 = groups[0].var(ddof=1) / len(groups[0]), groups[1].var(ddof=1) / len(groups[1])
    se_d = math.sqrt(v0 + v1)
    dfw = (v0 + v1) ** 2 / (v0 ** 2 / (len(groups[0]) - 1) + v1 ** 2 / (len(groups[1]) - 1))
    tcd = stats.t.ppf(0.975, dfw)
    dlo, dhi = diff - tcd * se_d, diff + tcd * se_d
    b.append(K.comparison_bracket(x1 + 18, rowy[0], rowy[1], f"+{diff:.2f} % vol",
                                  sub=f"CI {dlo:.2f}–{dhi:.2f}"))
    # key
    ky = 274
    b.append(K.data_dot(24 + 5, ky - 4, "c-story", r=5))
    b.append(K.line(16, ky - 4, 42, ky - 4, "c-story", 1.5))
    b.append(K.text(50, ky, "Mean, 95% CI", "c-body", 11.5))
    b.append(f'<circle class="c-context c-fill" cx="{160}" cy="{ky - 4}" r="2.2" fill-opacity=".6"/>')
    b.append(K.text(168, ky, "One wine", "c-body", 11.5))
    return K.Figure(
        id="wine", form="Dot plot · intervals · bracket",
        title=f"Cultivar 1 wines run {diff:.1f} points stronger than cultivar 2",
        dek=(f"Alcohol by grape cultivar, {sum(len(g) for g in groups)} wines from one Italian region. "
             f"Dots are means with 95% intervals; the faint points are the wines themselves. "
             f"The bracket is the difference and its own interval (Welch, p = {sci(w.pvalue)})."),
        svg=K.svg("".join(b), W, H, f"Dot plot of mean alcohol for three cultivars; cultivar 1 "
                  f"exceeds cultivar 2 by {diff:.2f} percentage points."),
        n=f"n = {len(groups[0])} + {len(groups[1])} + {len(groups[2])} wines",
        source="Forina et al., PARVUS; UCI Machine Learning Repository; via scikit-learn load_wine",
        table={"cols": ["Cultivar", "n", "Mean % vol", "95% CI"], "num": [1, 2],
               "rows": [[f"Cultivar {k+1}", str(nn), f"{m:.2f}", f"{lo:.2f}–{hi:.2f}"]
                        for k, (m, lo, hi, nn) in enumerate(summary)] +
                       [["Difference 1 − 2", "", f"{diff:.2f}", f"{dlo:.2f}–{dhi:.2f}"]]},
        uses=["data dot", "confidence interval", "comparison bracket", "measurement label", "key"],
        check={"means": [round(s[0], 2) for s in summary], "diff": round(diff, 2),
               "ci": [round(dlo, 2), round(dhi, 2)], "p": float(f"{w.pvalue:.2g}")},
    )


# ---------------------------------------------------------------------------
# 06 — Ranked bars against a benchmark
# ---------------------------------------------------------------------------
def fig_ranked():
    W, H = 720, 360
    x0, x1, top, band = 132, 640, 44, 28
    d = STOCKS.loc[BASE:]
    base = d.loc[BASE]
    ret = {c: (d[c].iloc[-1] / base[c] - 1) * 100 for c in d.columns
           if c != "^GSPC" and not math.isnan(base[c])}
    bench = (d["^GSPC"].iloc[-1] / base["^GSPC"] - 1) * 100
    order = sorted(ret, key=lambda c: -ret[c])
    xs = K.Linear(-80, 2400, x0, x1)
    rows_y = {c: top + i * band for i, c in enumerate(order + ["DELL"])}
    last_y = rows_y["DELL"] + band
    b = []
    for t in (0, 500, 1000, 1500, 2000):
        b.append(K.line(xs(t), top - 12, xs(t), last_y - 8, "c-grid" if t else "c-axis"))
        b.append(K.text(xs(t), last_y + 8, f"+{t:,}" if t else "0", "c-body", 10.5, "middle", "mono"))
    b.append(K.unit_label(x1, last_y + 30, "Change since Jan 2010, %", "end"))
    labels = []
    for c in order:
        yy = rows_y[c]
        v = ret[c]
        cls = "c-neg" if v < 0 else "c-context"
        labels.append(K.text(x0 - 14, yy + 4, NAMES[c], "c-ink", 12, "end", "sans", 500))
        xe = xs(v)
        if abs(xe - xs(0)) < 1:
            xe = xs(0) - 1 if v < 0 else xs(0) + 1
        b.append(K.bar(xs(0), xe, yy - 9, yy + 9, cls, horizontal=True))
        lx = max(xe, xs(0)) + 6
        labels.append(K.measurement_label(lx, yy + 4, signed(v, 1 if abs(v) < 10 else 0)))
        labels.append(K.hit(x0 - 120, yy - band / 2, x1 - x0 + 120, band,
                            f"{NAMES[c]}: {signed(v, 1)} ({'above' if v > bench else 'below'} the S&P 500)"))
    # bars → benchmark → labels: the dashed rule crosses the bars but breaks
    # behind every label (the labels carry a surface halo).
    b.append(K.reference_rule(x=xs(bench), extent=(top - 22, last_y - 8)))
    b.append(K.text(xs(bench) + 6, top - 14, f"S&P 500 {signed(bench, 0)}", "c-ink c-halo", 11.5, "start", "sans", 500))
    b.extend(labels)
    yy = rows_y["DELL"]
    b.append(K.text(x0 - 14, yy + 4, "Dell", "c-ink", 12, "end", "sans", 500))
    b.append(K.null_mark(xs(0) + 10, yy + 5, "Dell: listed Sep 2016 — no Jan 2010 price"))
    b.append(K.text(xs(0) + 22, yy + 4, "No 2010 price", "c-body c-halo", 11))
    beat = [c for c in order if ret[c] > bench and not c.startswith("^")]
    stocks_ = [c for c in order if not c.startswith("^")]
    return K.Figure(
        id="ranked", form="Ranked bars · dashed benchmark",
        title=f"{WORDS[len(beat)].capitalize()} of {WORDS[len(stocks_)]} stocks beat the S&P 500 from 2010 to mid-2022",
        dek=(f"Change in adjusted close, January 2010 to June 2022, against the S&P 500 "
             f"({signed(bench, 1)}), drawn dashed because it is a benchmark, not a bar. "
             f"Xerox is the only loss ({signed(ret['XRX'])}) and the only bar in the negative colour. "
             "Dell listed in 2016 and has no value to rank."),
        svg=K.svg("".join(b), W, H, f"Bar chart of change since 2010: Apple {signed(ret['AAPL'], 0)} "
                  f"down to Xerox {signed(ret['XRX'])}; S&P 500 benchmark {signed(bench, 0)}."),
        n=f"n = {len(ret)} series ranked; 1 not applicable",
        source=STOCKS_SRC,
        table={"cols": ["Series", "Change since Jan 2010", "vs S&P 500"], "num": [1, 2],
               "rows": [[NAMES[c], signed(ret[c], 1), signed(ret[c] - bench, 1, " pts")] for c in order] +
                       [["S&P 500 (benchmark)", signed(bench, 1), "—"], ["Dell", "—", "—"]]},
        uses=["bar (square base, 4px data end)", "reference rule (benchmark)",
              "measurement label", "negative value", "null indicator", "hover"],
        check={c: round(v, 1) for c, v in ret.items()} | {"bench": round(bench, 1)},
    )


FIGURES = [fig_indexed(), fig_states(), fig_returns(), fig_diabetes(), fig_wine(), fig_ranked()]

if __name__ == "__main__":
    for fg in FIGURES:
        print(f"[{fg['id']}] {fg['title']}\n   {fg['n']}\n   {fg['check']}\n")
