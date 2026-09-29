# Prompt for the coding agent: build, host and make editable the .describe( website

Paste everything below this line into the coding agent.

---

You're taking over the website for **.describe(**, a new data-analytics practice for small companies, run by Wafa'a Al-Hayek from Gaza. The design is finished and approved. Your job is engineering: turn the approved page into a real, hosted, editable website **without changing how it looks**.

## 1. What exists

The repository is `C:\describe\design\the LOGI\` (GitHub: `describedatateam/describe-brand-system`, private). Paths below are relative to it.

- `website/site.html`: **the approved homepage.** Self-contained, about 505 KB: CSS, JS and images are inline, and fonts load from Google Fonts. It was written as a claude.ai Artifact, so it has **no `<!doctype>`, `<html>`, `<head>` or `<body>`**. It starts with `<title>` and then `<style>`. Treat this file as the visual reference. Your output must render identically to it.
- `website/template.html`, `website/build.py` and `website/graphics.py`: the generator that produced `site.html`.
  - `build.py` inlines `type/typography.css` and `ui/ui.css`, the mark SVG, icons, and three 1-bit sky masks.
  - It draws every chart and ruler as inline SVG from `decisions/uci_audit.json`.
  - It asserts that all numbers reconcile.
  - `graphics.py` builds the rulers and counting marks using the geometry library in `geometry/astrolabe.py`.
- `website/BRIEF.md` and `website/BRIEF2.md`: the design and brand rules (palette, type, voice, banned words, honesty rules, chart rules). Read both before touching anything.
- `website/critiques/`: the critic's reports; the last round scored 9/10.
- Check scripts (Python and Playwright). They must keep passing:
  - `website/shoot.py`: renders the page at 1280 and 390 wide, in light and dark.
  - `website/a11y_check.py`: focus, nav overlap, target sizes and chart tooltip.
  - `website/overlap_check.py`: label collisions and clear space around numbers at 320–1280.
  - `website/pixel_check.py`: the hero sky must be exactly two colours at 1×, 2× and 3×.
  - `website/wordcount.py`: the page stays around 1,100 words.
- `decisions/uci_retail.py`: recomputes `decisions/uci_audit.json` from the public UCI "Online Retail" workbook. Download it from https://archive.ics.uci.edu/dataset/352/online+retail. It isn't in the repo.
- `illustrations/hero_night.py` and `illustrations/bitmaps/hero-night/`: the hero sky masks.
- `decisions/fonts/`: local copies of the brand fonts. The screenshot scripts use them; production uses Google Fonts.

**Hard-coded paths.** The scripts point at the designer's cloud workspace. Remap them to the repo:
- `/home/claude/` → the repo root
- `/home/claude/decisions/fonts/` → `decisions/fonts/`
- `/mnt/user-data/uploads/arabia/` → `C:\describe\design\arabia\` (the source scans; only needed to regenerate the sky)

Make paths relative to each script's location. Don't leave absolute paths in the code.

## 2. What to build

1. **New repo** `describedatateam/describe-site`. It must be under the **organization**, not the personal `describeteam` account. Copy in only what the site needs. Keep the brand-system repo as the design source.
2. **Content out of the template.** Move all editable copy into content files (Markdown with front-matter, or YAML/JSON). The build reads them and produces the same HTML. Minimum collections:
   - `services`: title, summary, price (a number, or "to be set"), days/weeks, revisions, bullets, "pick this when".
   - `portfolio` (new; not on the page yet): title, slug, date, client, problem, what we did, key findings (each a figure plus a label), **n and data source (required)**, source link, external link, status.
   - `faq`: question and answer.
   - `settings`: contact email, reply time, languages, LinkedIn, GitHub, and the hero copy.
   - The "Where we are" counts (exploratory sessions, proposals, completed projects). Derive "completed" from the portfolio; don't type it by hand.
3. **Pages.**
   - `/`: the homepage, identical to `site.html`.
   - `/work/`: portfolio index. Hide it while the portfolio is empty.
   - `/work/<slug>/`: one page per portfolio piece.
   - Leave room for an Arabic version later. It must be a full right-to-left mirror written for an Arabic reader, not machine-translated. Use Amiri for headings and Vazirmatn for body text.
   - New page types reuse the existing components (the `d-` classes in `ui/ui.css`) and graphics (`graphics.py`). Don't invent new styles.
   - Offer a small set of section types an editor can add and reorder, for example text with a big figure, a findings list, and a quote.
4. **Real HTML documents.** Wrap each page in a proper document: doctype, `lang`, charset, viewport, meta description, Open Graph tags, and a favicon from the 5a mark (`5a-favicon.png`). Keep everything else inline as it is now, or split CSS into one cached file. Your choice, as long as the rendering is identical.
5. **Hosting.** Use GitHub Pages or Cloudflare Pages, built by CI on every push. The domain is **describe.team**. Ask Wafa'a before changing any DNS.
6. **Admin panel.** Set up Pages CMS (https://pagescms.org) or Decap CMS (https://decapcms.org), editing the content files through GitHub login.
   - Required fields must be enforced in the form, above all n and source on portfolio pieces.
   - Saving commits to the repo, and CI rebuilds the site.
7. **Contact form.** The page currently never sends; it says so honestly. Connect a form service and ask Wafa'a which one. Show "sent" only after a confirmed success response. Keep the honest fallback message and the selectable email address.
8. **CI gates.** Run `build.py`'s asserts plus `a11y_check`, `overlap_check`, `pixel_check` and `wordcount` in CI. A failing check blocks the deploy.

## 3. Rules you must not break

- **Don't redesign.** Compare screenshots of your build against the original, using `shoot.py`, at 1280 and 390 in light and dark. Any visible difference is a bug unless Wafa'a approves it.
- **The hero sky is pixel-perfect.** The masks are shown at natural size and never scaled. The 1×, 2× and 3× files are swapped by `min-resolution` media queries. Don't run them through an image optimiser that resamples; lossless recompression is fine.
- **Real data only.** Every number on the site comes from `uci_audit.json` or the content files. Every chart states its n and source. No invented clients, testimonials or numbers.
- **Coral (#E5484D) marks data outliers only.** It's never used for text, buttons, warnings or decoration.
- **Portfolio honesty.**
  - Use only real, completed work. Anonymise the client unless they've given permission.
  - The Glocal Shift transportation hackathon project must **never** appear as agency work.
- **Rights.** Before launch, confirm the source of the hero sky: a British Library Flickr scan, id 11241855653. Its record is listed as still to confirm in `illustrations/PROVENANCE.md`. If it can't be confirmed as public domain, flag it to Wafa'a; don't ship it.
- **Accessibility.** Keep keyboard focus (the four-corner sighting frame), reduced motion, 24px minimum targets, the chart's table twin, and contrast.

## 4. Before you start, ask Wafa'a

1. Does she own describe.team, and is anything live on it now?
2. Which host (GitHub Pages or Cloudflare Pages) and which CMS (Pages CMS or Decap)?
3. Which form service for the contact form?

Then work in small pull requests: first repo setup and the identical homepage build, then content extraction, then CMS, then new pages. Each PR includes screenshots and check output. Commit messages in English, plain and specific.
