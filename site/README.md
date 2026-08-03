# GenePlaza blog

Static 11ty site served at **geneplaza.com/blog** via a dedicated CloudFront
behaviour. The Ember app is untouched — see `../blog_infra/DEPLOY.md`.

```bash
npm start     # local dev server
npm run check # markdown gate + build gate (run before every deploy)
npm run build # -> _site/blog/...
npm run deploy # check + build + s3 sync
```

## Layout

```
content/           51 posts (EN 28 · FR 13 · NL 10) + index, sitemap, robots
content/assets/    GenePlaza logo
content/images/    post illustrations
_includes/base.njk    shell: nav, brand tokens, footer
_includes/article.njk post layout: hreflang, language switcher, cohort-framing note
```

## Two things that will bite you if changed

**`pathPrefix` is `"/"`.** Permalinks already start with `blog/`, so output lands at
`_site/blog/...`. Setting `pathPrefix: "/blog/"` produces `/blog/blog/...`.

**Images are `/blog/images/...`.** Anything referenced outside `/blog/*` falls
through to the Ember origin and 404s into the SPA.

## Conventions

Every post carries `lang` and, when translated, a shared `translation_key`. The
layout uses it to emit reciprocal `hreflang` tags, the visible language switcher,
and the `xhtml:link` entries in the sitemap — so adding a translation needs no
template edits.

`type` is `app`, `science` or `announcement`, and decides how strictly the
validator treats citations, CTAs and page length.

Brand tokens in `base.njk` are copied from
`geneplaza-webapp/app/styles/_variables.scss` (`$brand-primary #44355b`,
`$brand-secondary #efefe5`, `$brand-success #20eac8`, Work Sans). If the app's
palette changes, update them here too.

## Editorial rules

Enforced by `~/.pi/agent/skills/geneplaza-blog/`:

- One post sells one app, deep-linked by id — never a generic `/app-store` link
- Every scientific claim cites a DOI/PMID that has been resolved, not remembered
- A score says where the reader **would have scored had they taken part in the
  original study** — never that their personal risk is raised or lowered
- No humour in health content; no competitor links without a stated justification
