# Email templates

Branded HTML for .describe( emails, built from the brand tokens (ink #092052, active blue #0F58E5, muted #64748B, line #CBD5E1, tint #E6EFFF, paper #F6F8FC).

```
python3 render_email.py outreach   body.md  [--lang ar] > out.html   # 1:1 emails: cold, follow-up, offer
python3 render_email.py newsletter issue.md [--lang ar] > out.html   # The .describe( Brief
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
