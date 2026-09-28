"""
mpl_describe.py — the .describe( furniture for matplotlib, for analysis work
that never becomes a web page (notebooks, PDFs, client decks).

    from mpl_describe import use, story, context, outlier, benchmark, finish

The web charts (chartkit.py) remain the reference. This module reproduces
the rules, not every pixel:

    * one story series in blue, everything else context grey
    * coral only through outlier(), which requires the rule that flagged it
    * dashed only through benchmark()
    * finish() refuses to save a chart without n and a source
"""

from __future__ import annotations

import os
from datetime import date

import matplotlib as mpl
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
C = {"ink": "#092052", "body": "#5A6B85", "dim": "#63738D", "rule": "#D8E1EF",
     "story": "#0F58E5", "context": "#64748B", "mark": "#E5484D",
     "pos": "#0F7B3D", "neg": "#8C1D1D", "panel": "#FFFFFF"}
MONO = ["IBM Plex Mono", "DejaVu Sans Mono"]


def use():
    """Apply the style. The brand faces are used when installed; otherwise the
    DejaVu fallbacks — quietly, since that is the normal case on a server."""
    import logging
    logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
    plt.style.use(os.path.join(HERE, "describe.mplstyle"))


def story(ax, x, y, **kw):
    """The one series the finding is about. Call it once per axes."""
    if getattr(ax, "_dsc_story", False):
        raise ValueError("One story series per chart. Use context() for the rest, "
                         "or small multiples if each series needs an identity.")
    ax._dsc_story = True
    return ax.plot(x, y, color=C["story"], lw=2, zorder=3, **kw)


def context(ax, x, y, **kw):
    return ax.plot(x, y, color=C["context"], lw=1.1, zorder=2, **kw)


def outlier(ax, x, y, rule, label=None, dx=12, dy=12):
    """Coral ring + dot. `rule` is required: an outlier states its test."""
    if not rule:
        raise ValueError("outlier() needs the rule that flagged the point, e.g. '|z| > 3'.")
    ax.plot([x], [y], "o", ms=11, mfc="none", mec=C["mark"], mew=1.3, zorder=5)
    ax.plot([x], [y], "o", ms=4.5, mfc=C["mark"], mec="none", zorder=6)
    if label:
        ax.annotate(f"{label}\n{rule}", (x, y), xytext=(dx, dy), textcoords="offset points",
                    fontsize=8.5, color=C["ink"],  # text is ink, never coral
                    bbox=dict(fc=C["panel"], ec="none", pad=1.5),  # halo over rules
                    arrowprops=dict(arrowstyle="-", color=C["body"], lw=0.75,
                                    connectionstyle="angle,angleA=0,angleB=60"))


def benchmark(ax, value, label, axis="y"):
    """Dashed = threshold, benchmark or projection. The only dashed line."""
    kw = dict(color=C["ink"], lw=1, ls=(0, (4, 4)), zorder=4)
    if axis == "y":
        ax.axhline(value, **kw)
        ax.annotate(label, (1, value), xycoords=("axes fraction", "data"), xytext=(0, 4),
                    textcoords="offset points", ha="right", fontsize=8.5, color=C["ink"])
    else:
        ax.axvline(value, **kw)
        ax.annotate(label, (value, 1), xycoords=("data", "axes fraction"), xytext=(4, -10),
                    textcoords="offset points", fontsize=8.5, color=C["ink"])


def finish(fig, ax, title, n, source, dek=None, path=None, computed=None):
    """Title states the finding; the provenance line carries n, source, date.
    No n, no chart."""
    if not n or not source:
        raise ValueError("Every chart states n and its source.")
    computed = computed or date.today().strftime("%-d %b %Y")
    fig.subplots_adjust(top=0.80 if dek else 0.88)
    fig.text(0.0, 0.985, title, fontsize=15, color=C["ink"], family="serif", va="top")
    if dek:
        fig.text(0.0, 0.905, dek, fontsize=9, color=C["body"], va="top", linespacing=1.4)
    fig.text(0.0, -0.02, n, fontsize=8, color=C["ink"], family=MONO, va="top")
    fig.text(0.0, -0.055, f"Source: {source}. Computed {computed}.", fontsize=8,
             color=C["body"], va="top")
    for t in ax.get_xticklabels() + ax.get_yticklabels():
        t.set_fontfamily(MONO)
    if path:
        fig.savefig(path)
    return fig
