"""
check.py — keep the kit honest.  python3 charts/kit/check.py

  1. styles/*.mplstyle match what tokens.json generates (no hand edits)
  2. the bundled tokens.json snapshot equals tokens/dist/tokens.json
     (`--write` refreshes the snapshot and the styles after a token change)
  3. the report lockup is the approved wordmark artwork, unchanged
  4. the rule guards still raise: two story series, an outlier with no
     rule, a chart with no n or source, a unit label over four words
  5. both style files load in matplotlib, both Plotly templates build
"""
import filecmp
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from describe_charts import mpl as D, plotly_theme as P
from describe_charts.tokens import SHARED, SNAPSHOT, from_shared, palette

if "--write" in sys.argv:
    snap = json.load(open(SNAPSHOT, encoding="utf-8"))
    snap.update(from_shared())
    with open(SNAPSHOT, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(snap, indent=2, ensure_ascii=False) + "\n")
    D.write_styles()
    print("wrote", SNAPSHOT, "and styles/")

fails = []


def ok(cond, msg):
    print(("  ok   " if cond else "  FAIL ") + msg)
    if not cond:
        fails.append(msg)


# 1
with tempfile.TemporaryDirectory() as tmp:
    for path in D.write_styles(tmp):
        name = os.path.basename(path)
        ok(filecmp.cmp(path, os.path.join(D.STYLE_DIR, name), shallow=False),
           f"{name} is in sync with tokens.json")

# 2
snap = json.load(open(SNAPSHOT, encoding="utf-8"))
if os.path.exists(SHARED):
    shared = from_shared()
    for mode in ("light", "dark"):
        diff = sorted(k for k in shared[mode] if shared[mode][k] != snap[mode].get(k))
        ok(not diff, f"{mode} snapshot = tokens/dist/tokens.json" + (f" (differs: {', '.join(diff)})" if diff else ""))
else:
    print("  skip tokens/dist/tokens.json not found (running outside the brand repo)")

# 3
src = os.path.join(ROOT, "wordmark", "web", "lockup-compact.svg")
ok(filecmp.cmp(src, os.path.join(HERE, "describe_charts", "templates", "lockup-compact.svg"), shallow=False),
   "report lockup = wordmark/web/lockup-compact.svg")

# 4
D.apply()


def raises(fn, msg):
    try:
        fn()
    except ValueError:
        ok(True, msg)
    else:
        ok(False, msg)


fig, ax = plt.subplots()
D.story(ax, [0, 1], [0, 1])
raises(lambda: D.story(ax, [0, 1], [1, 0]), "a second story series raises")
raises(lambda: D.outlier(ax, 0, 0, rule=""), "an outlier with no rule raises")
raises(lambda: D.finish(fig, ax, "t", n="", source="s"), "a chart with no n raises")
raises(lambda: D.units(ax, y="far too many words here"), "a unit label over four words raises")
plt.close("all")

# 5
for mode in ("light", "dark"):
    plt.style.use(os.path.join(D.STYLE_DIR, f"describe-{mode}.mplstyle"))
    ok(matplotlib.rcParams["axes.prop_cycle"].by_key()["color"][0].upper() == palette(mode)["story"].upper(),
       f"describe-{mode}.mplstyle loads; first series is story")
    try:
        t = P.template(mode)
        ok(t.layout.colorway[0] == palette(mode)["story"], f"Plotly template '{mode}' builds")
    except ImportError:
        print("  skip Plotly not installed")

print(f"\n{'FAILED: ' + str(len(fails)) if fails else 'all checks pass'}")
sys.exit(1 if fails else 0)
