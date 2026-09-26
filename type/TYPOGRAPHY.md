# .describe( — typography

**ROLE 04 deliverable.** The faces, the scale, the role split, and the
bilingual rules.

```
typography.css   the tokens — import this, don't retype sizes
specimen.html    the live test; re-run it on any machine
TYPOGRAPHY.md    this file
```

---

## 1. How these were decided

Your brief cut Bodoni Moda for a stated reason: its hairlines break at working
sizes on dark backgrounds. That is a **test**, not a preference — so the same
test decided everything below, and `specimen.html` runs it live rather than
asking you to take my word for it.

The method: draw the letter `o` to a canvas at each real working size, find
the thinnest stroke, and measure it in device pixels. Below about **1 device
pixel** a hairline stops being a line and becomes a grey smear — and
light-on-dark loses it first, because antialiasing has less to work with.

Two details that make the measurement honest rather than decorative:

- **Sub-pixel resolution.** The raster is drawn at 8×, but the text is laid
  out at its real size. Measuring at 8× the *font-size* would quietly thin a
  variable font by pushing its optical-size axis, which would have rigged the
  result in Fraunces's favour.
- **A font-load guard.** `document.fonts.check()` answers `true` for fonts
  that never arrived, because it resolves through the fallback. The specimen
  measures a probe string's width instead, and if a face is missing it
  **switches the table off** rather than reporting the fallback serif's
  measurements under another name. If you open the page offline you will see
  the guard fire — that is it working.

---

## 2. Latin display — Fraunces

Set at **weight 300** with `'SOFT' 0, 'WONK' 0`.

| | |
|---|---|
| **Why** | It has an optical-size axis (`opsz 9–144`) that thickens hairlines automatically as size drops. That is the Bodoni failure mode solved in the font rather than patched in CSS. |
| **Range** | Prata ships one weight, 400, no italic. Your system needs 88px display and 15px labels out of one family. Prata gives you nothing to recover with when a size goes weak. |
| **The trendiness problem** | Fraunces is everywhere — almost always with SOFT and WONK turned up, which is what makes it read friendly-retro. At `'SOFT' 0, 'WONK' 0` and weight 200–300 it is severe and high-contrast, and very few people use it that way. |

**Prata is kept**, restricted to display-only moments where nothing sits below
40px — a report cover, a poster. It is the better face at that one job. The
`.t-alt` class enforces the floor with `font-size: max(40px, 1em)`.

> ⚠️ Never name `'opsz'` inside `font-variation-settings`. Naming an axis pins
> it, which disables automatic optical sizing — the whole reason this face was
> chosen. Name only `SOFT` and `WONK`.

---

## 3. Arabic display — Amiri, with Reem Kufi for labels

**Amiri** for headings:

- It is a Naskh revival with real thick–thin modulation, so it sits beside a
  high-contrast Latin serif as the same idea rather than a substitute for it.
- It revives the Bulaq Press types — nineteenth-century Egyptian printing.
  Your brief wants Al-Khwarizmi as written lineage rather than portraiture;
  this is that, as a typeface.

**Reem Kufi** for short labels, section markers and tally captions. It is
geometric Kufi — built from circles and straight lines, the same
compass-and-rule construction the astrolabe mark uses. Too rigid for running
headlines, exactly right for a four-word label.

**El Messiri: not taken.** A good contemporary low-contrast humanist, and the
wrong one here — beside Fraunces at 300 it reads as a softer, different brand,
and it carries none of the archival quality the rest of the system rests on.
If the identity ever moves away from high-contrast serif, it becomes the right
answer.

### The one number you still owe this file

`--ar-scale` in `typography.css` is currently **1.30, a placeholder, not a
measurement.** Open `specimen.html` on a machine where the fonts load, read
the measured multiplier off section 02, and replace it. Until then Arabic
headings will be approximately right rather than right.

---

## 4. The scale

Base 16, ratio ≈1.32, seven steps. A size not in this list does not exist.

| Token | Size / leading | Used for |
|---|---|---|
| `--t-display` | 88 / 0.95 | Hero, report cover |
| `--t-opener` | 56 / 1.00 | Section opener |
| `--t-h2` | 40 / 1.06 | Section heading |
| `--t-h3` | 28 / 1.14 | Sub-heading, pull quote |
| `--t-lede` | 21 / 1.50 | Standfirst |
| `--t-body` | 16 / 1.62 | Running text |
| `--t-meta` | 11 / 1.40 | Metadata, axis labels, source lines |

---

## 4b. The interface faces — split by script

**Readex Pro for Latin. Vazirmatn for Arabic.**

I originally argued for one family covering both scripts, on coherence
grounds. Wafa'a reads Arabic daily and judged Vazirmatn's Arabic better, which
settles it: coherence is not worth buying at the cost of the script half the
market reads. Splitting is normal in bilingual systems — Latin and Arabic are
constructed differently enough that one designer rarely does both equally
well.

**A split is only safe if it is matched.** Two families at the same nominal
weight are almost never the same optical weight, and Arabic sets smaller at
the same `font-size`. `specimen.html` §04 measures both joins:

- **Optical size** — Latin x-height against Arabic body height, giving
  `--ar-body-scale`.
- **Stroke weight** — the stem of Latin `l` against Arabic alef `ا`. Both are
  a plain vertical stroke, so they are directly comparable; if one is thicker,
  Arabic at 400 will read bolder than Latin at 400 and the page will feel
  lopsided. The table says which way to step `--ar-w-body`.

Both tokens in `typography.css` are **placeholders until you read the measured
values off the specimen** on a machine where the fonts load.

### One thing to check with your own eyes

Vazirmatn is Persian-first. Persian and Arabic share the script but part
company on a few letters — **kaf and yeh above all** (`ك ي` against `ک ی`).
The specimen sets both forms side by side in each face, plus the Persian-only
letters. If the kaf or yeh read as Persian to you in running Arabic copy, say
so and we pick again. That judgement is yours.

### One consequence of splitting

Arabic no longer comes from the Latin family, so the Arabic-coverage
constraint that ruled out Geist, Inter, Manrope and the other Latin-only
grotesques no longer binds the Latin slot. Readex Pro stays unless you want to
revisit it.

---

## 4c. How the interface face was chosen

*Kept for the record — this is the shortlist the two choices came from.*

The interface face carries almost every word on every surface, so it has to be
clean enough to disappear. The shortlist was originally filtered on **Arabic
coverage in the same family**, which is why Geist, Inter, Manrope, Figtree,
Instrument Sans, Schibsted and Host Grotesk are absent: all Latin-only.

That filter no longer binds, since the decision above split the slot by
script. It still shaped the list, and every face below remains a legitimate
option for either half.

**What Hermes actually uses**, inspected directly rather than guessed: their
interface runs on **Rules Variable** at weights 400–500, 13–16px — a
commercial Swiss grotesque. Display is Rules Gothic Condensed. Part of what
reads as quality there is simply paid-for type; Rules has no Arabic and isn't
free.

Free faces that do carry Arabic in one family, all verified on Google Fonts:

| Face | Character |
|---|---|
| **Readex Pro** — chosen for Latin | Low contrast, soft terminals. Quiet enough to sit under Fraunces. |
| Rubik | Literally rounded corners — closest to "rounded". Warmer, more startup-ish. |
| **Vazirmatn** — chosen for Arabic | The most neutral; closest free analogue to the Swiss grotesque register. |
| Alexandria | Geometric, even. |
| Cairo | Gulf-familiar; Latin is the weaker half. |
| IBM Plex Sans Arabic | The previous choice. Not wrong, just technical — Plex is IBM's engineering voice, which reads as machinery rather than craft. |

`--font-sans` and `--font-ar-sans` in `typography.css` hold the two choices.
The serif and the mono are unaffected either way.

---

## 5. Three faces, three jobs

| | Face | Job |
|---|---|---|
| **Serif** | Fraunces | **Meaning.** Statements, concepts, the sentence you want remembered. |
| **Sans** | IBM Plex Sans Arabic | **Explanation.** Body, interface, labels, navigation. |
| **Mono** | IBM Plex Mono | **Measurement.** Numbers, units, metadata, axes, coordinates. |

### The mono budget

Your brief says never let the mono become the personality of the brand. **The
homepage draft broke that badly** — every eyebrow, nav link, button, section
kicker and caption was mono, which is exactly how a supporting face quietly
becomes the voice. Three hard limits, so it's checkable rather than a matter
of taste:

1. **Numerals — mono at any size.** Tables, prices, chart values, `n =`
   counts. Always tabular. This is what mono is for.
2. **Labels — mono only at ≤11px, uppercase, four words or fewer.** Axis
   labels, source lines, figure numbers, units. One per *region* of a
   composition, not one per element.
3. **Everything else — never.** Nav, buttons, eyebrows, section kickers, form
   labels, captions, body. All interface sans.

**The test: if a run of mono reads as a phrase, it's the wrong face.**

`.t-label` enforces limit 2 structurally with `font-size: min(11px, …)` — the
class can't be used bigger by accident. Metadata longer than four words takes
`.t-meta`, which is now the **sans** at 12.5px, not mono.

Benchmark: Hermes never sets mono above 11px and never inside a sentence.

### The gap that bites at launch

**IBM Plex Mono has no Arabic.** Every `n =` line, chart label, source credit
and timestamp in the Arabic system has no mono to fall back to. The browser
will silently substitute Arabic glyphs from some other face into a mono run,
and it looks broken.

The rule, already in `typography.css`: Arabic metadata uses **IBM Plex Sans
Arabic at 400, tabular figures, no tracking, no uppercase transform.**

---

## 6. Bilingual rules

1. **Never letter-space Arabic.** Latin labels take `letter-spacing: .14em`.
   Applying that to Arabic breaks the joins between letters and turns a word
   into debris. The Arabic equivalent of a spaced uppercase label is a weight
   change.
2. **Never synthesise bold.** `font-synthesis: none` is set for Arabic. A
   faked bold smears the joins. Use a weight the family actually ships.
3. **Arabic needs more leading.** Body `1.85` against the English `1.62`;
   headings `1.50` against `1.06`. Ascenders, descenders and diacritics stack
   further.
4. **Apply the measured multiplier**, per face, from the token — not by eye.
5. **Western digits in both languages.** `0123`, not `٠١٢٣`. Gulf business
   context expects them, and it keeps every figure in the system on one set of
   numerals, which matters more for a data practice than for most brands. A
   market that expects Eastern Arabic-Indic is a per-piece override, never a
   system change.
6. **Mirror the spine, not just the text.** The measuring edge moves to the
   right margin, its ticks point inward from the right, the mark moves with
   it, and every arc and pointer flips handedness. `direction: rtl` alone
   leaves the geometry facing the wrong way — see `astrolabe.py`, where the
   sight axis θ is the one value to negate.
7. **One language per piece.** Already your rule: posts are single-language. A
   split canvas makes each half look like a caption for the other.

---

## 7. What this unblocks, and what it doesn't

With the scale and the role split fixed, **Role 07 (UI language)** can start —
buttons, inputs, tables, nav and states all key off these tokens.

It does **not** unblock the website. That still needs the wordmark: `.describe(|`
drawn as letterforms rather than set in IBM Plex Mono as a stand-in, which is
what the homepage draft is currently doing.
