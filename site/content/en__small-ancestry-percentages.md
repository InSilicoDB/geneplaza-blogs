---
title: "Your 0.5% Is Probably Not an Ancestor"
type: science
description: Small ancestry percentages get read as distant relatives and turned into family stories. Usually they are the algorithm hedging. Here is how to tell the difference, including two settings in your results that almost nobody opens.
date: 2024-07-06
lang: en
translation_key: small-percentages
tags: ["post", "ancestry", "admixture", "reference panels", "trace ancestry"]
competitor_context: "Names 23andMe and AncestryDNA to explain a confidence setting in their own interfaces that readers should use. Instructional, unlinked, no link equity passed. Reviewed."
source: original
layout: article.njk
permalink: "blog/en/small-ancestry-percentages/index.html"
---

Someone posts their ancestry results online. Near the bottom, under the big numbers, sits **0.5% Filipino & Austronesian**. Within an hour the replies have built a story around it: enslaved Malagasy people transported to the Americas, a Spanish colonial route through the Philippines, a great-great-grandmother nobody remembers.

It's a good story. It might even be true. But the 0.5% is not evidence for it, and the same afternoon a second person is told their 0.2% Canary Islander points to a specific ancestor from a specific archipelago.

Here is how to tell a real signal from an algorithm hedging.

## Two settings almost nobody opens

**On 23andMe**, open Ancestry Composition and move the confidence slider from the default 50% up to 90%. Most components under about 1% will vanish.

They were never removed from your genome. They were never confidently there. **The default view is the optimistic one**, and the slider is the tool telling you so.

**On AncestryDNA**, click into any single region. Alongside the headline number there is an estimate *range*, and for small regions that range frequently runs down to 0%. The number on the summary screen is the midpoint of a guess presented as a fact.

Neither of these is hidden. Both are simply never opened.

## Learn to spot the hedge

A real set of results, posted recently:

| Region | Estimate |
|---|---|
| Central Italy | 2% |
| Southern Italy | 2% |
| Northeastern Italy | 2% |

Three regions. Identical values.

That is not three Italian ancestral lines. That is an algorithm distributing uncertainty evenly because it cannot choose between neighbours. When a stretch of your genome resembles several reference groups roughly equally, it gets split across the nearest options — and **identical small values across adjacent regions is the signature.**

The same person's results showed France 6% and Iberia 4%, in a family with documented Peruvian ancestry where the European input was overwhelmingly Spanish. Read separately, those are three findings. Read properly, they are one finding — roughly 16% southwestern European — chopped into labelled bins.

## Why the bins don't hold

An ancestry estimate is a similarity measurement against reference populations that somebody chose. It is not a lookup of where your ancestors lived.

Europe is the clearest case. Plot Europeans by their DNA and you essentially recover the map of Europe: allele frequencies change gradually with distance rather than jumping at national borders ([Novembre et al., *Nature*, 2008](https://doi.org/10.1038/nature07331), PMID: 18758442). That is a beautiful result about geography and a terrible basis for assigning one person to one country. France, Iberia and Italy blur into one another in your results because they blur into one another in reality.

There is a paper written specifically about over-reading these charts, with the memorable title *"A tutorial on how not to over-interpret STRUCTURE and ADMIXTURE bar plots"* ([Lawson et al., *Nature Communications*, 2018](https://doi.org/10.1038/s41467-018-05257-7)). Its central demonstration is that **very different population histories can produce nearly identical bar plots**. A single pulse of admixture two centuries ago and continuous low-level gene flow over two millennia can come out looking the same.

The chart shows a proportion. It does not show when, how, or in which direction anything happened. Everything beyond the proportion is supplied by the reader.

## Three things a small number can be

- A stretch of genome that resembles several reference groups about equally
- Noise at the limit of the method's resolution
- Occasionally, a genuinely distant ancestor

The difficulty is that all three look identical on screen.

And distance works against you. Ten generations back you have 1,024 ancestors, but only a few hundred contributed any detectable DNA to you at all. Recombination is a lottery: a real ancestor can disappear from your genome completely while a statistical artefact sits at 0.5% looking like a discovery.

## What to trust instead

**Trust the big components.** 82% Indigenous American, or 75% West African, is a large stable signal that will not move much between updates.

**Trust sub-regional detail inside those large components.** A West African result that separates Nigerian from Ghanaian, Liberian and Sierra Leonean from Senegambian is telling you something real about where in West Africa your ancestors came from. That is far more informative than any trace component, and it gets a fraction of the attention.

**Treat anything under a couple of percent as a maybe.** Not a fact, not a lead, not a family story.

**And when the numbers shift on the next update — they will — that is the method improving.** It was always a measurement with error bars. Most interfaces simply decline to draw them.

## Reading your own

The [Ancestry app](https://www.geneplaza.com/app-store/58) reports your estimated proportions against reference populations, and the [admixture calculators](https://www.geneplaza.com/app-store/65) do the same at various resolutions.

The caveats on this page apply to those results exactly as they apply to anyone else's. As with every app on the platform, the output tells you where your genome would have been placed within that reference set had it been included in the analysis — a similarity measurement under a chosen model, not a certificate of descent.

Two related pieces, if this is your rabbit hole: [what an ancestry estimate actually measures](/blog/en/what-is-genetic-ancestry/), and [how to read the bar chart](/blog/en/how-to-read-admixture-bar-charts/) — including what the K in K29 or K36 really is.
