# Diff-specific questions in qa-review lens prompts

**Date:** 2026-10-11 · **Issues:** #226, #225

A qa-review variant at dream-team `5987260` had the main session read the diff and the code
around each hunk, then write 3-6 questions per lens, each naming a `file:line`, into the lens
prompt under `Questions from the diff:`. It ran 3 times each on unbound t1 (C3, CVE-2026-82717),
t3 (C1, CVE-2026-81642) and pull request 1525 at Opus effort high in headless `claude -p`, $44.60
in total; qa-review is unchanged since the #218, #222 and #216 runs, which give the main columns.

## The questions do not find C3 on t1

Every lens in 3 of 3 runs judged the DNAME TTL write into the packet safe, as on main; 10 of the
12 lenses flagged it. The main session asked about the write in every run, mostly about which
consumers read the packet after scrub:

> iterator/iter_scrub.c:297 — writing the DNAME TTL into rrset->rr_first->ttl_data mutates the
> upstream wire packet in place; which consumers read that buffer after scrub_normalize (other
> serviced_query callbacks ..., dnstap, cachedb, validator) and can any see the rewritten value?

The run 1 architect question listed "re-parse" among those readers, as pr-review-toolkit's
question that found C3 named "later reparse", and that lens still got half credit. No lens
checked whether the names in the packet, decompressed again later, still fit the sizes computed
at parse time.

On t3 the merged report rated C1 critical in 2 of 3 runs, against 1 of 3 on main and 2 of 3 for
pr-review-toolkit: within run noise.

## Every lens scores lower on pull request 1525

The four lenses together scored within noise, but each lens alone lost 6-9 points:

| Run | main | with questions | main crit | with questions crit |
|---|---|---|---|---|
| 1 | 86.5 | 74.5 | 10 | 7 |
| 2 | 79.2 | 88.5 | 8 | 10 |
| 3 | 75.9 | 72.4 | 7 | 6 |
| Mean | 80.5 | 78.5 | 8.3 | 7.7 |

| Lens | main mean | with questions mean |
|---|---|---|
| architect | 54.4 | 46.1 |
| performance | 26.5 | 19.8 |
| sre | 57.5 | 51.8 |
| test-coverage | 34.3 | 24.9 |

The test-coverage and performance lenses scored below every main run in all three runs. C10, the
critical use-after-free across a fast_reload swap, was found in 2 of 3 main runs and in none with
questions. I20, another critical fast_reload use-after-free, was found once with questions and
never on main. N11, N24, N26 and T5, each found in 1 of 3 main runs, were lost; I14 was gained.
Of the 72 questions, 64 pointed at a ledger row: the lenses answered them and reported less
beyond them. A run cost $8.86-10.24, against $8.71-9.33 on main.

## Few questions are wrong, and a wrong one costs a paragraph, not a row

Out of 190 questions, 8 were wrong: 4 of 118 on t1 and t3, 4 of 72 on pull request 1525. Three
of the t3 ones asked whether `log_assert` compiles out in release builds; in unbound it never
does. 7 of the 8 were refuted in one bullet or ❓ paragraph; the t3 run 2 sre lens repeated the
`log_assert` premise as fact in a ❓. No lost row traces to a wrong question: C10 was also missed
in the pull request 1525 run with no wrong question, and the t3 sre lens rated C1 critical in 2
of the 3 runs where it got one.

## Diff questions narrowed the lenses, which supports #225's dedicated lens

#225 keeps the domain check a dedicated lens, on the risk that a check appended to every lens
prompt is diluted. No run here sent a domain check as questions. These runs show that lenses
given extra diff-specific questions answer them and lose breadth on pull request 1525; by
inference, a domain check sent the same way would cost the same, which favours the dedicated
lens.

## Ruled out

- Main-session questions per lens as a qa-review step: C3 not found, every lens lower on pull
  request 1525.
