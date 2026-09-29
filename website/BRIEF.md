# .describe( homepage — design brief for the designer and the critic

## The job

Build the .describe( homepage as ONE complete, self-contained page:
`/home/claude/website/site.html`.

Merge two existing pieces:
- **Content and structure** from the old draft `/home/claude/repo/site/index.html`
  (hero, who we help + who we're not for, three services, five-stage method,
  worked-example proof, "where we are", About, questions/FAQ, contact form, footer).
  Keep the copy; tighten it where it's long. Its proof figures were recomputed
  today and are correct (source of truth: `/home/claude/decisions/uci_audit.json`).
- **Look** from the illustration mock `/home/claude/illustrations/web/fixed-stars.html`
  (light dithered-sky hero, 1-bit al-Sufi illustrations coloured by tokens, the
  finished UI kit and type system).

## Who it's for

A hands-on CEO of a 2–10 person company that already generates data but has
nobody whose job it is to read it. .describe( is a new data-analytics practice
founded by Wafa'a Al-Hayek, working from Gaza. No completed commercial
projects yet, and the page says so openly.

## Output format (hard requirements)

- `site.html` is published as a claude.ai Artifact: **no `<!doctype>`, `<html>`,
  `<head>` or `<body>` tags**. Start with `<title>…</title>` then `<style>`.
- Everything inline: CSS, JS, images as `data:` URIs. External stylesheets only
  from fonts.googleapis.com (the CSS files already @import Google Fonts).
  Scripts only from cdnjs if truly needed (it shouldn't be).
- Inline `/home/claude/type/typography.css` and `/home/claude/ui/ui.css`
  (strip ui.css's `@import url('../type/typography.css')` line). Reuse `d-`
  components rather than restyling from scratch.
- Theme: tokens on bare `:root` (light), redefined under
  `@media (prefers-color-scheme: dark){:root:not([data-theme="light"])}` and
  `:root[data-theme="dark"]` (ui.css already does this). `body` sets an
  explicit background from a token. No preview/mock control bars.
- Works at 390px wide with no horizontal scroll; 16px minimum side gutter.
- A form cannot submit anywhere: handle submit with preventDefault and show an
  honest inline confirmation ("This preview doesn't send yet" style), never
  claim it was sent. Show the email address as selectable text.
- Visible keyboard focus, `prefers-reduced-motion` respected.
- Render and check with: `python3 /home/claude/website/shoot.py <tag>`
  (injects the real fonts locally; writes screenshots to `website/shots/`).

## Brand rules (non-negotiable)

**Palette** navy #092052 · blue #0F58E5 (live/active, story series) · coral
#E5484D (**data outliers only** — ring+dot marker; never text, never a warning,
never an accent, never a "missing" state) · grey #64748B · light grey #CBD5E1
· off-white #F6F8FC · negative #8C1D1D · positive #0F7B3D. Use the tokens in
ui.css (`--ink --body --dim --faint --rule --ground --panel --active --mark
--neg --pos`), which already carry the dark-mode values.

**Type**: Fraunces 300 (`'SOFT' 0,'WONK' 0`, never name opsz) for headings;
Readex Pro for Latin interface/body; Vazirmatn for Arabic; Amiri for Arabic
display. IBM Plex Mono is decoration only:
1. numerals — any size;
2. labels — ≤11px, uppercase, **four words or fewer**;
3. never for anything else: nav, buttons, eyebrows, kickers, form labels,
   captions, body. If a run of mono reads as a phrase, it's wrong.
Arabic runs are single-language, `lang="ar" dir="rtl"`, never mixed into an
English sentence except as a quoted label.

**Illustration** (read `/home/claude/illustrations/ILLUSTRATION.md`):
- Masks live in `/home/claude/illustrations/web_assets.json`
  (`cygnus`, `cyg_outside`, `astrolabe`, `libra`, `cancer_globe`,
  `cancer_sky`, `herosky`), each with layers (`lines`, `stars`, `outside`,
  `dotted`, `field`) as 1-bit PNG data URIs plus `w`,`h`. Render with stacked
  `<span>`s using CSS `mask` + a token colour (see fixed-stars.html).
  lines → `--ink`, stars → `--active`, outside → `--ink` (coral marker only
  on the cleaning service, where the meaning is outliers), herosky → `--faint`.
- Use an image only where its meaning applies. **Three or four illustrations
  on the whole page, not six.** Suggested: hero sky (background only),
  Cygnus's two outside stars → data cleaning, Libra → testing whether it's
  real, Cancer two views → method or proof. Cygnus-full is optional.
  The astrolabe plate's source is unconfirmed — avoid it.
- Never stack a figure on the sky. Don't scale dithered textures (hero sky at
  natural size, `mask-size:auto`). Text must stay readable over the hero sky:
  clear the texture behind the text column or keep text heavy/dark enough.
- Every illustration has a short caption with its source (al-Sufi, *Book of
  the Images of the Fixed Stars*, Iran, late 15th c., The Met, public domain).

**Charts** (read `/home/claude/charts/CHARTS.md`): the proof chart must use the
REAL monthly net revenue in `uci_audit.json` (Dec 2010 – Nov 2011). Title
states the finding; provenance line with n, source, date; bars in context grey
with Sep–Nov in story blue; the June flagged line gets the coral ring+dot
marker with its rule stated (|z| > 7 on line value); text never coloured
coral; solid hairline grid; include an accessible table twin (a toggle or a
visually-hidden table). SVG drawn inline to scale.

**Honesty**: no invented numbers, clients or testimonials. Known gaps outside
the designer's control must be shown honestly and neutrally (dim ink, never
coral):
- the wordmark isn't drawn yet → use the 5a mark SVG
  (`/home/claude/geometry/svg/z01-mark.svg`, stroke colours via tokens) plus
  `.describe(` text as a stand-in;
- Service 02 has no price yet → "Price to be set" style placeholder;
- warning colour undecided → no warning states needed on this page anyway.

**Voice**: "we", plain, specific. Banned words: leverage, solutions,
transform, unlock, seamless, actionable insights, "simply"/"just" before
anything technical, "insights" as a deliverable. Gaza belongs in About, not
the hero. Contact: info@describe.team, reply within 24 hours.

## Design test (the critic will use this)

1. Could it belong to a generic AI startup? → redesign.
2. Real relationship to measurement / information / orientation? → else remove.
3. Uses the vocabulary without drawing an astrolabe literally everywhere?
4. Is coral saying something? → else remove.
5. Still .describe( with the logo removed?
6. Survives in one colour?
7. Information clear with the decorative layer gone?
