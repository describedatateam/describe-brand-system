"""
plotly_theme.py — the .describe( look as a Plotly template.

    from describe_charts import plotly_theme as P
    P.apply()                       # pio.templates.default = "describe"
    fig = px.line(df, x="year", y="value", color="country")
    P.emphasise(fig, "Jordan")      # the story series blue, the rest context
    P.finish(fig, "Jordan's life expectancy rose 20 years", n="n = 12 years",
             source="Gapminder via plotly.express")

Two templates are registered: "describe" (light) and "describe_dark".
"""

from __future__ import annotations

from datetime import date

import textwrap

from .tokens import FONTS, SIZE, STROKE, palette

PX_PER_PT = 4 / 3


def _fam(key):
    return ", ".join(f"'{f}'" if " " in f else f for f in FONTS[key])


def template(mode: str = "light"):
    import plotly.graph_objects as go
    p = palette(mode)
    sz = lambda k: round(SIZE[k] * PX_PER_PT, 1)
    axis = dict(
        showgrid=True, gridcolor=p["rule"], gridwidth=1, zeroline=False,
        showline=False, ticks="", tickcolor=p["body"],
        tickfont=dict(family=_fam("mono"), size=sz("tick") + 1, color=p["body"]),
        title=dict(font=dict(family=_fam("mono"), size=sz("unit") + 1, color=p["dim"])),
        automargin=True,
    )
    xaxis = dict(axis, showgrid=False, showline=True, linecolor=p["body"], linewidth=1,
                 ticks="outside", ticklen=4)
    seq = [[i / (len(p["seq"]) - 1), c] for i, c in enumerate(p["seq"])]
    div = [[i / (len(p["div"]) - 1), c] for i, c in enumerate(p["div"])]
    t = go.layout.Template()
    t.layout = go.Layout(
        font=dict(family=_fam("sans"), size=sz("label") + 1, color=p["ink"]),
        title=dict(font=dict(family=_fam("serif"), size=sz("title") + 4, color=p["ink"], weight=300),
                   subtitle=dict(font=dict(family=_fam("sans"), size=sz("dek") + 2, color=p["body"])),
                   x=0, xanchor="left", xref="paper", y=1, yref="container", yanchor="top",
                   pad=dict(t=24)),
        paper_bgcolor=p["panel"], plot_bgcolor=p["panel"],
        # The categorical palette in its fixed order. For a chart with a
        # finding, emphasise() turns one trace into the story and the rest context.
        colorway=p["cat"],
        colorscale=dict(sequential=seq, diverging=div),
        xaxis=xaxis, yaxis=axis,
        legend=dict(bgcolor="rgba(0,0,0,0)", borderwidth=0, orientation="h",
                    x=0, xanchor="left", y=1.02, yanchor="bottom",
                    font=dict(size=sz("label") + 1, color=p["ink"])),
        hoverlabel=dict(bgcolor=p["panel"], bordercolor=p["rule"],
                        font=dict(family=_fam("mono"), color=p["ink"], size=12)),
        hovermode="x unified",
        margin=dict(l=24, r=32, t=96, b=72),
        bargap=0.28,
        separators=".,",
    )
    t.data.scatter = [go.Scatter(line=dict(width=STROKE["data"] * PX_PER_PT),
                                 marker=dict(size=8, line=dict(width=2, color=p["panel"])))]
    t.data.bar = [go.Bar(marker=dict(line=dict(width=0)))]
    t.data.histogram = [go.Histogram(marker=dict(color=p["context"], line=dict(width=0)))]
    t.data.box = [go.Box(line=dict(color=p["body"], width=1), fillcolor=p["panel"])]
    t.data.heatmap = [go.Heatmap(colorscale=seq)]
    return t


def register():
    import plotly.io as pio
    pio.templates["describe"] = template("light")
    pio.templates["describe_dark"] = template("dark")


def apply(mode: str = "light"):
    """Register both templates and make one the default for every new figure."""
    import plotly.io as pio
    register()
    pio.templates.default = "describe" if mode == "light" else "describe_dark"


def _mode_of(fig) -> str:
    bg = (fig.layout.paper_bgcolor or fig.layout.template.layout.paper_bgcolor or "").upper()
    return "dark" if bg == palette("dark")["panel"].upper() else "light"


def emphasise(fig, *names):
    """Make the named trace(s) the story and every other trace context grey,
    thinner and behind. Works on any figure, including plotly.express output."""
    p = palette(_mode_of(fig))
    for tr in fig.data:
        hit = tr.name in names
        col = p["story"] if hit else p["context"]
        if tr.type == "scatter":
            tr.line.color = col
            tr.line.width = (STROKE["data"] if hit else STROKE["context"]) * PX_PER_PT
            tr.marker.color = col
        elif hasattr(tr, "marker"):
            tr.marker.color = col
    # story drawn last, on top
    fig.data = tuple(sorted(fig.data, key=lambda tr: tr.name in names))
    return fig


def benchmark(fig, value, label, axis="y"):
    """Dashed = threshold, benchmark or projection. The label sits clear of
    the marks: above the plot for a vertical rule, at the right for a horizontal one."""
    p = palette(_mode_of(fig))
    line = dict(color=p["ink"], width=1.25, dash="4px,4px")
    font = dict(color=p["ink"], family=_fam("sans"))
    if axis == "y":
        fig.add_hline(y=value, line=line, layer="above")
        fig.add_annotation(xref="paper", x=1, y=value, text=label, showarrow=False, xanchor="right",
                           yanchor="bottom", bgcolor=p["panel"], font=font)
    else:
        fig.add_vline(x=value, line=line, layer="above")
        fig.add_annotation(yref="paper", y=1, x=value, text=label, showarrow=False, xanchor="center",
                           yanchor="bottom", yshift=4, bgcolor=p["panel"], font=font)
    return fig


def outlier(fig, x, y, rule, label=None):
    """Coral ring + dot; `rule` is required."""
    import plotly.graph_objects as go
    if not rule:
        raise ValueError("outlier() needs the rule that flagged the point, e.g. '|z| > 3'.")
    p = palette(_mode_of(fig))
    fig.add_trace(go.Scatter(x=[x], y=[y], mode="markers", showlegend=False, hoverinfo="skip",
                             marker=dict(size=16, color="rgba(0,0,0,0)", line=dict(color=p["mark"], width=1.6))))
    fig.add_trace(go.Scatter(x=[x], y=[y], mode="markers", showlegend=False,
                             hovertemplate=f"{label or ''}<br>{rule}<extra></extra>",
                             marker=dict(size=7, color=p["mark"], line=dict(width=0))))
    if label:
        fig.add_annotation(x=x, y=y, text=f"{label}<br><span style='font-size:11px'>{rule}</span>",
                           showarrow=True, arrowhead=0, arrowwidth=1, arrowcolor=p["body"],
                           ax=40, ay=-40, align="left", bgcolor=p["panel"], font=dict(color=p["ink"]))
    return fig


SIGHT = 40.6   # the sight axis θ, up and to the right on screen


def measuring_edge(fig, axis="x", minor=4):
    """The axis as a measuring edge: an ink line with outward major ticks and
    shorter minors (`minor` per interval; 0 for none)."""
    p = palette(_mode_of(fig))
    kw = dict(showline=True, linecolor=p["ink"], linewidth=1.25, ticks="outside", ticklen=7,
              tickwidth=1.25, tickcolor=p["ink"])
    if minor:
        kw["minor"] = dict(ticks="outside", ticklen=3.5, tickwidth=0.9, tickcolor=p["body"],
                           nticks=minor + 1, showgrid=False)
    for which in ("x", "y") if axis == "both" else (axis,):
        (fig.update_xaxes if which == "x" else fig.update_yaxes)(**kw)
    return fig


def index_mark(fig, x, y, label, length=46, side="right"):
    """The one point the finding is about: open ring, seated dot, and a sight
    line at θ out to the label. Once per figure. Story blue, never coral."""
    import math
    import plotly.graph_objects as go
    if getattr(fig, "_dsc_index", False):
        raise ValueError("One index mark per chart.")
    object.__setattr__(fig, "_dsc_index", True)
    p = palette(_mode_of(fig))
    fig.add_trace(go.Scatter(x=[x], y=[y], mode="markers", showlegend=False, hoverinfo="skip",
                             marker=dict(size=17, color=p["panel"], line=dict(color=p["story"], width=1.8))))
    fig.add_trace(go.Scatter(x=[x], y=[y], mode="markers", showlegend=False, hovertemplate=f"{label}<extra></extra>",
                             marker=dict(size=6, color=p["story"], line=dict(width=0))))
    sgn = 1 if side == "right" else -1
    fig.add_annotation(x=x, y=y, text=label, showarrow=True, arrowhead=0, arrowwidth=1.25,
                       arrowcolor=p["story"], standoff=9,
                       ax=sgn * length * math.cos(math.radians(SIGHT)),
                       ay=-length * math.sin(math.radians(SIGHT)),
                       xanchor="left" if sgn > 0 else "right", yanchor="bottom",
                       font=dict(color=p["ink"], family=_fam("sans")))
    return fig


def _is_category(fig, ax):
    for tr in fig.data:
        vals = getattr(tr, ax, None)
        if vals is not None and len(vals) and isinstance(vals[0], str):
            return True
    return False


def finish(fig, title, n, source, dek=None, computed=None, units=None):
    """Title (the finding) and dek above; n, source and date below.
    units = (x, y): unit labels, mono uppercase; the y unit sits above the
    axis, horizontal. "" removes an axis title plotly.express added."""
    if not n or not source:
        raise ValueError("Every chart states n and its source.")
    p = palette(_mode_of(fig))
    computed = computed or date.today().strftime("%-d %b %Y")
    width = fig.layout.width or 900
    # the title starts at the plot's left edge, after any category labels
    inset = 0
    if _is_category(fig, "y"):
        tr = next(t for t in fig.data if t.y is not None and len(t.y))
        inset = max(len(str(v)) for v in tr.y) * 8 + 12
    wrap = lambda text, px: "<br>".join(textwrap.wrap(text, max(20, int((width - 56 - inset) / px))))
    title_px, dek_px = (SIZE["title"] * PX_PER_PT + 4) * 0.5, (SIZE["dek"] * PX_PER_PT + 2) * 0.5
    title_txt, dek_txt = wrap(title, title_px), wrap(dek, dek_px) if dek else None
    lines_t, lines_d = title_txt.count("<br>") + 1, (dek_txt.count("<br>") + 1 if dek else 0)
    head = 24 + lines_t * 30 + (8 + lines_d * 20 if dek else 0) + 32
    fig.update_layout(title=dict(text=title_txt, subtitle=dict(text=dek_txt) if dek else None))

    # categorical axes: names are words, so sans ink rather than mono numerals
    for ax in ("x", "y"):
        if _is_category(fig, ax):
            fig.update_layout({f"{ax}axis": dict(tickfont=dict(family=_fam("sans"), color=p["ink"]))})

    ux, uy = units or (None, None)
    for ax, u in (("x", ux), ("y", uy)):
        cur = getattr(fig.layout, f"{ax}axis").title.text
        if u is not None or cur:
            fig.update_layout({f"{ax}axis": dict(title=dict(text=(u if u is not None else cur).upper() or None))})
    if fig.layout.yaxis.title.text:           # move the y unit above the axis, horizontal
        fig.add_annotation(xref="paper", yref="paper", x=0, y=1, xanchor="left", yanchor="bottom",
                           yshift=8, showarrow=False, text=fig.layout.yaxis.title.text,
                           font=dict(family=_fam("mono"), size=11, color=p["dim"]))
        fig.update_yaxes(title=dict(text=None))

    x_title = bool(fig.layout.xaxis.title.text)
    drop = 30 + (26 if x_title else 0)
    fig.add_annotation(xref="paper", yref="paper", x=0, y=0, yshift=-drop, xanchor="left", yanchor="top",
                       showarrow=False, align="left",
                       text=(f"<span style='font-family:{_fam('mono')};color:{p['ink']}'>{n}</span><br>"
                             f"<span style='color:{p['body']}'>Source: {source}. Computed {computed}.</span>"),
                       font=dict(size=11, family=_fam("sans")))
    fig.update_layout(margin=dict(t=head, b=drop + 48))
    return fig
