"""
build.py — assemble charts/specimen.html (self-contained) and charts/svg/*.svg.

    python3 build.py

Recomputes every figure from source (examples.py), draws the furniture sheet
from chartkit.py, and inlines ../type/typography.css and ../ui/ui.css so the
published page carries the real tokens.
"""

import json
import os
import re
from datetime import datetime

import chartkit as K
from examples import FIGURES, COMPUTED

HERE = os.path.dirname(os.path.abspath(__file__))


def read(p):
    with open(os.path.join(HERE, p), encoding="utf-8") as fh:
        return fh.read()


type_css = read("../type/typography.css")
ui_css = re.sub(r"@import url\('\.\./type/typography\.css'\);\s*", "", read("../ui/ui.css"))


# ------------------------------------------------------------- figures ---
def table_html(t):
    num = set(t.get("num", []))
    h = "".join(f'<th scope="col"{" class=num" if i in num else ""}>{K.esc(c)}</th>'
                for i, c in enumerate(t["cols"]))
    body = []
    for r in t["rows"]:
        cells = []
        for i, v in enumerate(r):
            cls = []
            if i in num:
                cls.append("num")
            if v in ("—", ""):
                cls.append("null")
            c = f' class="{" ".join(cls)}"' if cls else ""
            tag = "th scope=row" if i == 0 else "td"
            cells.append(f"<{tag}{c}>{K.esc(v)}</{tag.split()[0]}>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    cap = f'<caption>{K.esc(t["note"])}</caption>' if t.get("note") else ""
    return f"<table>{cap}<thead><tr>{h}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def figure_html(i, fg):
    near = ' data-nearest="1"' if fg.get("nearest") else ""
    uses = "".join(f"<span>{K.esc(u)}</span>" for u in fg["uses"])
    return f"""
<figure class="fg" id="fig-{fg['id']}"{near}>
  <div class="fg-k"><span class="t-label">Fig. {i:02d}</span><span class="form">{K.esc(fg['form'])}</span></div>
  <h3 class="fg-t">{K.esc(fg['title'])}</h3>
  <p class="fg-d">{K.esc(fg['dek'])}</p>
  <div class="fg-view">{fg['svg']}</div>
  <div class="fg-table" hidden>{table_html(fg['table'])}</div>
  <figcaption class="fg-prov"><span class="n">{K.esc(fg['n'])}</span>
    <span class="src">Source: {K.esc(fg['source'])}. Computed {COMPUTED}.</span>
    <button type="button" class="fg-tog" aria-pressed="false">Table view</button></figcaption>
  <div class="fg-uses" aria-label="Furniture used">{uses}</div>
</figure>"""


# ---------------------------------------------------------- validation ---
# Output of validate_palette.js (dataviz method: OKLab ΔE×100, Machado 2009
# CVD at severity 1.0), run 27 Sep 2026. Recorded, not re-derived here, because
# the validator is Node and this build is Python; re-run it on any change.
VALIDATION = [
    ("#0F58E5", "#64748B", "Story + context", "Light", "18.7", "16.9", "Pass",
     "The pair the charts use."),
    ("#092052", "#0F58E5", "Navy + blue + grey as three categories", "Light", "—", "—", "Fail",
     "Navy L 0.26 is below the 0.43 band; it reads as black. Navy is ink, never data."),
    ("#5B8DF0", "#676A70", "Story + context", "Dark", "19.8", "19.3", "Pass",
     "Dark context is a neutral grey, on purpose."),
    ("#5B8DF0", "#7285A6", "Story + blue-grey context", "Dark", "11.1", "11.4", "Fail",
     "Shares the story's hue; below the ΔE 15 normal-vision floor."),
    ("#64748B", "#8C1D1D", "Context + negative", "Light", "22.0", "16.6", "Pass", ""),
    ("#676A70", "#E0736F", "Context + negative", "Dark", "21.1", "10.2", "Pass", ""),
    ("#64748B", "#E5484D", "Context + coral marker", "Light", "23.1", "9.2", "Pass",
     "Above the ΔE 8 target; the ring shape is a second channel anyway."),
    ("#676A70", "#F0696D", "Context + coral marker", "Dark", "23.7", "9.3", "Pass", ""),
]


def validation_html():
    rows = []
    for a, b, what, mode, dn, dc, v, note in VALIDATION:
        extra = '<i style="background:#0F58E5"></i><i style="background:#64748B"></i>' if "three" in what else ""
        sw = f'<span class="sw"><i style="background:{a}"></i>' + (extra if extra else f'<i style="background:{b}"></i>') + "</span>"
        if extra:
            sw = f'<span class="sw"><i style="background:{a}"></i>{extra}</span>'
        cls = "ok" if v == "Pass" else "no"
        rows.append(f"<tr><td>{sw}{K.esc(what)}</td><td>{mode}</td><td class=num>{dn}</td>"
                    f"<td class=num>{dc}</td><td><span class='verdict {cls}'>{v}</span></td>"
                    f"<td style='color:var(--body);font-size:12.8px'>{K.esc(note)}</td></tr>")
    return ("<div class=wrapx><table class=vt><thead><tr><th>Pair</th><th>Mode</th>"
            "<th class=num>ΔE normal</th><th class=num>ΔE CVD</th><th>Verdict</th><th>Why</th>"
            "</tr></thead><tbody>" + "".join(rows) + "</tbody></table></div>"
            "<p class='fg-d' style='margin-top:16px'>Floors: ΔE 15 under normal vision, ΔE 8 "
            "under protanopia and deuteranopia. The validator also flags context grey's low chroma "
            "(0.041 light, 0.010 dark) on every run. For identity colours that is a failure; for "
            "context it is the job. So the palette carries <b>one</b> story series per chart. "
            "Two or more series that each need an identity are small multiples, or a palette "
            "extension — a decision for the brand, not for a chart.</p>"
            "<p class='fg-d'>Text contrast, WCAG: dim ink <span class=t-num>#63738D</span> 4.52:1 on the "
            "ground (was <span class=t-num>#8A99B0</span>, 2.89:1 — fixed across the kit). "
            "Coral as text: 3.91:1. It fails, so coral is never text.</p>")


# ---------------------------------------------------------- furniture ---
def tile(name, rule, body, w=240, h=110):
    return (f'<figure><svg class="dsc-chart" viewBox="0 0 {w} {h}" role="img" aria-label="{K.esc(name)}" '
            f'fill="none">{body}</svg><figcaption><b>{K.esc(name)}</b><span>{K.esc(rule)}</span>'
            f'</figcaption></figure>')


def kit_html():
    T = []
    xs = K.Linear(0, 100, 24, 220)
    T.append(tile("X-axis", "Baseline, measured ticks, mono numerals. Minor ticks carry no label.",
                  K.x_axis(xs, 50, [0, 25, 50, 75, 100], lambda v: f"{v:.0f}",
                           minor=[12.5, 37.5, 62.5, 87.5])))
    ys = K.Linear(0, 30, 96, 14)
    T.append(tile("Y-axis and grid", "Solid hairlines, one step off the surface. No vertical rule.",
                  K.y_axis(ys, 40, 224, [0, 10, 20, 30], lambda v: f"{v:.0f}")))
    ls = K.Log(1, 1000, 24, 220)
    T.append(tile("Log scale", "1-2-5 ticks. Always named in the unit label or the dek.",
                  K.x_axis(ls, 50, [1, 10, 100, 1000], lambda v: f"{v:,.0f}",
                           minor=[v for v in K.log_ticks(1, 1000) if v not in (1, 10, 100, 1000)])))
    T.append(tile("Unit label", "Mono, uppercase, 11px or less, four words or fewer.",
                  K.unit_label(24, 50, "Change since 2010, %") + K.unit_label(24, 76, "Patients")))
    T.append(tile("Data dot", "8px, filled, with a 2px ring in the surface colour where it crosses a line.",
                  K.line(24, 70, 216, 36, "c-context", 2) + K.data_dot(120, 53, "c-story") +
                  K.data_dot(170, 44.3, "c-context")))
    T.append(tile("Series line", "2px, round joins. A gap in the data is drawn as a gap.",
                  K.series_line([(24, 80), (60, 62), (96, 66), None, (150, 40), (190, 46), (216, 30)], "c-story")))
    up = [(24 + i * 24, 70 - i * 5 - 10 - abs(i - 4) * 2) for i in range(9)]
    dn = [(24 + i * 24, 70 - i * 5 + 10 + abs(i - 4) * 2) for i in range(9)]
    T.append(tile("Confidence band", "The series hue at 12%. No edge stroke. Wider where the data is thin.",
                  K.ci_band(up, dn) + K.series_line([(24 + i * 24, 70 - i * 5) for i in range(9)], "c-story")))
    T.append(tile("Confidence interval", "Whisker with measured end caps, dot at the estimate.",
                  K.interval(70, 180, 55, "c-story", 10) + K.data_dot(124, 55, "c-story", r=5)))
    T.append(tile("Comparison bracket", "Joins two compared rows. States the difference and its interval.",
                  K.data_dot(60, 30, "c-story", 5) + K.data_dot(96, 80, "c-story", 5) +
                  K.comparison_bracket(120, 30, 80, "+1.47", sub="CI 1.29–1.64")))
    T.append(tile("Outlier marker", "Coral ring and dot. Always states the test. The text stays ink.",
                  K.series_line([(24, 76), (60, 72), (96, 78)], "c-context", 1.5) +
                  K.outlier_marker(120, 30, "Oct 2008", rule="|Z| > 3", dx=20, dy=10) +
                  K.series_line([(144, 74), (180, 70), (216, 75)], "c-context", 1.5)))
    T.append(tile("Annotation leader", "Elbowed, never curved. The note is a sentence, so it is sans.",
                  K.data_dot(60, 80, "c-story") + K.leader(60, 80, 30, -44, "Listed on Nasdaq", sub="Jun 1997")))
    T.append(tile("Measurement label", "A value at a mark. Mono numerals — budget rule 01.",
                  K.bar(24, 160, 42, 60, "c-context", horizontal=True) +
                  K.measurement_label(166, 55, "+1,613%")))
    T.append(tile("Direct label", "Swatch, name in sans, value in mono. Selective: the end, the extreme.",
                  K.series_line([(24, 76), (90, 60), (150, 50)], "c-story") + K.data_dot(150, 50, "c-story") +
                  K.direct_label(158, 50, "Apple", "2,343", "c-story")))
    T.append(tile("Legend", "Present for two or more series. The swatch carries identity; the text is ink.",
                  K.legend([("c-story", "Apple"), ("c-context", "Seven others")], 24, 56)))
    T.append(tile("Reference rule", "Dashed means threshold, benchmark or projection. Nothing else.",
                  K.y_axis(K.Linear(0, 1, 90, 20), 24, 224, [0, .5, 1], lambda v: "", grid=True) +
                  K.reference_rule(y=46, extent=(24, 224), label="S&P 500 +256%", horizontal=True)))
    T.append(tile("Missing data", "Should exist, doesn't. Hatch over the gap, line broken under it.",
                  K.series_line([(24, 70), (80, 60), None, (160, 50), (216, 44)], "c-context") +
                  K.missing_band(88, 152, 22, 92)))
    T.append(tile("Not applicable", "Did not exist yet. Nothing before it — not zero, not a gap. Capped.",
                  K.line(140, 55, 224, 55, "c-context", 2, 'stroke-linecap="round"') +
                  K.na_start(140, 55, "Listed Sep 2016")))
    T.append(tile("Null", "Cannot be computed. An em dash, never a zero — a zero is a finding.",
                  K.text(24, 58, "Dell", "c-ink", 12, "start", "sans", 500) + K.null_mark(88, 59) +
                  K.text(100, 58, "No 2010 price", "c-body", 11)))
    T.append(tile("Selected state", "A sighting ring, not a glow. Keyboard focus looks the same.",
                  K.series_line([(24, 76), (90, 56), (150, 60), (216, 40)], "c-story") +
                  K.data_dot(90, 56, "c-story") + K.selected_state(90, 56)))
    T.append(tile("Bar", "24px or thinner, 4px round at the data end, square at the baseline, 2px gaps.",
                  "".join(K.bar(40 + i * 26, 64 + i * 26, 92, 92 - hgt, "c-context")
                          for i, hgt in enumerate([30, 52, 70, 44])) +
                  K.bar(40 + 4 * 26, 64 + 4 * 26, 92, 92 - 18, "c-neg") +
                  K.line(30, 92, 200, 92, "c-axis")))
    prov = (K.text(24, 46, "n = 389 monthly returns", "c-ink", 11.5, "start", "mono") +
            K.text(24, 66, "Source: Yahoo Finance via matplotlib.", "c-body", 11.5) +
            K.text(24, 84, "Computed 27 Sep 2026.", "c-body", 11.5))
    T.append(tile("Provenance line", "n, source and date under every chart. No n, no chart.", prov))
    return "".join(T)


RULES = [
    ("The title is the finding.", "Not the topic. “S&P 500 returns” is a label; “Three months in 32 years fell past 3σ” is a chart."),
    ("One story series.", "Blue for the series the finding is about, grey for context. The palette cannot carry more identities than that — measured, §02."),
    ("Every chart states n.", "With the source and the date computed, in the provenance line. No n, no chart."),
    ("Every outlier states its test.", "Coral appears only with the rule that flagged it. Where a rule flags nothing, the chart says so — Fig. 04."),
    ("Name the rule, because rules disagree.", "|z| > 3 flags three months of S&P returns; a 3×IQR fence flags none. The choice is part of the finding."),
    ("Four data states, four drawings.", "Missing (hatch, broken line) · not applicable (capped start) · null (em dash) · structural empty (removed, counted in provenance)."),
    ("Never manufacture a gap.", "If the data has no missing values, the missing indicator appears in the key only. Fig. 02."),
    ("Dashed means threshold.", "Benchmarks, ±3σ, projections. Gridlines are always solid."),
    ("Text never wears a data colour.", "Labels are ink or body; the swatch beside them carries identity. Coral text fails contrast anyway."),
    ("Colour follows meaning, not sign.", "Negative red for a value that moved the bad way. Never mix status colours with identity colours in one chart."),
    ("One axis.", "Two scales on one plot invent a correlation. Index to a common base instead — Fig. 01."),
    ("Every chart has a table twin.", "Tooltips enhance, never gate. Every value is reachable in the table view."),
    ("Mono is for numerals and short labels.", "Tick values, n, measurements. Annotations are sentences, so they are sans."),
    ("Association, said as association.", "A fitted slope is not an effect. The dek says which it is."),
]


def rules_html():
    return "".join(f"<li><b>{K.esc(a)}</b> {K.esc(b)}</li>" for a, b in RULES)


# --------------------------------------------------------------- build ---
def main():
    tpl = read("template.html")
    css = type_css + "\n" + ui_css
    out = (tpl.replace("/*CSS*/", css)
              .replace("/*CHART_TOKENS*/", K.page_tokens())
              .replace("/*CHART_CLASSES*/", K.style_block(tokens=False))
              .replace("<!--FIGURES-->", "".join(figure_html(i + 1, fg) for i, fg in enumerate(FIGURES)))
              .replace("<!--VALIDATION-->", validation_html())
              .replace("<!--KIT-->", kit_html())
              .replace("<!--RULES-->", rules_html())
              .replace("<!--COMPUTED-->", COMPUTED))
    with open(os.path.join(HERE, "specimen.html"), "w", encoding="utf-8") as fh:
        fh.write(out)
    os.makedirs(os.path.join(HERE, "svg"), exist_ok=True)
    manifest = []
    for i, fg in enumerate(FIGURES):
        s = fg["svg"].replace('fill="none">', f'fill="none"><style>{K.style_block()}</style>', 1)
        name = f"fig{i+1:02d}-{fg['id']}.svg"
        with open(os.path.join(HERE, "svg", name), "w", encoding="utf-8") as fh:
            fh.write(s)
        manifest.append({"file": name, "title": fg["title"], "n": fg["n"], "source": fg["source"],
                         "check": json.loads(json.dumps(fg["check"], default=float))})
    with open(os.path.join(HERE, "figures.json"), "w", encoding="utf-8") as fh:
        json.dump({"computed": COMPUTED, "figures": manifest}, fh, indent=2, ensure_ascii=False)
    print(f"specimen.html — {len(out)//1024} KB · {len(FIGURES)} figures · svg/ ×{len(FIGURES)}")


if __name__ == "__main__":
    main()
