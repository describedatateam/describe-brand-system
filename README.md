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
| `brandkit/logo/` | The locked 5a mark: ten production variants, the generator, and a QA script |
| `geometry/` | **Role 02** — the primitive library. Generator, 46 SVG plates, 92 PNGs, derivation notes |
| `type/` | **Role 04** — typography. Tokens, written rules, and a specimen that measures its own decisions |
| `specs/logo/` | The logo master spec and the open questions against it |
| `previews/logo/` | Rendered preview sheet |
| `wordmark/` | The wordmark study — direction A, awaiting approval (`wordmark/README.md`) |
| `ui/` | **Role 07** — interface components, icons and their specimen. Rules in `ui/UI.md` |
| `charts/` | **Role 03** — chart kit: SVG and matplotlib styles, worked figures. Rules in `charts/CHARTS.md` |
| `illustrations/` | The illustration layer (`illustrations/ILLUSTRATION.md`) |
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
- **The wordmark is a study, not approved.** `wordmark/` holds direction A;
  until it is signed off, lockups remain provisional.
- **The proof figures are recomputed from the canonical UCI file** by
  `decisions/uci_retail.py` (→ `uci_audit.json`), and `site/index.html` uses
  them. `site/proof/` is the separate audit of the May 2026 deck, which was
  built on the Kaggle copy — use its correction table when revising the deck.
- **Dark-mode blue is three different values.** `ui/ui.css` uses `#5B8DF0`,
  the logo generator's dark tier uses `#5B93FF` (`specs/logo/open-questions.md` Q2,
  still awaiting approval), and `geometry/astrolabe.py` and the wordmark's dark
  files use `#4F86F7`. Pick one and set it in all three places.
- **Service 02 has no price.** The "when to pick this" text was pasted into the
  price field.

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
