---
title: "Two Completely Different Histories Can Produce the Same Ancestry Bar Chart"
type: app
description: K29, K35, K5, K30 — the number in an admixture calculator is a setting, not a discovery. A tutorial paper written specifically about misreading these charts explains what they can and cannot tell you.
date: 2026-06-22
lang: en
translation_key: admixture-bar-charts
tags: ["post", "admixture", "ADMIXTURE", "K value", "population genetics"]
app_id: 65
study: "Lawson DJ et al., Nature Communications 2018"
source: original
layout: article.njk
permalink: "blog/en/how-to-read-admixture-bar-charts/index.html"
---

You open your results and there it is: a bar, split into coloured segments, each labelled with a country, each with a number beside it. It looks like a fact about you.

It is a stacked bar chart, the signature image of consumer ancestry testing, and it is more slippery than it looks.

In 2018 three population geneticists published a paper with an unusually blunt title: *"A tutorial on how not to over-interpret STRUCTURE and ADMIXTURE bar plots"* ([Lawson et al., *Nature Communications*, 2018](https://doi.org/10.1038/s41467-018-05257-7)).

They wrote it because these charts are misread constantly, including by researchers.

## The central problem

Their key demonstration is that **very different demographic histories can produce nearly identical bar plots.**

A population that received a single pulse of admixture 200 years ago, and a population that experienced continuous low-level gene flow over two thousand years, can come out looking the same. The chart shows a proportion. It does not show when, how, or in what direction anything happened.

So the honest reading of any admixture result is narrow: *given this reference panel and this K, my genome is best described as this mixture.* Everything beyond that — a migration story, an origin, a nationality — is added by the reader.

## What the K actually is

The number in K5, K29, K30, K35 is the number of ancestral components the algorithm is instructed to fit. **It is an input, not a result.**

The method underneath is ADMIXTURE, which estimates ancestry proportions for unrelated individuals under a model with K ancestral populations ([Alexander et al., *Genome Research*, 2009](https://doi.org/10.1101/gr.094052.109), PMID: 19648217). You tell it K. It finds the best fit for that K.

Three consequences follow, and they explain most of the confusion these tools generate:

- **There is no true K.** Cross-validation can indicate which K fits the data well, but it does not uncover a real number of ancestral populations, because populations are not discrete objects in nature.
- **Higher K is not more accurate.** K35 is finer-grained than K5. It is not more correct. It splits the same variation into more bins.
- **The components are not peoples.** A cluster labelled with a modern country name is a statistical construct fitted to a reference panel, not a historical nation.

## Sampling decides the answer

The reference panel determines the output. Include many samples from one region and it will tend to appear as its own component; include few and it dissolves into neighbours.

This is why the same genome yields different percentages across companies, across calculator versions, and across K values. Nothing about the person changed. The question changed.

## How to read your own result

Read it as: *these are the reference groups my genome most resembles, under this panel and this K.*

Do not read it as a list of countries your ancestors came from, a fraction of your identity, or evidence for or against a family story. And treat small percentages with particular caution — components below a few percent are frequently noise, and the Lawson tutorial is explicit that they should not be over-interpreted.

## The calculators

GenePlaza hosts several, at different resolutions: [K5](https://www.geneplaza.com/app-store/77), [K29](https://www.geneplaza.com/app-store/65), [K30](https://www.geneplaza.com/app-store/78), [K35](https://www.geneplaza.com/app-store/69), and [SAPDA](https://www.geneplaza.com/app-store/73), which targets South Asian population structure specifically.

As with every app on the platform, the output tells you where your genome would have been placed had it been included in that analysis, against that reference panel. It is a position within a chosen model — not a verdict on who you are.

Running several is genuinely instructive. When the same genome produces different pictures at K5 and K35, you are seeing the method's assumptions, not a contradiction.
