# Organic growth plan

**Goal:** ~14 app sales/month attributable to content (median app €14) — enough to
justify a $200/month tooling spend.

**Measurement:** Umami at `analytics.geneplaza.com`, website id `f9b20801-26ed-459d-aa4d-b23091d05550`.
Outbound clicks to `/app-store/<id>` are tracked automatically. Check referrers
before scaling anything.

**Baseline (set the day this starts):** _____ visits/month, _____ app-store clicks/month.

---

## The angle

Almost every post debunks an over-interpretation: *the cilantro gene explains
almost none of it*, *the professional body recommends against MTHFR testing*,
*your ancestry result changed and nobody edited your DNA*.

That is not marketing copy — it is the answer to questions asked daily in DTC
genetics communities. Lead with the correction, not the product.

---

## Channel priority

| Rank | Channel | Time to value | Why |
|---|---|---|---|
| 1 | **Internal linking** (app page ↔ post) | immediate | Free, uses existing domain authority, catches people already on a product page. **Ember work.** |
| 2 | **Reddit** | 2–4 weeks | Real clickable traffic; the debunking angle fits |
| 3 | **SEO / Search Console** | 3–6 months | Compounding. FR/NL SERPs are near-empty — that is the wedge. |
| 4 | **Instagram** | 6–12 months | Brand, not traffic. No links in posts. |
| 5 | **Facebook** | — | Auto-post and forget. 1–2% organic reach. |

---

## 1. Internal linking (do first)

- [ ] Every one of the 49 app pages links its blog post
- [ ] Every post links its app (done — 46/49 covered)
- [ ] Footer of geneplaza.com links Instagram + Facebook (currently links neither)
- [ ] Blog linked from the main nav

Highest return on the list and it is a day of Ember work.

---

## 2. Reddit

### Rules of engagement

- **Real named account**, founder identity, disclosed every time. Reddit forgives a
  transparent founder and destroys a covert marketer.
- **~9 substantive comments per 1 link.**
- **Answer inside the comment.** Full answer, cite the paper, link only if someone
  wants depth. A comment that is only a link gets removed.
- **Read each sub's rules first** — some ban commercial domains outright.
- A domain ban is sitewide and effectively permanent. Do not rush this.

### Targets

| Subreddit | Size | Angle |
|---|---|---|
| r/23andMe | ~250k | Daily "what does this mean?" posts |
| r/AncestryDNA | ~150k | "My percentages changed!" |
| r/genealogy | ~300k | Ancient DNA, migrations, era posts |
| r/genetics | ~90k | GWAS limitations, effect sizes |
| r/AskHistorians | large, strict | Bell Beaker, Cheddar Man, Rome — impeccable sourcing only |

### Recurring questions we already answer

| Question | Post |
|---|---|
| "Why did my ancestry percentages change?" | `/blog/en/what-is-genetic-ancestry/` |
| "I have the MTHFR mutation — what now?" | `/blog/en/mthfr-testing-acmg/` |
| "Is the cilantro gene real?" | `/blog/en/cilantro-tastes-like-soap-genetics/` |
| "My report says increased risk — should I worry?" | `/blog/en/childhood-inflammation-depression-risk/` |
| "What do K numbers mean?" | `/blog/en/how-to-read-admixture-bar-charts/` |
| "Am I related to Cheddar Man?" | `/blog/en/cheddar-man-dark-skin-blue-eyes/` |

### Four weeks

- [ ] **Week 1** — create/age account, comment only, no links, reach 100+ karma
- [ ] **Week 2** — 3–5 substantive answers/day, still no links
- [ ] **Week 3** — first links, only where they add real depth
- [ ] **Week 4** — check Umami referrers. Reddit visible? Scale. Not visible? Diagnose, do not persist on faith.

---

## 3. Instagram — `@gene.plaza`

### Carousel formula

```
1  the surprising number, big type over the illustration
2-4  explanation, one idea per slide
5  the limitation  <- the differentiator
6  source: author, journal, year
```

### First ten posts

- [ ] 24% vs 63% — morning people by age. "Nobody's genome changed."
- [ ] 90% of Britain's gene pool replaced (Bell Beaker illustration)
- [ ] Cheddar Man — dark skin, blue eyes, decoded partly via a consumer DNA test
- [ ] The cilantro gene explains under 1%
- [ ] 1.5% — what 249,796 people's obesity genes actually explained
- [ ] 11% — what a DNA test predicts about schooling
- [ ] Copper Age Iberia — male lineages replaced, female lineages not
- [ ] Imperial Rome looked genetically eastern Mediterranean
- [ ] Iceland could identify almost every high-risk woman. It doesn't.
- [ ] The neuroticism gene that failed to replicate

3×/week. Reply to every comment. Assets in `site/content/assets/` and
`site/content/images/`.

---

## 4. SEO

- [x] Sitemap live at `/blog/sitemap.xml`
- [x] Search Console property verified
- [ ] Sitemap submitted
- [ ] `gcloud auth application-default login --scopes=…webmasters.readonly` so
      `tools/gsc.py` can report
- [ ] Fix the apex — `geneplaza.com/*` 404s on every path but `/`. Splits ranking
      signals and breaks every existing inbound link to the store.
- [ ] Monthly: `python3 tools/gsc.py --queries --pages`

FR/NL is the wedge. *"test ADN métabolisme caféine"* is a near-empty SERP;
the English equivalent is owned by 23andMe and Healthline.

---

## Review cadence

**Monthly**, in this order:

1. `tools/gsc.py --queries --pages` — what we rank for
2. Umami referrers — where visits come from
3. Umami outbound clicks to `/app-store/<id>` — the conversion proxy
4. Sales, if attribution exists

**Kill rule:** any channel with no measurable traffic after 8 weeks of real effort
gets dropped, not doubled down on.
