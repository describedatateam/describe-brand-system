# Email templates

Branded HTML for .describe( emails, built from the brand tokens (ink #092052, active blue #0F58E5, muted #64748B, line #CBD5E1, tint #E6EFFF, paper #F6F8FC).

```
python3 render_email.py outreach   body.md  [--lang ar] > out.html   # 1:1 emails: cold, follow-up, offer
python3 render_email.py newsletter issue.md [--lang ar] > out.html   # The .describe( Brief (plain layout)
python3 render_email.py brief      issue.md [--lang ar] [--img-base URL] > out.html   # The Brief, rich layout
python3 build_assets.py [--num 4 --unit "weeks to" --event "White Friday" --date "Friday 27 November"]   # hero + ruler PNGs
```

Pass the HTML as the Gmail draft's `htmlBody` and the plain text as `body`. Do not also add the Gmail signature: the template already has one.

- **Outreach** stays a plain-looking letter (no banner, no body images) so it reads as personal and lands in the inbox. Only the signature carries the mark.
- **Newsletter**: wordmark header, blue-ruled section headings, "Our take" tinted notes (`> ` lines), one button (`[[Text](url)]`), footer with why-you-get-this and "reply stop".
- Arabic: `--lang ar` flips direction and alignment.
- Images are served from this branch (`email/lockup-ink-40.png`, `email/mark-44.png`) via raw.githubusercontent.com. Keep the branch, or merge it to main and switch the two URLs.

Newsletter markup:

```
# Issue title
_Edition line · date_

## Section heading
Paragraph with **bold** and [a link](https://describe.team/).

> **Our take:** one or two sentences.

1. numbered item
2. numbered item

[[Book a free 20-minute call](https://describe.team/#contact)]

---
Sources: ...
```

## The rich Brief layout (`brief`)

Order: wordmark and edition label, ticked rule, lede, countdown hero, the lead section with its numbered list as a tinted card, news items with "Our take" as a ruled note, a brass band for the one thing to try, a navy call-to-action block, sources, signature, footer.

Tag each section heading in the issue file:

```
## Four weeks to White Friday {lead}      hero image, then paragraphs; a numbered list after a line ending ":" becomes the card
## What else happened {news}              "**Bold headline.** body" items; "> Our take: ..." notes
## One thing to try {band}                brass band; a "> " line becomes the pull quote
## Want your baseline done for you? {cta} navy block; the [[button]]; a "Not subscribed yet?" line renders small
```

`---` then `Sources: ...` at the end of the last section renders above the signature. Untagged sections render as plain text.

Images are PNG (Gmail ignores SVG), two only: `brief-hero.png` and `brief-rule.png`, built by `build_assets.py` from the tokens, the ring and star in `geometry/astrolabe.py`, and the brand fonts. **Rebuild the hero for each issue** (`--num`, `--date`): the countdown figure goes stale. The tally shows the weeks left as strokes and the White Friday week as the active diagonal, so it only makes sense for a count of four or fewer; for a bigger count, change the hero. Use `--img-base` to preview against local files. The layout reads with images off, and headlines fall back to Georgia and body text to Arial, since the brand faces do not load in inboxes.
