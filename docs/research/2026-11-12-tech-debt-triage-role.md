# The tech-debt triage role

**Date:** 2026-11-12 · **Issues:** #440

This note checks the `tech-debt-triage` skill as shipped in #431 (main `eaa2ff1`) against outside
sources on technical debt: books, engineering-org write-ups and papers. The skill's judge eval
(`skills/tech-debt-triage/evals/run.sh`, Fable, case `dream-team-66a2f62`) scored 8/10 and 9/10
after tuning. C7 (review-bench METHODOLOGY duplication) flipped between Skip and Act now across
runs. C8 (jit-context fixed `/tmp` marker, expected Later) came back Act now on both runs.

## Role intro for the skill

The sources agree on the role. The intro below states it for the judge brief:

> You triage technical debt. Debt is code that no longer fits the task it serves. Its principal is
> the cost of the fix. Its interest is what the code costs while it stays: defects users hit, and
> time lost on each change to it. Code that changes often charges the most interest; stable code
> charges little, even when it is ugly. Your job is to pay the debt whose interest exceeds its
> principal now, schedule the rest, and drop claims that are not debt at all. Most candidates you
> get are overstated: verify each one in the code before you rate it.

## The role: engineers near the code name debt items; the item is the hand-off

Kruchten, Nord and Ozkaya's *Managing Technical Debt* splits the work into identifying debt items,
analysing their cost, and deciding per item whether to eliminate, reduce or mitigate it. The SEI
records each item as a name, a description and its consequences if left, with candidate
remediations, and keeps the items in a registry. Engineers and architects write the items; the
owner of the backlog decides when to pay. Google (Jaspan and Green) treats debt as a human and
technical problem and surveys engineers on which kinds of debt hinder them.

The skill maps onto this: `architect-reviewer` identifies, the judge analyses and decides, and an
Act now item becomes an issue in the tracker, which is the registry. The judge's evidence line
plays the role of the item's consequence. No gap.

## Criteria: interest against principal; the three pillars split interest by kind

Every source rates an item by its interest against its principal. Cunningham's 1992 report defines
interest as the time spent on not-quite-right code. Tornhill measures it as change frequency: debt
in a hot spot is expensive, debt in stable code is low-interest and can be ignored. Fowler's
quadrant post says prudent debt in rarely touched code may be left alone. Lenarduzzi et al.'s
review of 44 studies finds 53 factors and no consensus, and notes that principal is rarely
estimated.

The pillars map onto interest. Quality is interest paid as defects. Readability is interest paid as
time per change. Performance is interest only where the code is too slow today, which the brief
already says. Principal is the brief's "lines and concepts the change adds against those it
removes".

## Criteria: a latent defect in a rare environment is Later unless its impact is severe

Risk-based prioritization (Boehm's likelihood × impact) gives a defect that only a rare
environment triggers low likelihood, so low interest. The fix waits unless the impact is data loss,
a security hole or a crash with no recovery. C8 is that case: a fixed `/tmp` path only fails on a
shared host, and the failure loses no data. The brief's "A defect counts before anyone hits it"
has no likelihood term, so the judge rates C8 Act now. Open: #442.

## Verifying a claim: the judge's blind code check matches the sources

Detection by itself has low precision. Expert validation in SmellBench found 63.1% of detected
architectural smells to be false positives. LLM detectors of self-admitted debt fail mainly on
precision. Souza et al. find LLMs reliable on structural smells (Large Class, Long Method) and
noisier on complex ones. ACE keeps an LLM refactoring only when the target smell is gone and code
health has not dropped.

Practices that carry over to an LLM judge, all already in the skill: a separate judge verifies
each claim in the code; the brief warns that about half of the claims are overstated; an item must
name what the change removes. No gap.

## Measuring verdict accuracy: expected verdicts are one rater's labels, and a verdict needs 3 runs

No ground truth exists for debt prioritization. Lenarduzzi et al. find no agreed factors, and in
one industrial case study five raters agreed at Cohen's kappa 0.29 on business value. The eval's
expected verdicts are therefore the maintainer's labels, not facts. Keep only cases whose label
the evidence in the code settles.

LLM judges are not self-consistent. Haldar and Hockenmaier ("Rating Roulette", EMNLP 2025
Findings) find low intra-rater reliability. Temperature 0 does not remove the variance, and a
stable verdict can still be wrong. The practitioner advice is at least 3 runs per case, with
agreement reported. `run.sh` runs each case once, so C7's flip shows up only when a person
compares runs. Open: #443.

## Ruled out

- Google's ten-category debt taxonomy: categories describe kinds of debt, not how to rate one
  candidate; the full list was not reachable from public summaries.
- Business-value weighting (Tracy): needs product-owner input the skill does not have.

## Sources

- [Cunningham, The WyCash Portfolio Management System, OOPSLA 1992](https://c2.com/doc/oopsla92.html)
- [Fowler, Technical Debt Quadrant](https://martinfowler.com/bliki/TechnicalDebtQuadrant.html)
- [Kruchten, Nord, Ozkaya, Managing Technical Debt](https://www.oreilly.com/library/view/managing-technical-debt/9780135646052)
- [SEI, Experiences Documenting and Remediating Enterprise Technical Debt](https://sei.cmu.edu/blog/experiences-documenting-and-remediating-enterprise-technical-debt/)
- [Jaspan, Green, Defining, Measuring, and Managing Technical Debt](https://research.google/pubs/defining-measuring-and-managing-technical-debt/)
- [Tornhill, SREcon24 EMEA slides](https://usenix.org/system/files/srecon24emea_slides-tornhill.pdf)
- [Lenarduzzi et al., Technical Debt Prioritization: State of the Art](https://arxiv.org/abs/1904.12538)
- [Business-Driven Technical Debt Prioritization: An Industrial Case Study](https://arxiv.org/abs/2010.09711)
- [SmellBench: LLM agents on architectural smell repair](https://www.roboticscenter.ai/research/papers/smellbench-evaluating-llm-agents-on-architectural-code-smell-repair-2605)
- [Souza et al., LLMs for code smell detection](https://arxiv.org/abs/2601.09873)
- [Self-admitted technical debt in test code](https://arxiv.org/abs/2510.22409)
- [ACE: validated LLM refactorings](https://arxiv.org/abs/2507.03536)
- [Haldar, Hockenmaier, Rating Roulette](https://aclanthology.org/2025.findings-emnlp.1361)
- [MLflow, judge consistency](https://mlflow.org/articles/judge-consistency-llm/)
