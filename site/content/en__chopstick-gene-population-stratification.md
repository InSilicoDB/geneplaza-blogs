---
title: "In 1994, Two Geneticists Explained How You Could Discover a Gene for Using Chopsticks"
type: science
description: A study can find a real, statistically significant association between a genetic variant and a habit that has nothing to do with genetics. The mechanism is population stratification, and it is the reason two maps looking alike proves nothing.
date: 2026-07-13
lang: en
translation_key: chopstick-gene
tags: ["post", "population stratification", "GWAS", "confounding", "PCA"]
source: original
layout: article.njk
permalink: "blog/en/chopstick-gene-population-stratification/index.html"
---

Imagine surveying a few hundred people in San Francisco. You record how well each one uses chopsticks, you genotype them, and you look for associations.

You will find one. A variant of the HLA immune-system genes will show a strong, statistically significant association with chopstick proficiency — a real result, correctly calculated, that would survive peer review on the numbers alone.

There is, of course, no chopstick gene. Eric Lander and Nicholas Schork used this example in a 1994 review to illustrate the trap that had been quietly ruining genetic association studies ([Lander & Schork, *Science*, 1994](https://doi.org/10.1126/science.8091226), PMID: 8091226).

The sample contained people of Asian and European descent. Chopstick use is more common in the first group for cultural reasons. HLA allele frequencies differ between the two for population-history reasons. The two things correlate because they share a cause — ancestry — not because one causes the other.

## The map version of the same mistake

This has a well-travelled cousin in statistics teaching: put a map of the 1992 UK mad cow disease outbreak next to a map of the 2016 Brexit referendum result and the resemblance is striking. Cattle-farming areas and Leave-voting areas overlap heavily.

Both maps are accurate. The overlap is real. And the inference is worthless, because almost anything that varies with rurality, population density, age structure or industrial history will produce roughly that map. The shared cause is geography, and geography is upstream of a great many things.

Any two variables that both track ancestry, or both track place, will correlate. That is not a discovery about either of them.

## Why this is the central problem in genetics

Population stratification is not a curiosity. It is the failure mode that early candidate-gene studies kept walking into, and it explains a large share of findings from that era that never replicated.

Consider what a genome-wide association study is doing: comparing allele frequencies between people with a trait and people without. If your cases and controls differ even slightly in ancestry — and they usually do — then **every variant whose frequency differs between those ancestries will show an association**. You get thousands of hits, all statistically real, none of them causal.

The field's response was methodological rather than rhetorical. The standard fix, published in 2006, uses principal components analysis to summarise the ancestry structure in a dataset and then includes those components as covariates, so associations are tested *within* ancestry rather than across it ([Price et al., *Nature Genetics*, 2006](https://doi.org/10.1038/ng1847), PMID: 16862161).

That paper is one of the most cited in human genetics, and the reason is unglamorous: it is the correction that made the rest of the field's results trustworthy.

## What this means for your own results

Three consequences follow, and they are worth carrying around.

**A statistically significant association is not a mechanism.** It says two things vary together in this dataset. Whether one causes the other is a separate question requiring separate evidence.

**Polygenic scores travel badly.** A score built in one population loses accuracy when applied to another, and the loss grows with genetic distance — which is why a well-built consumer app reports your percentile against an *ancestry-matched* reference group rather than one universal distribution. It is also why so much of this literature comes with a European-ancestry caveat attached.

**Ancestry is the confounder hiding under most population-scale claims about behaviour.** Any trait that differs between groups for cultural, historical or economic reasons will produce genetic associations if you do not control for structure. Diet, education, income, language, religion — all of them have "genes" in exactly the sense that chopsticks do.

## Reading a result properly

Ask three questions of any genetic association you meet:

1. Was ancestry controlled for, and how?
2. Has it replicated in an independent sample?
3. How large is the effect, in units a person could notice?

Most claims that reach the public fail at least one. The chopstick example survives thirty years later because it is the cleanest possible demonstration that a result can be entirely correct and entirely meaningless at the same time.

If you want to see the underlying structure for yourself, the [Ancestry app](https://www.geneplaza.com/app-store/58) reports where your genome sits relative to reference populations — the very axis that has to be controlled for before any association means anything.

Related: [what an ancestry estimate actually measures](/blog/en/what-is-genetic-ancestry/), and [why small percentages are usually not ancestors](/blog/en/small-ancestry-percentages/).
