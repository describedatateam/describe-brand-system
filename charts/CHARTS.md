# Role 03 — Information design

Charts are where .describe( is judged. A client can forgive a plain website;
they cannot forgive a chart that overstates, hides its sample, or colours a
number to make a point it doesn't support. So this role is mostly rules,
and every rule is enforced by code where code can enforce it.

```
python3 charts/build.py          # recompute all six figures, rebuild specimen.html + svg/
python3 charts/examples.py       # print each figure's recomputed numbers (the check)
python3 charts/mpl/example.py    # the same furniture in matplotlib, for notebooks and PDFs
```

| File | What it is |
|---|---|
| `chartkit.py` | The furniture: scales, axes, marks, annotation, data states, provenance. Every chart is built from it. |
| `examples.py` | Six charts from real datasets. Loads, audits and recomputes from source every time. |
| `build.py`, `template.html` | Assemble `specimen.html` (hover layer, table twins, light/dark) and `svg/`. |
| `specimen.html` | The live reference. Open it; tab through any chart. |
| `svg/fig01…06.svg` | Standalone SVGs with their own light/dark tokens. |
| `figures.json` | Every figure's title, n, source and check numbers, for review diffs. |
| `mpl/` | `describe.mplstyle` + `mpl_describe.py`: the rules for matplotlib. |

---

## §1 The data

Nothing on the specimen is invented. All three datasets ship with the
libraries, so anyone can reproduce every number offline.

| Figure | Dataset | Source |
|---|---|---|
| 01, 02, 03, 06 | `Stocks.csv` — monthly closes for 10 series, 1990–2022 | Yahoo Finance, via matplotlib sample data |
| 04 | Diabetes — 442 patients, BMI and one-year progression | Efron, Hastie, Johnstone & Tibshirani (2004), via scikit-learn |
| 05 | Wine — 178 wines, three cultivars | Forina et al., PARVUS; UCI ML Repository, via scikit-learn |

**The audit is part of the load.** `load_stocks()` reconciles every blank
cell before anything is drawn, and asserts if they don't add up:

```
1,915 blank cells  =  1,330 structural (133 dated rows with no values — removed)
                   +    585 not applicable (Amazon, Alphabet, Dell before listing)
                   +      0 missing
```

It also drops one duplicate row (2022-06-28 repeats 2022-06-01 exactly),
leaving 390 month-start rows. That became Fig. 02, because *"1,915 blanks,
none missing"* is a finding a client would pay for.

---

## §2 Colour is emphasis, not category

Measured with the dataviz palette validator (OKLab ΔE×100; Machado 2009 CVD
simulation; floors ΔE 15 normal vision, ΔE 8 colour-blind):

| Pair | Mode | ΔE normal | ΔE CVD | |
|---|---|---|---|---|
| Story `#0F58E5` + context `#64748B` | Light | 18.7 | 16.9 | Pass |
| Navy + blue + grey as three categories | Light | — | — | **Fail** — navy L 0.26 reads as black |
| Story `#5B8DF0` + context `#676A70` | Dark | 19.8 | 19.3 | Pass |
| Story `#5B8DF0` + blue-grey `#7285A6` | Dark | 11.1 | 11.4 | **Fail** — shares the story's hue |
| Context + negative | Light / Dark | 22.0 / 21.1 | 16.6 / 10.2 | Pass |
| Context + coral marker | Light / Dark | 23.1 / 23.7 | 9.2 / 9.3 | Pass |

What that decides:

- **Blue is the story. Grey is context. Navy is ink, never data.** One story
  series per chart. The validator flags grey's low chroma every run; for an
  identity colour that's a failure, for context it's the job.
- **Dark-mode context is a neutral grey** (`#676A70`). Every blue-grey tried
  failed against the dark story blue.
- **More than one identity series** → small multiples. A true categorical
  palette would be a brand decision (an extension to the eight colours), not
  something a chart gets to improvise. `mpl_describe.story()` raises if you
  call it twice on one axes.

Text contrast (WCAG), which the validator doesn't cover:

- Dim ink was `#8A99B0` at **2.89:1**, failing everywhere it was used. It is
  now `#63738D`: 4.52:1 on the ground, 4.81:1 on panels. Fixed in `ui/ui.css`,
  `type/specimen.html`, `geometry/` and `site/`.
- Coral as text is **3.91:1** and fails. Coral is never text: the `.d-outlier`
  marker is coral, and its text is ink.

---

## §3 The furniture

The brief's §15 component list, all in `chartkit.py`:

x-axis · y-axis & grid · log scale · time scale · unit label · data dot ·
series line · confidence band · confidence interval · comparison bracket ·
outlier marker · annotation leader · measurement label · direct label ·
legend · reference rule · missing band · not-applicable start · null mark ·
selected state · bar · hit target · provenance line.

Fixed specs:

| | |
|---|---|
| Data line | 2px, round joins. `None` breaks the line — never interpolated across |
| Context line | 1.25px |
| Dot | r 4 (8px), filled, 2px surface ring |
| Bar | ≤ 24px thick, 4px round at the data end, square at the baseline, 2px gap |
| Grid, axes, leaders | 1px hairline, solid |
| Reference rule | 1.25px, dashed 4/4, ink |
| Confidence band | series hue at 12%, no edge |
| Tick labels, values, n | IBM Plex Mono (mono budget rule 01) |
| Unit labels | Mono, uppercase, ≤ 11px, ≤ 4 words (rule 02) |
| Annotations, names, deks | Readex Pro. Annotations are sentences |
| Chart titles | Fraunces 300. The title is the finding |

Labels that sit over rules carry a **surface halo** (`c-halo`: a 4px stroke
in the panel colour, `paint-order: stroke`), so a dashed benchmark breaks
behind the text instead of striking through it. Layer order matters: marks,
then rules, then labels.

---

## §4 The four data states

| State | Meaning | Drawn as |
|---|---|---|
| **Missing** | Should exist, doesn't | 45° hatch over the gap, line broken under it, the word MISSING |
| **Not applicable** | Didn't exist yet (a company before listing) | Nothing before it — not zero, not a gap. A cap at the start, labelled |
| **Null** | Can't be computed (no base period) | An em dash in dim ink. Never a zero — a zero is a finding |
| **Structural empty** | A row with no data at all | Removed, and counted in the provenance line |

**Never manufacture a gap to demonstrate the missing indicator.** If the
data has no missing values, the indicator appears in the key only, labelled
"none here". Fig. 02 does exactly this.

---

## §5 Outliers

Coral means a genuine outlier, and a point is only an outlier *under a
test*. So:

- `outlier_marker()` takes the rule; `mpl_describe.outlier()` raises without it.
- **Name the rule, because rules disagree.** On S&P 500 monthly returns,
  |z| > 3 flags three months (Aug 1998 −14.6%, Oct 2008 −16.9%, Mar 2020
  −12.5%); a 3×IQR fence flags none. The tails are fat. The choice of test is
  part of the finding, so it goes in the dek.
- **When a test flags nothing, say so.** Fig. 04's largest studentized
  residual is 2.65 — inside |t| > 3 — so nothing is coral, and the dek states
  that. An absent marker should never look like a forgotten one.
- The ±3σ lines are drawn as reference rules (dashed): they are thresholds.

---

## §6 Figures and hero numbers

- **Tabular figures only in columns** (tables, tick labels). A lone number —
  a stat tile, a readout — uses proportional figures. `.d-stat__value` was
  tabular; fixed in `ui/ui.css`.
- **Deliberate deviation from the dataviz method:** its guidance puts the
  hero number in the interface sans. .describe( sets stat-tile values in
  Fraunces 300, because the serif carries *meaning* in this system (Role 04)
  and a headline number is a statement. Chart readouts (Fig. 02) stay mono,
  under mono rule 01.

---

## §7 Interaction and access

- **Every chart has a table twin** holding every value. Per-figure toggle,
  plus a page-wide Charts/Tables switch. Tooltips enhance; they never gate.
- **Hover layer:** crosshair + all-series readout on line charts, per-bar
  targets on bars and bins (full band height, ≥ 24px), nearest-point within
  24px on scatter.
- **Keyboard:** bars, bins and outlier markers are focusable and show the
  same tooltip. Dense scatter dots are not — 442 tab stops is worse than
  none; the table serves the keyboard there.
- **Light and dark** are selected token sets (`page_tokens()`), each validated
  against its own surface. Standalone SVGs carry both via
  `prefers-color-scheme`.

---

## §8 Rules

1. **The title is the finding.** Not the topic.
2. **One story series.** Blue for what the finding is about; grey for context.
3. **Every chart states n**, its source, and the date computed. No n, no chart.
4. **Every outlier states its test.**
5. **Name the rule, because rules disagree.**
6. **Four data states, four drawings.**
7. **Never manufacture a gap.**
8. **Dashed means threshold** — benchmarks, ±3σ, projections. Gridlines are solid.
9. **Text never wears a data colour.**
10. **Colour follows meaning, not sign.** Never mix status and identity colours in one chart.
11. **One axis.** Index to a common base instead of a second scale.
12. **Every chart has a table twin.**
13. **Mono is for numerals and short labels.** Annotations are sans.
14. **Association, said as association.** A fitted slope is not an effect.

---

## §9 Open

- **Multi-series identity.** The palette supports one story series. If
  client work regularly needs three or four named series on one plot, that
  is a palette extension to decide at brand level, then validate.
- **Fonts in the matplotlib bridge.** It falls back to DejaVu unless
  Readex Pro, Fraunces and IBM Plex Mono are installed locally.
- **Arabic charts.** Not built yet. Numbers stay LTR and right-aligned (Role 07
  §4); axis direction in RTL layouts is an open design question — time
  usually still runs left to right in Arabic financial charts, but that
  should be confirmed with the audience.
