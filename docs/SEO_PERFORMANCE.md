# SEO and performance

## What is implemented

| Item | Where |
|---|---|
| Unique `<title>` and meta description per page | `templates/base.html` blocks, overridden per page |
| Meaningful URLs | `/olympiads/mathematics/`, `/register/` |
| One `<h1>` per page, ordered h2/h3 | all public templates (covered by a test) |
| Canonical tag | `base.html`, built from `SITE_URL` + path |
| XML sitemap | `/sitemap.xml` (home, register, active Olympiads) |
| robots.txt | `/robots.txt`, disallows private areas and links the sitemap |
| Structured data | `EducationalOrganization` on home, `Course` on Olympiad pages (JSON-LD) |
| Private areas not indexed | `noindex` meta on login and dashboards, plus an `X-Robots-Tag` header on `/student/`, `/staff/`, `/login/`, `/api/`, `/django-admin/` |
| Images and alt text | No raster images. The logo is inline SVG with an accessible label, and the favicon is an SVG, so there is nothing heavy to optimise. |
| Mobile friendly | Responsive CSS, viewport tag, 44px-ish touch targets |
| Speed | No frameworks, one small CSS file, one tiny deferred JS file, system fonts, gzip/brotli via WhiteNoise |

## Lighthouse report (to be filled in after deployment)

Lighthouse needs the live HTTPS URL, which does not exist yet, so no scores are claimed here. After deploying:

1. Open the staging URL in Chrome, DevTools > Lighthouse, run Mobile for `/`, `/olympiads/mathematics/` and `/register/`.
2. Save the HTML reports (or screenshots) into `docs/lighthouse/`.
3. Paste the scores below and note any remaining issues.

| Page | Performance | Accessibility | Best practices | SEO |
|---|---|---|---|---|
| `/` | | | | |
| `/olympiads/mathematics/` | | | | |
| `/register/` | | | | |

## Likely remaining issues

- A free-tier host can add a cold-start delay to the first request, which lowers the Performance score.
- Cache headers for HTML pages are Django's defaults.
- No `hreflang` or Open Graph image, which is fine for a single-language prototype.
