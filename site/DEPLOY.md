# Publishing the site on Cloudflare Pages

The homepage in `site/` is published as a static site. `site/build.sh`
copies only the public files into `site/dist/`; the analysis code and notes
in `site/proof/` stay in the repository and are never served.

| Path | Published as |
|---|---|
| `site/index.html` | `/` |
| `site/public/privacy.html` | `/privacy` |
| `site/public/404.html` | shown for any unknown path |
| `site/public/_headers` | security and cache headers |
| `site/public/*` (icons, `og.png`, `robots.txt`, `sitemap.xml`) | as named |

## One-time setup (Cloudflare dashboard)

1. **Workers & Pages → Create → Pages → Connect to Git**, pick
   `describedatateam/describe-brand-system`. Authorise the Cloudflare GitHub
   app for the repository if asked.
2. Build settings:
   - Framework preset: **None**
   - Build command: `sh site/build.sh`
   - Build output directory: `site/dist`
   - Root directory: leave empty
   - Production branch: `main`
3. Save and deploy. The site appears at `<project>.pages.dev`. Every other
   branch and pull request gets its own preview URL.

## Custom domain

In the Pages project, **Custom domains → Set up a custom domain**, add
`describe.team`, then `www.describe.team`.

- If `describe.team` already uses Cloudflare nameservers, Cloudflare adds the
  DNS records itself.
- If the domain is registered elsewhere, either move its nameservers to
  Cloudflare (recommended; it keeps email records working if you copy them
  across) or add the `CNAME` record Cloudflare shows at your registrar.
- Point `www` at the apex with a redirect rule (Rules → Redirect Rules,
  `www.describe.team/*` → `https://describe.team/${1}`, 301).

Before changing nameservers, make sure the MX, SPF and DKIM records for
`info@describe.team` exist in Cloudflare DNS, or email will stop arriving.

## Before launch

- Sign off the proof section (`site/proof/README.md`).
- Set a price for service 02, or keep "Priced per project".
- Confirm `info@describe.team` receives mail: the contact form opens the
  visitor's email app addressed to it.
- The canonical URL, sitemap and social image assume `https://describe.team/`.
  If the domain differs, search and replace it in `site/index.html` and
  `site/public/`.
