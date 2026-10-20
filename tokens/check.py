"""Check the tokens. Every rule here is a measurement, so a colour change that
breaks one fails CI instead of shipping.

  python3 tokens/check.py           run every check; exit 1 on any FAIL
  python3 tokens/check.py --audit   also list hex values in the repo's own
                                    source that are not tokens (informational)

What it measures, per mode (light and dark are each checked against their
own surfaces):

  1. Text contrast    ink, body, dim and the role colours as text: WCAG 4.5:1
                      on ground, panel and field. Coral is exempt because it
                      is never text (charts/CHARTS.md §2).
  2. Mark contrast    every colour a chart draws with: 3:1 on ground and panel.
  3. Categorical      the six-check palette method (charts/CHARTS.md §2 uses
                      the same validator): OKLCH lightness band, chroma floor,
                      adjacent-pair Delta E >= 8 under protan and deutan
                      simulation (6-8 is a WARN that needs direct labels),
                      >= 15 under normal vision, the first three slots on all
                      pairs (scatter, maps), and every slot >= 15 from coral
                      so an outlier ring never looks like a series.
  4. Story / context  the one-story-series pair still separates.
  5. Sequential       one hue, lightness strictly monotone, steps >= 0.06 L.
  6. Diverging        each arm monotone; both arms the same lightness at the
                      same step; a neutral (chroma < 0.02) midpoint.
  7. Drift            ui/ui.css, type/typography.css, charts/chartkit.py and
                      charts/mpl/mpl_describe.py carry the token values.
"""
import itertools
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from colour import contrast, delta_e, delta_e_cvd, oklch  # noqa: E402
import build  # noqa: E402

TEXT_MIN, MARK_MIN = 4.5, 3.0
BAND = {"light": (0.43, 0.77), "dark": (0.48, 0.67)}
CHROMA_FLOOR = 0.10
CVD_TARGET, CVD_FLOOR, NORMAL_FLOOR = 8.0, 6.0, 15.0
ALL_PAIRS_SLOTS = 3
SEQ_MIN_DL, HUE_SPREAD = 0.06, 40
DIV_L_TOL, NEUTRAL_C = 0.03, 0.02

results = []


def report(ok, name, detail, warn=False):
    results.append(("WARN" if warn and ok else "PASS" if ok else "FAIL", name, detail))


def main():
    tokens = json.loads((HERE / "tokens.json").read_text())
    flat = build.resolve(tokens)
    v = lambda key, mode: flat[key][mode]  # noqa: E731

    for mode in ("light", "dark"):
        surfaces = {s: v(f"color.surface.{s}", mode) for s in ("ground", "panel", "field")}
        mark_surfaces = {s: surfaces[s] for s in ("ground", "panel")}
        tag = f"[{mode}]"

        # 1. text
        for key in ("color.text.ink", "color.text.body", "color.text.dim",
                    "color.role.active", "color.role.neg", "color.role.pos"):
            worst = min((contrast(v(key, mode), h), s) for s, h in surfaces.items())
            report(worst[0] >= TEXT_MIN, f"{tag} text {key[6:]}",
                   f"{v(key, mode)} worst {worst[0]:.2f}:1 on {worst[1]}")
        ai = contrast(v("color.text.active-ink", mode), v("color.role.active", mode))
        report(ai >= TEXT_MIN, f"{tag} text active-ink on active", f"{ai:.2f}:1")

        # 2. marks
        cat = [v(f"color.viz.cat.{i}", mode) for i in range(1, 7)]
        marks = {"role.mark": v("color.role.mark", mode), "viz.story": v("color.viz.story", mode),
                 "viz.context": v("color.viz.context", mode),
                 **{f"viz.cat.{i}": c for i, c in enumerate(cat, 1)}}
        for name, h in marks.items():
            worst = min((contrast(h, s), n) for n, s in mark_surfaces.items())
            report(worst[0] >= MARK_MIN, f"{tag} mark {name}", f"{h} worst {worst[0]:.2f}:1 on {worst[1]}")

        # 3. categorical
        lo, hi = BAND[mode]
        off = [(h, round(oklch(h)[0], 3)) for h in cat if not lo <= oklch(h)[0] <= hi]
        report(not off, f"{tag} categorical lightness band", f"L {lo}-{hi}" + (f"; outside: {off}" if off else ""))
        grey = [(h, round(oklch(h)[1], 3)) for h in cat if oklch(h)[1] < CHROMA_FLOOR]
        report(not grey, f"{tag} categorical chroma floor", f">= {CHROMA_FLOOR}" + (f"; below: {grey}" if grey else ""))
        adj = list(zip(cat, cat[1:]))
        cvd = min((delta_e_cvd(a, b), a, b) for a, b in adj)
        report(cvd[0] >= CVD_FLOOR, f"{tag} categorical adjacent CVD",
               f"worst {cvd[1]}/{cvd[2]} dE {cvd[0]:.1f}", warn=cvd[0] < CVD_TARGET)
        nor = min((delta_e(a, b), a, b) for a, b in adj)
        report(nor[0] >= NORMAL_FLOOR, f"{tag} categorical adjacent normal vision",
               f"worst {nor[1]}/{nor[2]} dE {nor[0]:.1f}")
        first = list(itertools.combinations(cat[:ALL_PAIRS_SLOTS], 2))
        fc = min((delta_e_cvd(a, b), a, b) for a, b in first)
        fn = min((delta_e(a, b), a, b) for a, b in first)
        report(fc[0] >= CVD_TARGET and fn[0] >= NORMAL_FLOOR, f"{tag} categorical first {ALL_PAIRS_SLOTS}, all pairs",
               f"CVD {fc[0]:.1f} ({fc[1]}/{fc[2]}), normal {fn[0]:.1f}")
        coral = v("color.role.mark", mode)
        near = min((delta_e(coral, h), h) for h in cat)
        report(near[0] >= NORMAL_FLOOR, f"{tag} categorical vs outlier coral", f"nearest {near[1]} dE {near[0]:.1f}")

        # 4. story / context
        st, cx = v("color.viz.story", mode), v("color.viz.context", mode)
        report(delta_e(st, cx) >= NORMAL_FLOOR and delta_e_cvd(st, cx) >= CVD_TARGET, f"{tag} story vs context",
               f"normal {delta_e(st, cx):.1f}, CVD {delta_e_cvd(st, cx):.1f}")

    # 5. sequential (mode-independent ramps)
    for ramp in ("seq", "seq-alt"):
        hexes = [flat[f"color.viz.{ramp}.{s}"]["light"] for s in build.SEQ_STEPS]
        ls = [oklch(h)[0] for h in hexes]
        mono = all(a > b for a, b in zip(ls, ls[1:]))
        gap = min(a - b for a, b in zip(ls, ls[1:]))
        hues = [oklch(h)[2] for h in hexes if oklch(h)[1] > 0.02]
        spread = max(hues) - min(hues)
        spread = min(spread, 360 - spread)
        report(mono and gap >= SEQ_MIN_DL and spread <= HUE_SPREAD, f"sequential {ramp}",
               f"monotone {mono}, min step {gap:.3f} L, hue spread {spread:.0f} deg")

    # 6. diverging
    for mode in ("light", "dark"):
        neg = [v(f"color.viz.div.n{i}", mode) for i in range(1, 6)]
        pos = [v(f"color.viz.div.p{i}", mode) for i in range(1, 6)]
        mid = v("color.viz.div.0", mode)
        ln, lp = [oklch(h)[0] for h in neg], [oklch(h)[0] for h in pos]
        step = lambda ls: all(abs(b - a) >= SEQ_MIN_DL for a, b in zip(ls, ls[1:]))  # noqa: E731
        sym = max(abs(a - b) for a, b in zip(ln, lp))
        report(step(ln) and step(lp) and sym <= DIV_L_TOL and oklch(mid)[1] < NEUTRAL_C,
               f"[{mode}] diverging", f"arm L match within {sym:.3f}, midpoint chroma {oklch(mid)[1]:.3f}")

    # 7. drift in the files that consume the tokens
    drift(flat)

    width = max(len(r[1]) for r in results)
    for state, name, detail in results:
        print(f"  [{state}] {name.ljust(width)}  {detail}")
    fails = sum(r[0] == "FAIL" for r in results)
    print(f"\n{len(results)} checks, {fails} failed")
    if "--audit" in sys.argv:
        audit(flat)
    sys.exit(1 if fails else 0)


def css_block(text, selector_pattern):
    m = re.search(selector_pattern + r"\s*\{(.*?)\}", text, re.S)
    return dict(re.findall(r"--([\w-]+)\s*:\s*([^;]+);", m.group(1))) if m else {}


def drift(flat):
    by_css = {t["css"][2:]: t for t in flat.values()}
    web = build.type_scale(json.loads((HERE / "tokens.json").read_text()), "web")

    def compare(label, found, mode):
        bad = []
        for name, val in found.items():
            val = val.strip()
            if name in by_css:
                want = build.css_value(by_css[name], by_css[name][mode])
            elif name.startswith("t-") and name[2:] in web:
                want = web[name[2:]]
            else:
                continue
            if norm(val) != norm(want):
                bad.append(f"--{name} {val} (token {want})")
        report(not bad, f"drift {label}", "; ".join(bad) if bad else f"{len(found)} values match")

    ui = (ROOT / "ui/ui.css").read_text()
    compare("ui/ui.css light", css_block(ui, r"(?m)^:root"), "light")
    compare("ui/ui.css dark", css_block(ui, r':root\[data-theme="dark"\]'), "dark")
    ty = (ROOT / "type/typography.css").read_text()
    compare("type/typography.css", css_block(ty, r"(?m)^:root"), "light")

    pymap = {"story": "viz-story", "context": "viz-context"}
    for path, names in (("charts/chartkit.py", ("LIGHT", "DARK")), ("charts/mpl/mpl_describe.py", ("C",))):
        src = (ROOT / path).read_text()
        for var, mode in zip(names, ("light", "dark")):
            m = re.search(rf"^{var}\s*=\s*(\{{.*?\}})", src, re.S | re.M)
            found = {pymap.get(k, k): h for k, h in re.findall(r'"([\w-]+)":\s*"(#[0-9A-Fa-f]{6})"', m.group(1))}
            compare(f"{path} {var}", found, mode)


def norm(s):
    """Compare values, not spellings: 1.50 == 1.5, .2 == 0.2, quotes ignored."""
    s = re.sub(r"\s+", "", str(s)).lower().replace("'", "").replace('"', "")
    return re.sub(r"(?<![#\w])\d*\.?\d+", lambda m: repr(float(m.group())), s)


def audit(flat):
    """Every #rrggbb in the repo's own source that is not a token value."""
    known = {str(t[m]).upper() for t in flat.values() for m in ("light", "dark") if t["type"] == "color"}
    hits = {}
    for p in ROOT.rglob("*"):
        if p.suffix not in (".py", ".css", ".json", ".md") or "dist" in p.parts or ".git" in p.parts:
            continue
        if p.name in ("tokens.json", "TOKENS.md", "figures.json", "manifest.json"):
            continue
        for h in re.findall(r"#[0-9A-Fa-f]{6}\b", p.read_text(errors="ignore")):
            if h.upper() not in known:
                hits.setdefault(h.upper(), set()).add(str(p.relative_to(ROOT)))
    print(f"\nAudit: {len(hits)} hex values in source that are not tokens")
    for h, files in sorted(hits.items(), key=lambda kv: -len(kv[1])):
        print(f"  {h}  {', '.join(sorted(files))}")


if __name__ == "__main__":
    main()
