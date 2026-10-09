# Prompt for the coding agent: the bigger logo and the Arabic site

Paste everything below this line into the coding agent working in `describedatateam/website`.

---

Two changes to describe.team. The design and the Arabic copy are finished and approved
by Wafa'a; your job is to build them without changing anything else on the site.

The design source is the brand repo, `describedatateam/describe-brand-system`
(`C:\describe\design\the LOGI\` on Wafa'a's computer). Paths below are relative to it.

## 1. The logo: swap in the approved wordmark, larger

The wordmark is approved (direction A, `wordmark/README.md`). The site still shows the
mark plus `.describe(` typed in Readex Pro at 17px, and a footer note saying the
wordmark is still being drawn. Replace both.

**Files** (`wordmark/web/`): tight viewBoxes, colours as CSS variables with fallbacks:

| File | Use | Size |
|---|---|---|
| `lockup-compact.svg` | nav, every page | 34px tall from 761px up, 30px below |
| `lockup-primary.svg` | footer, every page | 64px tall from 761px up, 48px below |
| `lockup-stacked-compact.svg` | square uses (social card, OG image) | as needed, ≥ 96px tall |

- **Inline the SVG** (don't use `<img>`), so it follows the theme. On the wrapper set
  `--wm-ink: var(--ink); --wm-accent: var(--active);`. Dark mode then works with no
  second file.
- Keep the accessible name on the link: `aria-label=".describe( — home"` on the `<a>`,
  `aria-hidden="true"` on the SVG.
- **Minimum sizes:** compact never below 20px tall; primary never below 48px tall.
  Below 20px (favicon, tiny avatars), use the mark alone, which is already in place.
- **Clear space:** one x-height on every side, which is about half the lockup's height
  (16px at nav size). In the nav, the nav's own padding provides it.
  The nav may grow from 60px to 64px if it needs to. Re-run the a11y check
  afterwards: focus must still never hide under the nav (update `scroll-padding`
  if the nav height changes).
- **Remove** the footer note "The wordmark is still being drawn…" on every page and
  in both languages.
- **Don't** redraw the wordmark, retype it in a font, recolour the caret (the blue bar)
  or stretch it. In one-colour contexts the caret takes the ink colour.

## 2. The Arabic site: `/ar/`, `/ar/check/`, `/ar/privacy/`

**Copy:** `website/arabic/ar-copy.json`, generated from `website/arabic/ar_copy.py`.
- Every entry is `[english, arabic, note]`. The English is the live site's text
  exactly, so you can map string to string. Read every note: they carry the build
  details.
- An empty Arabic string means "remove this line" (the wordmark note).
- `website/arabic/review.html` shows the copy side by side. Wafa'a may still edit a
  few lines there before launch; keep the Arabic in content files, not hard-coded.
- **Don't change the Arabic wording yourself.** If something doesn't fit, flag it.

**Pages and switching**

- The homepage, store profit check and privacy page in Arabic at `/ar/`, `/ar/check/`
  and `/ar/privacy/`. Each page has `<html lang="ar" dir="rtl">`.
- Language switch in the nav, next to Contact: «English» on Arabic pages, «العربية»
  on English pages. Each link goes to the same page in the other language. Give each
  its own `lang`.
- Remember the choice only if the visitor clicks it, never by browser language
  redirects.
- Add `hreflang` alternates (en, ar, x-default → en) and an Arabic `<title>` and
  meta description (in the JSON under `home.meta`).
- In-page links on Arabic pages go to the Arabic pages (`/ar/check/`, `/ar/privacy/`).
  `mailto:`, LinkedIn and GitHub stay the same.

**Right to left: the kit already supports it**

`ui/ui.css` and `type/typography.css` are built on logical properties and have
`[dir="rtl"]` / `:lang(ar)` rules. Use them; don't write a second stylesheet.

- **Type**
  - Headings: Amiri at `--ar-scale` (1.15× the Latin size), line-height
    `--ar-lh-display`.
  - Body: Vazirmatn 300 at `--ar-body-scale` (1.20×), line-height 1.85.
  - Load Amiri and Vazirmatn from Google Fonts on Arabic pages only.
- **Small labels:** IBM Plex Mono has no Arabic. Every small uppercase mono label
  becomes Vazirmatn 500 at about 12px, with no letter-spacing and no uppercase.
  Numerals stay in Plex Mono.
- **Digits:** Western digits (0–9) everywhere. Don't convert to Arabic-Indic digits.
- **The brand name** `.describe(` stays Latin. Inside Arabic text it must be isolated
  LTR. The JSON already wraps it in U+2066…U+2069; in markup, use
  `<bdi dir="ltr">`.
- **Bidi isolation** is also needed for signed numbers (−24,754, +13%), emails, and
  anything with `>` in it, so the sign or symbol doesn't jump to the wrong side.
- **Mirroring:** the layout mirrors fully.
  - The page spine (measuring edge) moves to the right margin.
  - Section numerals sit on the right.
  - Arrows in buttons flip (`.d-icon--dir`).
  - The hero's sky window moves to the left side, with the text on the right.
    Re-run `pixel_check.py` at 1×, 2× and 3×: the sky must stay exactly two colours
    with whole-pixel edges.
- **Charts and rulers don't mirror.** They are number lines and timelines, and the
  convention is that they read left to right. Keep every SVG graphic LTR (`dir="ltr"`
  on the SVG). Only translate its text labels, set in Vazirmatn. The table twin under
  the chart is a normal RTL table, with numbers right-aligned as the kit already does.
- **The wordmark lockup never mirrors.** It sits at the inline-start (right) of the
  nav, reading left to right.
- **The form**
  - Error and success messages come from the JSON.
  - Show success only after the form service confirms it.
  - The email input stays `dir="ltr"`.

**Checks before you ship**

1. Run every existing check on the Arabic pages too, at 320, 390 and 1280, light and
   dark: `a11y_check.py`, `overlap_check.py`, `pixel_check.py`. Point them at the
   built Arabic page.
2. No horizontal scroll at 320px.
3. No Latin fallback glyphs in Arabic text, and no Arabic set in Plex Mono.
4. Screenshots of `/` and `/ar/` side by side in the PR, desktop and mobile.

Work in two pull requests: the logo first, then the Arabic pages. Include screenshots
in each.
