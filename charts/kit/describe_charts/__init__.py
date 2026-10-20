"""
describe_charts — the .describe( data-visualization kit.

The one line that brands an existing analysis script or notebook:

    import describe_charts; describe_charts.use()

Every matplotlib, pandas .plot, seaborn and Plotly chart made after it takes
the brand palette and type. The helpers in describe_charts.mpl and
describe_charts.plotly_theme add the rules a theme cannot express, and
describe_charts.report assembles charts into a branded HTML / PDF report.
"""

from __future__ import annotations

from .tokens import palette  # noqa: F401

__version__ = "0.1.0"


def use(mode: str = "light", matplotlib: bool = True, plotly: bool = True) -> dict:
    """Apply the brand look to whichever chart libraries are installed.
    Returns what was applied, e.g. {'matplotlib': ['Fraunces', ...], 'plotly': 'describe'}."""
    done = {}
    if matplotlib:
        try:
            from . import mpl
            done["matplotlib"] = mpl.apply(mode)
        except ImportError:
            pass
    if plotly:
        try:
            from . import plotly_theme
            plotly_theme.apply(mode)
            done["plotly"] = "describe" if mode == "light" else "describe_dark"
        except ImportError:
            pass
    return done
