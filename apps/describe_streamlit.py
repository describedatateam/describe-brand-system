"""
describe_streamlit.py — the .describe( look for Streamlit apps.

    import streamlit as st
    import describe_streamlit as S

    S.use()                                   # tokens, ui.css, app.css, fonts, Plotly template
    S.header("Store health", "Sep to Nov brought in 38% of the year.", dek="...")
    S.kpis([S.kpi("Net revenue", "£9.33", unit="M", note="..."), ...])
    st.plotly_chart(fig, theme=None)          # theme=None keeps the describe template
    S.source("n = 497,814 sale lines", "Online Retail dataset (UCI)")

Streamlit draws its own chrome (sidebar, widgets) from .streamlit/config.toml;
`python3 apps/build.py` writes that file from the tokens, so it never needs
editing by hand. Everything inside the page reads the same stylesheets as the
static dashboard in apps/out/.
"""

from __future__ import annotations

import html
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "charts", "kit"))

from describe_charts.tokens import TOKENS  # noqa: E402

FONTS = ("https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300;9..144,400"
         "&family=Readex+Pro:wght@300;400;500&family=IBM+Plex+Mono:wght@400;500&display=swap")

# Streamlit's own containers, quietened so the page reads as one plate
CHROME = """
.stApp{background:var(--ground)}
.stApp,.stApp p,.stApp li{font-family:var(--font-sans);font-weight:var(--w-body);color:var(--ink)}
[data-testid="stHeader"]{background:transparent}
.block-container{padding-top:2rem;max-width:1440px}
[data-testid="stPlotlyChart"]{border:var(--hair) solid var(--rule);background:var(--panel)}
"""


def _css(rel: str) -> str:
    return open(os.path.join(ROOT, rel), encoding="utf-8").read()


def _tokens_css(mode: str) -> str:
    """tokens.css pinned to one mode. Streamlit picks the mode (its settings
    menu, or the viewer's system), so the page must not switch on its own."""
    css = _css("tokens/dist/tokens.css")
    css = re.sub(r"@media \(prefers-color-scheme: dark\)\{.*?\n\}\n", "", css, flags=re.S)
    if mode == "dark":
        css = css.replace(':root[data-theme="dark"], [data-theme="dark"]{', ":root{")
    return css


def mode() -> str:
    """The mode Streamlit is showing: 'light' or 'dark'."""
    import streamlit as st
    return "dark" if (st.context.theme.type or "light") == "dark" else "light"


def use(mode_: str | None = None):
    """Inject the tokens, the UI layer and the app shell in the mode
    Streamlit is showing, and make the describe Plotly template the default.
    Call once, first. Returns the mode."""
    import streamlit as st
    from describe_charts import plotly_theme as P

    m = mode_ or mode()
    P.apply(m)
    css = "\n".join([_tokens_css(m), _css("ui/ui.css"), _css("apps/app.css")])
    st.html(f'<link rel="stylesheet" href="{FONTS}"><style>{css}{CHROME}</style>')
    return m


def header(label: str, title: str, dek: str = ""):
    """The title is the finding, never the dataset's name."""
    import streamlit as st
    st.html(f'<header class="app__head"><div><span class="app__eyebrow">{html.escape(label)}</span>'
            f'<h1 class="app__title" style="margin:8px 0 10px">{html.escape(title)}</h1>'
            + (f'<p class="app__dek" style="margin:0">{html.escape(dek)}</p>' if dek else "")
            + "</div></header>")


def kpi(label: str, value: str, unit: str = "", note: str = "", rule: str | None = None) -> str:
    """One tile. `note` may carry a <span class="pos|neg"> delta. Pass `rule`
    only for a count of outliers: the value gets the coral marker and the
    rule is written into the note, so the marker never appears without it."""
    v = f'<span class="d-outlier">{value}</span>' if rule else value
    u = f"<small>{html.escape(unit)}</small>" if unit else ""
    n = html.escape(rule) + ("; " + note if note else "") if rule else note
    return (f'<div class="kpi"><span class="kpi__label">{html.escape(label)}</span>'
            f'<span class="kpi__value">{v}{u}</span><span class="kpi__note">{n}</span></div>')


def kpis(tiles: list[str]):
    import streamlit as st
    st.html(f'<section class="kpis" aria-label="Key figures">{"".join(tiles)}</section>')


def source(n: str, source: str, computed: str = ""):
    """The provenance line every page ends on."""
    import streamlit as st
    if not n or not source:
        raise ValueError("Every page states n and its source.")
    tail = f" Computed {html.escape(computed)}." if computed else ""
    st.html(f'<footer class="provenance"><span><span class="n">{html.escape(n)}</span> · '
            f'Source: {html.escape(source)}.{tail}</span></footer>')


def config_toml() -> str:
    """Streamlit's theme, from the tokens: one section per mode."""
    def section(mode):
        t = TOKENS[mode]
        return "\n".join([
            f"[theme.{mode}]",
            f'primaryColor = "{t["story"]}"',
            f'backgroundColor = "{t["ground"]}"',
            f'secondaryBackgroundColor = "{t["panel"]}"',
            f'textColor = "{t["ink"]}"',
            f'borderColor = "{t["rule"]}"',
            ""])
    return ("# GENERATED by apps/build.py from tokens/dist/tokens.json. Do not edit.\n"
            "[theme]\n"
            'font = "Readex Pro, system-ui, sans-serif"\n'
            'headingFont = "Fraunces, Georgia, serif"\n'
            'codeFont = "IBM Plex Mono, ui-monospace, monospace"\n'
            "baseRadius = \"2px\"\n\n"
            + section("light") + "\n" + section("dark"))
