# geneplaza-blogs

The GenePlaza blog: 51 posts (EN 28 · FR 13 · NL 10), each built on the
peer-reviewed study behind a GenePlaza app.

Served at **geneplaza.com/blog** from its own S3 bucket via a dedicated CloudFront
behaviour. **The Ember app is not modified** — see [How /blog stays outside Ember](#how-blog-stays-outside-ember).

```
site/     11ty site — content, layouts, config
tools/    validators (vendored so CI needs no external skill install)
tests/    pytest regression suite
infra/    CloudFront function + deployment runbook
```

## Quick start

```bash
pip install -r requirements.txt
cd site && npm install

npm start          # dev server
npm run check      # markdown gate + build gate
npm run build      # -> site/_site/blog/...
```

## The three gates

Nothing ships unless all three pass. Each exists because something got through the
previous ones.

| Gate | Command | Catches |
|---|---|---|
| **Unit tests** | `pytest tests/` | regressions in the validator's own rules |
| **Markdown** | `tools/validate_post.py --dir site/content` | missing citations, generic CTAs, personal-risk framing, humour in health content, invalid YAML |
| **Build** | `tools/build_check.py --site site` | pages that do not render, empty bodies, broken internal links |

The markdown gate alone is not enough. Two bugs reached the preview with "51/51
passed": frontmatter that was valid-looking but invalid YAML (11ty refused to build
the whole site), and a template that used `layout:` with `{% block %}` and rendered
an empty body. **Only building catches those.**

## How /blog stays outside Ember

CloudFront matches cache behaviours by path pattern *before* the request reaches an
origin:

```
Request → CloudFront
           ├── behaviour "/blog/*" → S3: geneplaza-blog-static   (this repo)
           └── behaviour "*"       → S3: Ember app + SPA fallback (untouched)
```

A CloudFront Function (`infra/blog-redirects.js`) on viewer-request does two jobs:
301s the 18 legacy WordPress URLs, and rewrites `/blog/en/x/` → `/blog/en/x/index.html`,
which S3 does not do for sub-paths.

### Known risk: soft 404s

The SPA fallback is a CloudFront **custom error response** (403/404 → `/index.html`,
status 200), and custom error responses are configured **per distribution, not per
behaviour**. A mistyped blog URL therefore returns the Ember SPA with a 200 rather
than a 404 — bad for users and worse for SEO.

Decide before launch: a path-aware function returning a real 404 for unknown
`/blog/*`, or accept and monitor. Do not discover this in production.

## Two invariants that will bite you

**`pathPrefix` stays `"/"`.** Permalinks already begin with `blog/`, so output lands
at `_site/blog/...`. Setting `pathPrefix: "/blog/"` produces `/blog/blog/...`.

**Images are `/blog/images/...`.** Anything outside `/blog/*` falls through to Ember.

Both are enforced by the `guard` job in CI.

## Content conventions

Every post carries `lang`, and translations share a `translation_key`. The layout
uses it for hreflang, the visible language switcher and the sitemap — adding a
translation needs no template edit.

`type` is `app`, `science` or `announcement`, and decides how strictly citations,
CTAs and page length are enforced.

**Score framing is non-negotiable.** A GenePlaza score says what your result *would
have been had you participated in the original study*, within that cohort — never
that your personal risk is raised or lowered. The validator fails posts that invert
this.

## Deployment

See [`infra/DEPLOY.md`](infra/DEPLOY.md). Nothing is deployed automatically; CI
builds and uploads an artifact, and the S3 sync is a deliberate manual step until
the CloudFront behaviour is in place.
