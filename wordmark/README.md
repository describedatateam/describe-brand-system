# .describe( wordmark — direction A, approved

Direction A, "constructed": a lowercase monoline wordmark built from the 5a mark's own parts.
- Bowls (d, e, c, b) are one circle, the size of the mark's bowl in the lockup.
- The e's bar is the bowl's horizontal diameter (the mark's sighting rule).
- Openings and terminals follow the sight angle θ = 40.6°.
- The blue caret is the mark's stem: `.describe(|`, 1.4× the letter stroke.
- Ascenders are 1.74× the x-height, the mark's stem-to-bowl proportion.

Tiers: primary (letter stroke 10, x-height 100) for ≥48px ink height; compact (stroke 15) for ≥20px.
Below 20px use the mark alone. Clear space: one x-height on every side.

Approved by Wafa'a Al-Hayek, October 2026.

For the website use `web/`: the same artwork with tight viewBoxes and colours as CSS
variables (`--wm-ink`, `--wm-accent`, with brand fallbacks), so an inline SVG follows
the page theme. Nav: `web/lockup-compact.svg` at 34px tall (30px on phones). Footer:
`web/lockup-primary.svg` at 64px (48px on phones).

Build: `python3 build_wordmark.py` (needs fontTools; the B/C alternates need static instances
readex300.ttf / fraunces300.ttf made from decisions/fonts with fontTools.varLib.instancer).
Study page: `python3 build_study.py` → study.html.
