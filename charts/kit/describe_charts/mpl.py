"""
mpl.py — the .describe( look for matplotlib (and so pandas .plot and seaborn).

    from describe_charts import mpl as D
    D.apply()                 # or D.apply("dark")
    fig, ax = plt.subplots()
    D.story(ax, x, y, label="Apple")
    D.context(ax, x, other)
    D.finish(fig, ax, "Apple tripled the index", n="n = 150 months", source="Yahoo Finance")

apply() alone restyles every chart an existing script makes. The helpers add
what a style cannot express, and enforce the rules in charts/CHARTS.md §8:

    * story() once per axes: one blue series, everything else context grey
    * coral only through outlier(), which requires the rule that flagged it
    * dashed only through benchmark()
    * finish() refuses a chart without n and a source
"""

from __future__ import annotations

import logging
import os
from datetime import date

from .fonts import register_matplotlib
from .tokens import FONTS, HERE, SIZE, STROKE, palette

STYLE_DIR = os.path.join(HERE, "styles")
_mode = "light"


def C() -> dict:
    """The palette of the mode last applied."""
    return palette(_mode)


def rc(mode: str = "light") -> dict:
    """rcParams for a mode. Built from tokens.json, so a palette change is a
    one-file change; the .mplstyle files in styles/ are generated from this."""
    p = palette(mode)
    # Series cycle: the categorical palette, in its fixed order (TOKENS.md),
    # so existing multi-series code gets distinguishable, validated colours.
    # A chart with a finding should instead use story() and context().
    cycle = p["cat"]
    return {
        "font.family": "sans-serif",
        "font.sans-serif": FONTS["sans"],
        "font.serif": FONTS["serif"],
        "font.monospace": FONTS["mono"],
        "font.size": SIZE["label"],
        "text.color": p["ink"],
        "figure.facecolor": p["panel"],
        "figure.edgecolor": p["panel"],
        "figure.dpi": 110,
        "figure.figsize": (7.2, 4.2),
        "savefig.dpi": 200,
        "savefig.facecolor": p["panel"],
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.25,
        "axes.facecolor": p["panel"],
        "axes.edgecolor": p["body"],
        "axes.linewidth": STROKE["hair"],
        "axes.labelcolor": p["dim"],
        "axes.labelsize": SIZE["unit"],
        "axes.titlesize": SIZE["title"] - 2,
        "axes.titleweight": "normal",
        "axes.titlelocation": "left",
        "axes.titlecolor": p["ink"],
        "axes.titlepad": 10,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": False,
        "axes.grid": True,
        "axes.grid.axis": "y",
        "axes.axisbelow": True,
        "axes.prop_cycle": __import__("cycler").cycler(color=cycle),
        "grid.color": p["rule"],
        "grid.linewidth": STROKE["hair"],
        "grid.linestyle": "-",
        "xtick.color": p["body"],
        "ytick.color": p["body"],
        "xtick.labelcolor": p["body"],
        "ytick.labelcolor": p["body"],
        "xtick.labelsize": SIZE["tick"],
        "ytick.labelsize": SIZE["tick"],
        "xtick.major.size": 4,
        "xtick.major.width": STROKE["hair"],
        "xtick.minor.size": 2,
        "ytick.major.size": 0,
        "ytick.minor.size": 0,
        "lines.linewidth": STROKE["data"],
        "lines.solid_capstyle": "round",
        "lines.solid_joinstyle": "round",
        "lines.markersize": STROKE["dot"] + 1,
        "patch.linewidth": 0,
        "patch.facecolor": p["story"],
        "hist.bins": "auto",
        "legend.frameon": False,
        "legend.fontsize": SIZE["label"] - 0.5,
        "legend.handlelength": 1.4,
        "legend.labelcolor": p["ink"],
        "image.cmap": f"describe_seq_{mode}",
        "boxplot.boxprops.color": p["body"],
        "boxplot.whiskerprops.color": p["body"],
        "boxplot.capprops.color": p["body"],
        "boxplot.medianprops.color": p["story"],
        "boxplot.flierprops.markeredgecolor": p["context"],
        "scatter.edgecolors": p["panel"],
        "svg.fonttype": "path",
        "pdf.fonttype": 42,
    }


def _register_cmaps():
    """describe_seq_* (the blue scale, for magnitude) and describe_div_*
    (brass below, blue above, grey at zero: polarity, not good/bad)."""
    import matplotlib as mpl
    from matplotlib.colors import LinearSegmentedColormap
    for mode in ("light", "dark"):
        p = palette(mode)
        for name, stops in ((f"describe_seq_{mode}", p["seq"]), (f"describe_div_{mode}", p["div"])):
            if name not in mpl.colormaps:
                mpl.colormaps.register(LinearSegmentedColormap.from_list(name, stops))


def apply(mode: str = "light") -> list[str]:
    """Restyle matplotlib globally. Returns the brand faces found (empty means
    DejaVu fallbacks; run `python -m describe_charts fonts`)."""
    global _mode
    import matplotlib as mpl
    logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
    found = register_matplotlib()
    _register_cmaps()
    _mode = mode
    mpl.rcParams.update(rc(mode))
    return found


def write_styles(dest: str = STYLE_DIR) -> list[str]:
    """Regenerate styles/describe-{light,dark}.mplstyle from tokens.json, for
    anyone who would rather `plt.style.use(path)` than import the kit."""
    os.makedirs(dest, exist_ok=True)
    out = []
    for mode in ("light", "dark"):
        lines = [f"# describe-{mode}.mplstyle — GENERATED from describe_charts/tokens.json by",
                 "# describe_charts.mpl.write_styles(). Edit tokens.json, not this file.",
                 "# The sequential colormap needs the kit (import describe_charts) to be registered.", ""]
        for k, v in rc(mode).items():
            if k == "image.cmap":
                continue
            if k == "axes.prop_cycle":
                v = "cycler('color', [" + ", ".join(f"'{c['color'].lstrip('#')}'" for c in v) + "])"
            elif isinstance(v, (list, tuple)):
                v = ", ".join(str(x) for x in v)
            elif isinstance(v, str) and v.startswith("#"):
                v = v.lstrip("#")
            lines.append(f"{k:<34}: {v}")
        path = os.path.join(dest, f"describe-{mode}.mplstyle")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
        out.append(path)
    return out


# ---------------------------------------------------------------------------
# Helpers — the parts a style file cannot express
# ---------------------------------------------------------------------------
def story(ax, x, y, **kw):
    """The one series the finding is about. Call it once per axes."""
    if getattr(ax, "_dsc_story", False):
        raise ValueError("One story series per chart. Use context() for the rest, "
                         "or small multiples if each series needs an identity.")
    ax._dsc_story = True
    return ax.plot(x, y, color=C()["story"], lw=STROKE["data"], zorder=3, **kw)


def context(ax, x, y, **kw):
    return ax.plot(x, y, color=C()["context"], lw=STROKE["context"], zorder=2, **kw)


def label_end(ax, x, y, text, story=False, dx=6):
    """Direct label at a line's end: ink text, never a data colour (rule 9)."""
    ax.annotate(text, (x, y), xytext=(dx, 0), textcoords="offset points", va="center",
                fontsize=SIZE["label"], color=C()["ink"] if story else C()["body"],
                family=["Readex Pro Medium"] + FONTS["sans"] if story else FONTS["sans"],
                annotation_clip=False)


def outlier(ax, x, y, rule, label=None, dx=12, dy=12):
    """Coral ring + dot. `rule` is required: an outlier states its test."""
    if not rule:
        raise ValueError("outlier() needs the rule that flagged the point, e.g. '|z| > 3'.")
    p = C()
    ax.plot([x], [y], "o", ms=11, mfc="none", mec=p["mark"], mew=1.3, zorder=5)
    ax.plot([x], [y], "o", ms=4.5, mfc=p["mark"], mec="none", zorder=6)
    if label:
        ax.annotate(f"{label}\n{rule}", (x, y), xytext=(dx, dy), textcoords="offset points",
                    fontsize=SIZE["label"] - 0.5, color=p["ink"],
                    bbox=dict(fc=p["panel"], ec="none", pad=1.5),
                    arrowprops=dict(arrowstyle="-", color=p["body"], lw=STROKE["hair"],
                                    connectionstyle="angle,angleA=0,angleB=60"))


def benchmark(ax, value, label, axis="y"):
    """Dashed = threshold, benchmark or projection. The only dashed line."""
    p = C()
    kw = dict(color=p["ink"], lw=STROKE["rule"], ls=(0, (4, 4)), zorder=4)
    box = dict(fc=p["panel"], ec="none", pad=1.2)
    if axis == "y":
        ax.axhline(value, **kw)
        ax.annotate(label, (1, value), xycoords=("axes fraction", "data"), xytext=(0, 4),
                    textcoords="offset points", ha="right", fontsize=SIZE["label"] - 0.5,
                    color=p["ink"], bbox=box)
    else:
        ax.axvline(value, **kw)
        ax.annotate(label, (value, 1), xycoords=("data", "axes fraction"), xytext=(0, 4),
                    textcoords="offset points", ha="center", va="bottom",
                    fontsize=SIZE["label"] - 0.5, color=p["ink"], bbox=box, annotation_clip=False)


def ranked_bars(ax, labels, values, highlight=None, fmt="{:+.0f}%", meaning=False):
    """Horizontal bars, largest first. `highlight` names the story bar(s);
    the rest are context. meaning=True colours by good/bad (pos/neg) instead,
    for values whose sign is a judgement — never both in one chart (rule 10)."""
    p = C()
    pairs = sorted(zip(labels, values), key=lambda t: t[1])
    hi = set([highlight] if isinstance(highlight, str) else (highlight or []))
    cols = [(p["pos"] if v >= 0 else p["neg"]) if meaning else
            (p["story"] if l in hi else p["context"]) for l, v in pairs]
    ys = range(len(pairs))
    ax.barh(list(ys), [v for _, v in pairs], color=cols, height=0.62)
    ax.set_yticks(list(ys), [l for l, _ in pairs])
    ax.tick_params(axis="y", labelcolor=p["ink"], labelsize=SIZE["label"])
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", visible=True)
    ax.axvline(0, color=p["body"], lw=STROKE["hair"], zorder=2)
    span = max(abs(v) for _, v in pairs) or 1
    for y, (_, v) in zip(ys, pairs):
        ax.annotate(fmt.format(v), (v, y), xytext=(4 if v >= 0 else -4, 0), textcoords="offset points",
                    ha="left" if v >= 0 else "right", va="center", fontsize=SIZE["tick"],
                    family=FONTS["mono"], color=p["ink"])
    lo = min(0, min(v for _, v in pairs))
    ax.set_xlim(lo - (max(0.15 * -lo, 0.06 * span) if lo < 0 else 0),
                max(0, max(v for _, v in pairs)) + 0.14 * span)
    ax.xaxis.set_major_formatter(lambda v, _: f"{v:,.0f}")
    return ax


def units(ax, x=None, y=None):
    """Unit labels: mono, uppercase, ≤ 4 words, at the axis ends (rule 02)."""
    for text, setter, kw in ((x, ax.set_xlabel, dict(loc="right")),
                             (y, ax.set_ylabel, dict(loc="top", rotation=0, labelpad=-8))):
        if text:
            if len(text.split()) > 4:
                raise ValueError("Unit labels are four words or fewer.")
            setter(text.upper(), family=FONTS["mono"], color=C()["dim"], fontsize=SIZE["unit"], **kw)
    if y:
        ax.yaxis.set_label_coords(0, 1.02)
        ax.yaxis.label.set_horizontalalignment("left")


def finish(fig, ax, title, n, source, dek=None, path=None, computed=None):
    """Title states the finding; the provenance line carries n, source, date.
    No n, no chart."""
    if not n or not source:
        raise ValueError("Every chart states n and its source.")
    p = C()
    computed = computed or date.today().strftime("%-d %b %Y")
    axes = ax if isinstance(ax, (list, tuple)) else getattr(ax, "flat", [ax])
    for a in axes:
        for t in a.get_xticklabels() + a.get_yticklabels():
            if not t.get_text() or any(ch.isdigit() for ch in t.get_text()):
                t.set_fontfamily(FONTS["mono"])
    # Header and footer are laid out in inches, so they hold at any figure size.
    W, H = fig.get_size_inches()
    pt = 1 / 72
    dek_lines = dek.count("\n") + 1 if dek else 0
    title_h = SIZE["title"] * 1.25 * pt
    dek_h = dek_lines * SIZE["dek"] * 1.5 * pt
    unit_h = 0.28                       # room for a unit label above the plot
    head = 0.08 + title_h + (0.08 + dek_h if dek else 0) + unit_h
    fig.subplots_adjust(top=1 - head / H)
    y = 1 - 0.08 / H
    fig.text(0.0, y, title, fontsize=SIZE["title"], color=p["ink"], family=FONTS["serif"], va="top")
    if dek:
        fig.text(0.0, y - (title_h + 0.08) / H, dek, fontsize=SIZE["dek"], color=p["body"],
                 va="top", linespacing=1.5)
    fig.text(0.0, -0.32 / H, n, fontsize=SIZE["provenance"], color=p["ink"], family=FONTS["mono"], va="top")
    fig.text(0.0, -0.52 / H, f"Source: {source}. Computed {computed}.", fontsize=SIZE["provenance"],
             color=p["body"], va="top")
    if path:
        fig.savefig(path)
    return fig
