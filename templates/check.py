"""
check.py — keep the slide and social templates honest.  python3 templates/check.py

Builds both template sets (no browser needed) and fails if:

  1. enrich.css or a build script types a colour instead of reading a token
  2. coral (--mark) is used anywhere but the outlier ring and the outside
     stars of an outlier illustration
  3. an illustration without confirmed rights is placed (ILLUSTRATION.md §4)
  4. the guards stop guarding: an outlier ring without its rule, a full-circle
     graduation, data_cells() without data, a second index mark on a chart
  5. a page carries no source line (every page with a figure states one)
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "charts", "kit"))

import kit as K  # noqa: E402

fails: list[str] = []


def ok(cond, msg):
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond:
        fails.append(msg)


def raises(fn, msg):
    try:
        fn()
    except ValueError:
        ok(True, msg)
    else:
        ok(False, msg)


HEX = re.compile(r"#[0-9A-Fa-f]{6}\b")
for rel in ("templates/enrich.css", "templates/kit.py", "slides/build.py", "social/templates/build.py",
            "apps/app.css", "apps/build.py", "apps/describe_streamlit.py", "apps/streamlit_app.py"):
    src = open(os.path.join(ROOT, rel), encoding="utf-8").read()
    ok(not HEX.findall(src), f"{rel}: no typed colours (found {sorted(set(HEX.findall(src)))})")

outs = []
for script in ("slides/build.py", "social/templates/build.py"):
    r = subprocess.run([sys.executable, os.path.join(ROOT, script)], capture_output=True, text=True)
    ok(r.returncode == 0, f"{script} builds" + ("" if r.returncode == 0 else ": " + r.stderr[-400:]))
    outs += [l.strip() for l in r.stdout.splitlines() if l.strip().endswith(".html")]

for path in outs:
    html = open(path, encoding="utf-8").read()
    html = html[html.index("<body>"):]   # the shared stylesheet names every class
    name = os.path.relpath(path, ROOT)
    marks = re.findall(r'class="mark[ "]|var\(--mark\)', html)
    rings = html.count('aria-label="Outlier:')
    outside = html.count("--c:var(--mark)")
    # each outlier ring paints two mark elements (ring + dot)
    ok(len(marks) == 2 * rings + outside, f"{name}: coral only on outlier rings ({rings}) and outside stars ({outside})")
    for sec in re.findall(r'<section class="pg.*?</section>', html, flags=re.S):
        has_fig = re.search(r'class="num', sec) is not None
        if has_fig:
            ok("Source:" in sec or "Flagged by" in sec, f"{name}: a page with figures states its source")

# the data-app kit: the static dashboard and the Streamlit theme
r = subprocess.run([sys.executable, os.path.join(ROOT, "apps/build.py")], capture_output=True, text=True)
ok(r.returncode == 0, "apps/build.py builds" + ("" if r.returncode == 0 else ": " + r.stderr[-400:]))
sys.path.insert(0, os.path.join(ROOT, "apps"))
import describe_streamlit as S  # noqa: E402
from describe_charts.tokens import TOKENS  # noqa: E402

for path in [l.strip() for l in r.stdout.splitlines() if l.strip().endswith(".html")]:
    html = open(path, encoding="utf-8").read()
    body = html[html.index("<body"):]
    name = os.path.relpath(path, ROOT)
    flagged = len(json.load(open(os.path.join(ROOT, "decisions/uci_audit.json")))["flagged_lines"])
    # coral: one marker per flagged line in the table, one on the tile; none in the chart
    ok(body.count('class="d-outlier"') == flagged + 1, f"{name}: coral only on the flagged lines and their tile")
    coral = {TOKENS[m]["mark"].lower() for m in ("light", "dark")}
    ok(not any(c in body.lower() for c in coral), f"{name}: the chart has no coral (it has no outliers)")
    ok("Source:" in body, f"{name}: the page states its source")
    ok("t-label" not in body, f"{name}: no mono eyebrow above the title")
cfg = open(os.path.join(ROOT, "apps/.streamlit/config.toml"), encoding="utf-8").read()
ok(cfg == S.config_toml(), "apps/.streamlit/config.toml is generated from the tokens")
ok("robust z" in S.kpi("Flagged", "3", rule="robust z > 7"), "kpi() writes an outlier tile's rule into it")

raises(lambda: K.outlier_ring(40, rule=""), "outlier_ring() refuses a ring without its rule")
raises(lambda: K._radial_scale(0, 0, 10, 0, 340, 6, 5, 2, 1, "faint", 1), "graduation refuses a full circle")
raises(lambda: K.data_cells([], 100, 100), "data_cells() refuses an empty series")
raises(lambda: K.art("scorpio", HERE, {"lines": "ink"}), "art() refuses an illustration without confirmed rights")
raises(lambda: K.art("libra", HERE, {"lines": "mark"}), "art() keeps coral off the drawing's lines")
raises(lambda: K.gauge(1.4), "gauge() takes a share between 0 and 1")

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from describe_charts import mpl as D  # noqa: E402

fig, ax = plt.subplots()
D.index_mark(ax, 0, 0, "a")
raises(lambda: D.index_mark(ax, 1, 1, "b"), "index_mark() once per chart")
plt.close(fig)

print()
if fails:
    print(f"{len(fails)} failed")
    sys.exit(1)
print("all passed")
