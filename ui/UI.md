# .describe( — UI language

**ROLE 07 deliverable.** The interface should feel like the instrument being
used, not like marketing collateral.

```
ui.css               the components — import this
icons.py             the icon generator (imports θ from geometry/)
icons/               17 icons as SVG · icons.json for build use
build_specimen.py    assembles specimen.html
template.html        the specimen source
specimen.html        the live component library — open it
UI.md                this file
```

```css
@import url('ui/ui.css');   /* pulls in type/typography.css itself */
```

Every class is prefixed `d-`. Every spacing and position uses logical
properties, so **`dir="rtl"` mirrors the whole kit with no per-component
overrides** — only directional icons need flipping, and that is one rule.

---

## 1. The colour law

UI is where it is most tempting to break it. A coral error message *looks*
right and means the wrong thing.

| | | |
|---|---|---|
| **Blue** | `--active` | Live, selected, in progress, the one primary action |
| **Coral** | `--mark` | A **data outlier**. Nowhere else — never an error, a warning or an accent |
| **Red** | `--neg` | A value that moved the bad way, or an action that failed |
| **Green** | `--pos` | A value that moved the good way, or an action that completed |

**Colour follows meaning, not the sign.** A return rate that falls 0.6 points
is a negative number and a good outcome — so it's green. A kit that coloured
by sign would paint it red. `.pos` and `.neg` are applied by whoever knows what
the number means, never computed from `< 0`.

---

## 2. Components

| | Rule that makes it this system's |
|---|---|
| **Buttons** | Not pills. Primary gets **calibration ticks** either side — one per view. Busy replaces the arrow with a counting tally. |
| **Focus** | A **sighting frame** — four corner brackets — not a glow. A transparent outline stays underneath so Windows High Contrast still draws a ring. |
| **Fields** | Boxed, thin rule, 2px radius. A unit sits *in* the field as a readout (`.d-affix`). Errors are written as the fix, not the fault. |
| **Radio** | Checked is a ring with a **positional dot** — the mark's own grammar. |
| **Switch** | An **index mark that travels a scale**, not a knob on a pill. |
| **Range** | A graduated scale with a sighting index for a thumb; readout in mono. |
| **Tabs** | A scale with a **pointer** that travels to the selected reading. Arrow keys work, and swap meaning in RTL. |
| **Tables** | Numbers mono and right-aligned; headers ≤4-word mono labels; **nulls shown as —, never 0**; a true minus sign; the outlier circled on its *value*, never deleted — the ring is coral, the number stays ink (coral text is 3.91:1); sort puts nulls last in both directions. |
| **Nav** | The current page carries an **index tick**, like a reading. Collapses behind a menu below 760px. |
| **Banners / toasts** | A toast's countdown is a **measurement sweep** along its bottom edge, and it pauses on hover. |
| **Panels** | Instrument plates: no shadow, no radius. `.d-panel--edge` adds a graduated measuring edge that moves to the right in Arabic. |
| **Readouts** | A figure read as a **statement** is serif (Fraunces). A figure read as **one measurement in a set** is mono. |
| **Loading** | Five states, never a spinner: **calibration, measurement sweep, tally, coordinate lock, data field.** Each has a resolved frame for reduced motion. |
| **Empty / error** | Honest sentences. No illustrations of absence. An error names what's wrong and exactly how to fix it. |

---

## 3. Conflicts resolved while building

**Buttons are not mono.** Brief §18 shows `[ RUN ANALYSIS → ]`, which reads as
mono. Your later direction — mono only for numerals and tiny labels — wins.
Labels are Readex Pro, uppercase and tracked in English; the technical feel
comes from the ticks and the directional mark. In Arabic there is no case and
no tracking, so weight carries it.

**Errors are never coral.** Failed actions use the negative red. Coral stays a
data word.

---

## 4. Bidirectional rules — found by testing, not assumed

Every one of these was a real defect in the first build, caught by switching
the specimen to Arabic.

1. **The interface sans is redefined, not just re-applied, in Arabic.**
   `type/typography.css` now sets `--font-sans: var(--font-ar-sans)` under
   `[dir="rtl"]`. Without it, every component asking for `var(--font-sans)`
   would render its Arabic in **Readex Pro's own Arabic glyphs** — Readex ships
   them — silently overriding the decision to use Vazirmatn for Arabic.

2. **Numbers are isolated as left-to-right.** Unicode's bidi algorithm treats a
   leading `+` or `−` as a neutral and, in an RTL paragraph, moves it to the far
   side: `+6.2%` rendered as `6.2%+` and `−4.8%` as `4.8%−`. Every numeric
   element is now `direction: ltr; unicode-bidi: isolate`. Wrap any other signed
   or unit-bearing figure in `.d-num`.

3. **Numbers align on the ones digit — physically right — in both directions.**
   Place value doesn't change with the language. The logical `end` would flip
   numeric columns to the left in Arabic and misalign the digits.

4. **Notification text takes its direction from its own content**
   (`unicode-bidi: plaintext`). Messages come from anywhere — a file name, an
   API error, a sentence in the other language — and an English sentence in an
   Arabic layout should keep its full stop at the end.

5. **A tick mark never mirrors.** The checkbox's check and the sort pointer use
   physical borders on purpose. A check is universal; an arrow is directional.

6. **Mono labels become Arabic sans in RTL** (IBM Plex Mono has no Arabic).
   Mono *numerals* stay mono — Western digits in both languages.

---

## 5. Open decisions — yours, not mine

1. **Warning has no colour.** The palette has none to give it, and coral would
   be the obvious grab and exactly the wrong one. Warnings are distinguished by
   **form** — an icon of a pointer arriving at a limit, and a heavier edge rule.
   If you want a colour, add one to the palette deliberately (an amber, say),
   and it becomes a system change, not a component tweak.

2. **Numeric alignment in Arabic tables.** Rule 4.3 follows from place value.
   Check it against what your Gulf readers actually expect — if their
   convention differs, it's a one-line change.

3. **Arabic strings on the specimen are drafts** for your review, not approved
   copy.

4. **The nav's wordmark is a stand-in** — `.describe(` set in IBM Plex Mono, the
   one place the kit knowingly breaks the mono budget. It stays until the real
   wordmark is drawn.

---

## 6. Icons

17 icons on a 24-grid, one stroke weight (1.5), round caps like the mark, drawn
from the same θ. The eight your brief specified: **search, data, report,
automation, decision, research, dataset, error.** Plus arrow, check, close,
chevron, plus, info, warning, orbit, menu.

Two were redrawn after testing at 20px:

- **Search** lost its crosshair centre — a cross inside a ring reads as *add*,
  the opposite of search. It's a dot now.
- **Error** became a proper ruler — broken, and its right half no longer lines
  up with the left. The first version read as brackets.

Directional icons (⇄ in the specimen) carry `.d-icon--dir` and flip in RTL:
arrow, automation, decision, research, search, warning.
