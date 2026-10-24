# .describe( — brand system

The visual identity of **.describe(**, a data analytics and business
intelligence practice, built as code rather than as a folder of exported
pictures.

Everything here derives from one angle.

```
θ = −40.6°     the sight axis
R = 86         ring radius, on a 200-unit canvas centred at (100,100)
κ = 0.4884     the tangent ratio, r/R = 42/86
gap = 28°      the aperture, centred on θ
```

Fix θ and the rest of the mark is forced: the star sits on the ring at θ, the
positional dot at θ+180°, the inner bowl is internally tangent **exactly at
that dot**, the ring's aperture opens on θ, and the star's eight arms are
phased so one lies along it. Change θ and the whole mark rotates coherently.

That is not a description of the logo. It is the grammar the entire system is
generated from — which is why a chart axis, a loading state and a section
marker all read as the same instrument.

---

## Layout

| Path | What it is |
|---|---|
| `tokens/` | **The design tokens**: one JSON source, generated CSS and JSON, the checks, and the reference (`tokens/TOKENS.md`). See *Design tokens* below |
| `brandkit/logo/` | The locked 5a mark: ten production variants, the generator, and a QA script |
| `geometry/` | **Role 02** — the primitive library. Generator, 46 SVG plates, 92 PNGs, derivation notes |
| `type/` | **Role 04** — typography. Tokens, written rules, and a specimen that measures its own decisions |
| `specs/logo/` | The logo master spec and the open questions against it |
| `previews/logo/` | Rendered preview sheet |
| `wordmark/` | The approved wordmark, direction A: masters, lockups, and web-ready SVGs in `wordmark/web/` (`wordmark/README.md`) |
| `ui/` | **Role 07** — interface components, icons and their specimen. Rules in `ui/UI.md` |
| `charts/` | **Role 03** — chart kit: SVG and matplotlib styles, worked figures. Rules in `charts/CHARTS.md` |
| `illustrations/` | The illustration layer (`illustrations/ILLUSTRATION.md`) |
| `templates/` | **The enrichment layer**: construction backdrops, measuring edge, tally, orbit fill, data cells, gauge, dither, illustration masks and callouts, shared by the slide and social templates. Rules in `templates/ENRICHMENT.md` |
| `slides/` | The 16:9 slide template: eight layouts (title, section, big number, chart, outliers, method, statement, close). `python3 slides/build.py --render` |
| `social/templates/` | The social templates: a 4:5 carousel whose cards double as single posts, plus 1:1 and 9:16. `python3 social/templates/build.py --render` |
| `decisions/` | Scripts and evidence behind specific decisions — the UCI audit, Arabic sizing sheets, the warning-colour options (`warning.html`), and the brand fonts used by the screenshot checks (`fonts/`) |
| `website/` | The approved homepage design: content brief (`content-brief.html`), design briefs, build script, checks, critiques, and the handoff prompt. The live site is built from this in its own repo, `describedatateam/website`, and runs at https://describe.team |
| `site/` | The earlier homepage draft. **Not a deliverable** — see the warning below |
| `Logo Design With Astrolabe Inspiration (2)/` | The original exploration exports, kept for provenance |

---

## The two libraries

### `geometry/` — the primitive vocabulary

Run `python3 astrolabe.py` to regenerate the SVGs, then `python3 render_png.py`
for the rasters (`python3 render_png.py 2048` for print). Import it to build
anything else:

```python
from astrolabe import broken_ring, radial_scale, tally, polar, THETA, R
```

46 plates across eight families: arcs, measurement, orientation, instrument
details, construction geometry, data, tallies, and the orbit motif. Read
`geometry/PRIMITIVES.md` first.

**Three rules are guards in the code, not notes in a document:**

- `radial_scale()` raises on a sweep of 330° or more. Uniform graduation all
  the way round reads as a clock; a graduated *sector* reads as an instrument.
- `broken_ring()` raises on a zero gap. A closed ring is not part of the
  vocabulary.
- Nothing reaches for coral on its own. `data_series()` takes an explicit list
  of outlier indices, so coral is always a judgement someone made about the
  data — never an automatic rule, never decoration.

### `type/` — the typographic system

```css
@import url('type/typography.css');
```

| Role | Face | Job |
|---|---|---|
| Serif | Fraunces, weight 300, `'SOFT' 0, 'WONK' 0` | Meaning — headlines, statements |
| Sans (Latin) | Readex Pro | Explanation — body, interface |
| Sans (Arabic) | Vazirmatn | The same, in Arabic |
| Arabic display | Amiri; Reem Kufi for labels | Headings, section markers |
| Mono | IBM Plex Mono | Measurement — numerals and short labels only |

`type/specimen.html` is not a specimen sheet. It **runs the decisions** in your
browser: it rasterises each candidate at real working sizes, measures the
thinnest stroke in sub-pixel units, and reports whether a hairline survives.
Open it and the numbers are recomputed on your machine.

Two details that make that honest rather than decorative:

- The raster is drawn at 8× while the text is laid out at its **real** size.
  Measuring at 8× the font-size would push a variable font's optical-size axis
  and quietly thin it, rigging the comparison.
- `document.fonts.check()` returns `true` for fonts that never arrived,
  because it resolves through the fallback. The page probes text width
  instead, and if a face is missing it **switches the table off** rather than
  reporting the fallback's measurements under another name.

#### The mono budget

Mono is ornament, not text. Three limits:

1. **Numerals** — any size. Tables, prices, chart values, `n =` counts.
2. **Labels** — ≤11px, uppercase, four words or fewer. One per region.
3. **Everything else** — never. Nav, buttons, eyebrows, kickers, form labels,
   captions, body.

The test: *if a run of mono reads as a phrase, it is the wrong face.*
`.t-label` enforces limit 2 structurally with `font-size: min(11px, …)`.

---

## Known open items

- **The Arabic size and weight tokens are measured but the choice inside the
  bracket is a visual one.** `--ar-scale: 1.15`, `--ar-body-scale: 1.20` and
  `--ar-w-body: 300` come from `type/specimen.html` §02 and §04 (see
  `type/TYPOGRAPHY.md`). The page brackets each multiplier and the value was
  picked by eye at working size — worth a look from someone who reads Arabic
  daily before it is locked.
- **The Arabic site copy is written and awaiting the founder's read.**
  `website/arabic/` holds every line of the homepage, store profit check and privacy
  page in Arabic (`ar-copy.json`, review page `review.html`); the build spec for the
  coding agent is `website/HANDOFF_AR_LOGO.md`.
- **The proof figures are recomputed from the canonical UCI file** by
  `decisions/uci_retail.py` (→ `uci_audit.json`), and `site/index.html` uses
  them. `site/proof/` is the separate audit of the May 2026 deck, which was
  built on the Kaggle copy — use its correction table when revising the deck.
- **Dark-mode blue is three different values.** The tokens, `ui/ui.css`, the charts
  and the live site use `#5B8DF0`; the logo generator's dark tier uses `#5B93FF`
  (`specs/logo/open-questions.md` Q2, still awaiting approval); `geometry/astrolabe.py`,
  the wordmark's dark files and the October LinkedIn posts use `#4F86F7`. The token is
  `#5B8DF0` because it is the one validated against the dark chart context grey.
  Approve it (or another) and regenerate the logo, wordmark and geometry from it.
  `python3 tokens/check.py --audit` lists every off-token hex left in the repo.
- **Warning still has no colour.** The tokens follow `ui/UI.md` §5: warning is form
  only. `decisions/warning.html` shows the amber option; adding it is one token.
- **Service 02 has no price.** The "when to pick this" text was pasted into the
  price field.

---

## Design tokens

Every colour, size, space, stroke and timing the system uses lives in **one file**,
`tokens/tokens.json` (W3C design-token format). Everything else is generated from it
or checked against it.

```
python3 tokens/build.py     # writes tokens/dist/tokens.css, tokens/dist/tokens.json, tokens/TOKENS.md
python3 tokens/check.py     # contrast, palette and drift checks; CI runs both on every push
```

| Output | For |
|---|---|
| `tokens/dist/tokens.css` | Anything in a browser: website, data apps, HTML reports, HTML-rendered social posts |
| `tokens/dist/tokens.json` | Code that is not CSS: Python (matplotlib, Plotly, Streamlit), JS charting, Figma plugins. Flat: each token has `light`, `dark` and its `css` name |
| `tokens/TOKENS.md` | People: every value, its job and its measured contrast |
| `tokens/palette.png` | Picking colours by eye in Canva, Slides or Figma (`python3 tokens/render_palette.py`) |

To change a value: edit `tokens.json`, run both scripts, commit all of it. `check.py`
fails if a colour breaks contrast or the palette rules, or if `ui/ui.css`,
`type/typography.css`, `charts/chartkit.py` or `charts/mpl/mpl_describe.py` no longer
carry the token value.

### What the colour tokens are for

| Job | Tokens | Rule |
|---|---|---|
| Ground and plates | `--ground`, `--panel`, `--field` | Off-white page, white plates. Dark mode is its own set, not an inversion |
| Text | `--ink`, `--body`, `--dim` | Every text token clears 4.5:1 on every surface in both modes |
| Live / primary action | `--active` | Blue. One primary action per view |
| Outlier | `--mark` | Coral, under a named test. Never text, never an error |
| Good / bad movement | `--pos`, `--neg` | By meaning, not by sign |
| One story in a chart | `--viz-story`, `--viz-context` | **The default chart.** Blue for the finding, grey for everything else |
| Several named series, none the story | `--viz-cat-1` … `--viz-cat-6` | Blue, verdigris, brass, plum, moss, sky, **in that order**. Lines, bars, stacks: up to six. Scatter, maps, small multiples: first three only. More → fold into Other or facet |
| Magnitude | `--viz-seq-step-1` … `-7` (blue), `--viz-seq-alt-step-*` (brass) | Step 1 is near zero. The steps flip in dark mode so small values recede |
| Above / below a meaningful zero | `--viz-div-n5` … `--viz-div-0` … `--viz-div-p5` | Brass below, blue above, neutral grey at zero. Polarity, not good/bad |

The categorical, sequential and diverging palettes are new with the tokens. They extend
the palette (charts/CHARTS.md §9 left multi-series open) without touching the eight
brand colours, and exclude coral, red and green so an outlier or a status never
looks like a series. Their checks: OKLab ΔE ≥ 8 between neighbours under protanopia
and deuteranopia simulation (worst pair 13.5 light, 14.0 dark), ≥ 15 under normal
vision, ≥ 3:1 against the chart surface, and every slot ≥ 15 from coral.

### By medium

The type scale is one set of ratios (display 5.5×, opener 3.5×, h2 2.5×, h3 1.75×,
lede 1.31×, meta 0.69× of body). Each medium sets its own body size; spacing scales
with it. Set `data-medium` on the root of an HTML page and every `--t-*` re-bases.

| Medium | Base | Display / H2 / Body / Meta | How |
|---|---|---|---|
| **Website** | 16px | 88 / 40 / 16 / 11 px | `@import url('tokens/dist/tokens.css')`; `ui/ui.css` uses the same names. Theme follows the OS unless `data-theme` is set |
| **Data apps** | 16px | as web | HTML/React: the CSS file. Python apps: read `tokens/dist/tokens.json` (below). Light and dark both supported; never invent a series colour |
| **Slides** (1920×1080) | 28px | 154 / 70 / 28 / 19 px | `data-medium="slides"`. In PowerPoint, Keynote or Google Slides set the theme to: Dark 1 `#092052`, Light 1 `#F6F8FC`, Dark 2 `#5A6B85`, Light 2 `#CBD5E1`, Accents 1–6 = categorical 1–6, hyperlink `#0F58E5`. The six theme accents are the six categorical slots, in order |
| **Social** (1080×1350, 1080×1080) | 32px | 176 / 80 / 32 / 22 px | `data-medium="social"`. Matches the October 2026 LinkedIn set (headlines 80–110, labels 22). Dark posts use the dark tokens: `--active` `#5B8DF0`, `--dim` `#788BAC` |
| **Reports** (A4, PDF) | 10pt | 55 / 25 / 10 / 7 pt | `data-medium="report"`, light mode only: ink on white panels. Charts from `charts/mpl/` already carry the token colours |

The mono budget scales with the medium: a mono label is at most the medium's
`--t-meta` (11px on the web, 22px on social), uppercase, four words or fewer.

For Canva, add the eight brand colours plus the six categorical colours to the brand
kit, in the order above, and set headings in Fraunces Light, body in Readex Pro.

```python
import json
T = json.load(open("tokens/dist/tokens.json"))["tokens"]
c = lambda key, mode="light": T[key][mode]

story, context = c("color.viz.story"), c("color.viz.context")
categorical = [c(f"color.viz.cat.{i}") for i in range(1, 7)]

# Plotly: fig.update_layout(colorway=categorical)
# matplotlib: plt.rcParams["axes.prop_cycle"] = plt.cycler(color=categorical)
# Streamlit .streamlit/config.toml: primaryColor = c("color.role.active"),
#   backgroundColor = c("color.surface.ground"), textColor = c("color.text.ink")
```

---

## Design test

Before approving any asset:

1. Could this belong to a generic AI startup? → if yes, redesign.
2. Is there a real relationship to measurement, information, orientation,
   computation or knowledge? → if no, remove it.
3. Does it use the vocabulary **without drawing an astrolabe**? → if yes, good.
4. Is coral saying something? → if no, remove it.
5. Would it still read as .describe( with the logo removed? → if no, the system
   is too logo-dependent.
6. Does it survive in one colour? → set all five inks to the same value.
7. Is the information still clear with the decorative layer gone? → delete
   every `faint` element and check.

Tests 6 and 7 are mechanical with these libraries, which is most of why they
exist.

---

## Palette

| | Hex | Role |
|---|---|---|
| Navy | `#092052` | Structure, typography, dark surfaces |
| Bright blue | `#0F58E5` | Active, computational, directional |
| Coral | `#E5484D` | **Genuine outliers only** |
| Grey | `#64748B` | Instrument body — does most of the work |
| Light grey | `#CBD5E1` | Construction, grids, inactive |
| Off-white | `#F6F8FC` | Light ground |
| Deep red | `#8C1D1D` | Negative values only |
| Green | `#0F7B3D` | Positive deltas only |

Dark mode is a separate environment, not an inversion.

---

See `NOTICE.md` for rights.
