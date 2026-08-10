---
title: "Plot Europeans by Their DNA and You Get a Map of Europe"
type: app
description: A 2008 study showed genetic variation across Europe mirrors geography closely enough to place people within a few hundred kilometres. That result is the foundation of every 3D genetic-distance visualisation — and of their limits.
date: 2026-06-29
lang: en
translation_key: genetic-distance
tags: ["post", "genetic distance", "PCA", "population structure", "ancestry"]
app_id: 63
study: "Novembre J et al., Nature 2008"
source: original
layout: article.njk
permalink: "blog/en/genetic-distance-3d-ethnicity/index.html"
---

Take 3,000 Europeans, look at half a million positions in each genome, and reduce all of that to two numbers per person. Plot those numbers.

You get a map of Europe.

Not a metaphor for one — an actual scatter of dots in which Spain sits southwest of France, Italy hangs below Switzerland, and the Baltic states cluster in the northeast. The correlation is close enough that many individuals can be placed within a few hundred kilometres of their grandparents' origin ([Novembre et al., *Nature*, 2008](https://doi.org/10.1038/nature07331), PMID: 18758442).

## Why geography shows up in a genome

People historically had children with people nearby. Over enough generations, that simple fact produces gradients: allele frequencies change gradually with distance rather than jumping at borders.

The technique that reveals it — principal component analysis — does not know anything about countries. It finds the axes along which the data varies most, and in Europe those axes turn out to run roughly north–south and east–west.

This is different from an admixture bar chart. A bar chart assigns you proportions of K ancestral components. A distance plot places you in a continuous space relative to other samples. The second makes no claim that discrete ancestral populations exist, which is one reason population geneticists tend to prefer it.

## The word "ethnicity" is doing something the maths is not

A tool can measure genetic distance. It cannot measure ethnicity.

Ethnicity is social: language, religion, self-identification, shared history, and how others categorise you. Genetic distance is a statistic describing allele-frequency similarity between samples. They correlate in some places, weakly or not at all in others, and no coordinate in a plot has an opinion about who anyone is.

The clearest way to see this: two people from the same village with the same identity can land in different spots, and a plot's clusters shift when you change which samples are included. **The reference set draws the map.**

## What the gradients hide

**Continuous does not mean uniform.** Gradients contain dense clusters where populations were historically isolated, and sparse regions where sampling is thin.

**Recent migration breaks the geography.** The 2008 result relied on people whose grandparents came from one place. Someone with grandparents from four countries lands somewhere in the middle — a position that corresponds to no real location.

**Europe is unusually well sampled.** The tidy map exists partly because so many European samples have been collected. Most of the world is far less densely represented, and the resolution is correspondingly worse.

## What the app reports

The [Ethnicity Calculator](https://www.geneplaza.com/app-store/63) visualises your genetic distances to known populations in 3D, using algorithms developed by Lasse Folkersen, whose open-source work on consumer polygenic tools is documented in the literature ([Folkersen et al., *Frontiers in Genetics*, 2020](https://doi.org/10.3389/fgene.2020.00578), PMID: 32714365).

What you are looking at is where your genome would sit among the reference samples had it been included in that analysis. Being near a cluster means your genotype resembles those samples. It does not mean you are from there, and the plot cannot tell you who you are — only who you resemble, among the people who happen to have been sampled.
