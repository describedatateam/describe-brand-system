"""
streamlit_app.py — the reference dashboard as a Streamlit app.

    cd apps && streamlit run streamlit_app.py

Run it from apps/ so Streamlit picks up apps/.streamlit/config.toml (written
by `python3 apps/build.py`). Same figures and layout as apps/out/dashboard.html;
the chart is Plotly with the describe template and the chart kit's furniture.
"""

from __future__ import annotations

import json
import os

import plotly.graph_objects as go
import streamlit as st

import describe_streamlit as S
from describe_charts import plotly_theme as P

HERE = os.path.dirname(os.path.abspath(__file__))
A = json.load(open(os.path.join(HERE, "..", "decisions", "uci_audit.json"), encoding="utf-8"))
MONTHS = ["Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov"]
SRC = "Online Retail dataset (UCI, public), Dec 2010 to Nov 2011"

st.set_page_config(page_title="Store health", layout="wide")
S.use()          # follows Streamlit's own light or dark setting

v = [x / 1e6 for x in A["monthly_net_gbp"].values()]
S.header("Store health", f"Sep to Nov brought in {A['sep_nov_share'] * 100:.0f}% of the year.",
         "Net revenue after duplicates, cancellations, postage and fees are taken out. Twelve full months.")
S.kpis([
    S.kpi("Net revenue", f"£{A['year_net_gbp'] / 1e6:.2f}", "M",
          f'<span class="pos">+{(v[11] / v[10] - 1) * 100:.1f}%</span> November vs October'),
    S.kpi("Customers with an ID", f"{A['customers_known']:,}",
          note=f"{A['customers_for_half']} of them bring in half the revenue"),
    S.kpi("Sales value with no customer ID", f"{A['missing_customer_value_share'] * 100:.1f}", "%",
          f"{A['missing_customer_lines_clean']:,} sale lines carry no ID"),
    S.kpi("Lines flagged as outliers", str(len(A["flagged_lines"])),
          note="all three were cancelled", rule="robust z > 7 on line value"),
])

left, right = st.columns([1.6, 1], gap="medium")
with left:
    fig = go.Figure()
    fig.add_scatter(x=MONTHS[:9], y=v[:9], name="Dec to Aug", mode="lines")
    fig.add_scatter(x=MONTHS[8:], y=v[8:], name="Sep to Nov", mode="lines")
    P.emphasise(fig, "Sep to Nov")
    P.measuring_edge(fig, "x", minor=0)
    P.index_mark(fig, "Nov", v[11], f"Nov £{v[11]:.2f}M", side="left")
    fig.update_layout(showlegend=False, height=420, yaxis=dict(range=[0, 1.6]))
    P.finish(fig, "Net revenue by month", n=f"n = {A['window_sale_lines']:,} lines",
             source="UCI Online Retail", units=("", "£ million, net"))
    st.plotly_chart(fig, theme=None, use_container_width=True)

with right:
    st.html('<div class="d-panel__head"><span class="d-panel__title">Flagged order lines</span>'
            '<span class="d-panel__meta">robust z &gt; 7</span></div>')
    rows = sorted(A["flagged_lines"], key=lambda r: -r["val"])
    st.dataframe(
        {"Product": [r["Description"].replace(" ,", ",").capitalize() for r in rows],
         "Units": [r["Quantity"] for r in rows],
         "Value, £": [round(r["val"]) for r in rows]},
        hide_index=True, use_container_width=True,
        column_config={"Units": st.column_config.NumberColumn(format="localized"),
                       "Value, £": st.column_config.NumberColumn(format="localized")})
    st.caption("Each line was cancelled the same day, so it never counts as revenue.")

S.source(f"n = {A['window_sale_lines']:,} sale lines", SRC)
