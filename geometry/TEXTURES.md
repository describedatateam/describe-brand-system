# .describe( — textures

Five fields that are not clean lines: a one-bit dither, a halftone, two ring
sets, a line field and a bitmap crescent. They give the website and the posts
a surface with a vibe, and every one of them is a measurement drawn as a field.

```
geometry/textures.py        the generator (SVG strings, token classes, no typed colour)
geometry/textures/          textures.css, light and dark SVG files, textures.html (the specimen)
```

`python3 geometry/textures.py` rebuilds the folder. Open `textures/textures.html`
for the set on paper, navy and cobalt, with the signal band animating in.

## The five

| Texture | Reads as | Binds to | Marked thing | Use it for |
|---|---|---|---|---|
| `signal(values, w, h, label=)` | Signal and noise: solid where the data is dense, dissolving where it thins | one column per value | the tallest column's top cell, with the star above it | a divider or hero band; a footer rule |
| `halftone(w, h, measure=)` | Dots sized by a measure, bent toward the largest | dot size = `measure` | the one active disc | a cover or section background |
| `rings(w, h, a=, b=)` | Two datasets and where they overlap | one ring set each | the active ring and the star at the overlap | a card header, a feature image |
| `waves(w, h, label=)` | One series among many | one line per series | the story line, a long active tick on the edge, the star at its crest | a page header |
| `crescent(w, h, label=)` | Eid and occasions, in cells | none: it is the occasion motif | the star in the opening | a seasonal banner, a greeting |

Each returns an inline `<svg class="tx tx--<name>">`. `label` (or `measure`, `a`
and `b`) becomes the SVG's accessible name; the guards refuse an empty one.

## Rules

1. **Bound to a measurement.** `signal()` refuses empty, flat or negative values;
   there is no default pattern. Say what the field measures.
2. **One marked thing.** One star, one active line, one active ring or one focus
   disc. Never a second. (`templates/check.py` counts them.)
3. **ink, body, dim, faint paint the field; active marks.** Coral never appears
   (a `mark` tone raises). The wave steps are five discrete greys (`s1`..`s5`),
   not an opacity ramp.
4. **One-bit or stepped, never smooth.** The dissolve is an 8×8 Bayer dither;
   there is no gradient or glow inside a drawing. The two `tx-clear-*` helpers fade
   a whole field out under type with a mask, the same device as `fade-up`.
5. **Never behind a chart, a table or body text.** Hero bands sit beside the
   headline, not under it.
6. Delete the texture and the page still reads (design test 7).

## On the website

```html
<link rel="stylesheet" href="tokens/dist/tokens.css">
<link rel="stylesheet" href="geometry/textures/textures.css">

<!-- a hero band: headline, then the field -->
<header class="hero">
  <h1>Signal, <em>then noise.</em></h1>
  <!-- inline the SVG that TX.signal(values, 1440, 360, label="...", reveal=True) returned -->
</header>

<!-- the same drawing on the brand blue -->
<section class="on-cobalt"> … </section>
```

```python
import sys; sys.path.insert(0, "geometry")
import textures as TX
svg = TX.signal(weekly_orders, 1440, 360, label="Weekly orders, last 72 weeks", reveal=True)
```

Inline the SVG (an `<img>` cannot read the page's tokens). The classes read
`--ink`, `--body`, `--dim`, `--faint` and `--active`, so a texture follows the
light and dark environments and the `.on-cobalt` ground without a second drawing.
Use the `texture-*-light.svg` and `-dark.svg` files only where CSS variables are
not available (email, slides, Figma).

**Reveal.** Add `reveal=True` for the optional entrance: signal columns rise in,
wave lines draw in, the star lands last. One curve (`--ease`), no overshoot,
and nothing animates under `prefers-reduced-motion`, which shows the finished frame.

**Backgrounds.** Give the SVG `tx--bg` inside a `position:relative` parent and
keep the headline on its own side (`tx-clear-left` fades the field under it).

## On social

`social/templates/occasions.py` has five posts built from the set: Dither,
Halftone, Interference, Line field and the cell crescent for Eid. Copy is
placeholder and each says `Template` until the values are real.
