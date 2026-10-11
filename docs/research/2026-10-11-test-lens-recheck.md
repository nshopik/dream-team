# qa-review test-coverage lens on branches with test surface

**Date:** 2026-10-11 · **Issues:** #221

This note reruns qa-review on five of the commits from the
[Rust and Go sweep](2026-10-11-rust-go-sweep.md), picked for test surface: hickory-dns r2 (name
server connection tracking), CoreDNS g2 (edns0 revert), g3 (DNS over QUIC (DoQ) stream limit) and
g5 (headless external records) change test files; hickory-dns r3 adds a validation cache with no
tests. qa-review is dream-team `b9f1d2b`, whose skill and agents match the sweep's `2a416c9`, so
the sweep run counts as run 1; runs 2 and 3 are new. Opus at effort high, headless `claude -p`.
Graded per lens on the sweep's ledger, one new defect row the graders verified (E80), and 25
test-gap rows: 19 written from the diffs before any review was read, 6 verified from the reports.
Test-gap rows weigh 3, as on unbound pull request 1525. Quality is weighted recall out of 100;
marginal is the score lost when the lens is removed from the run.

## The test-coverage lens adds 9.1-20.9 points per run, all from test gaps

| Run | Quality | Test-gap recall | Test-gap recall without the lens | Lens marginal | Lens marginal, defect rows only |
|---|---|---|---|---|---|
| 1 | 89.1 | 88.0 | 42.0 | 20.9 | 0 |
| 2 | 83.0 | 80.0 | 50.0 | 13.6 | 0 |
| 3 | 85.2 | 74.0 | 54.0 | 9.1 | 0 |

It holds 6-13 test-gap rows per run that no other lens reports. Its marginal is above 5 on every
target in every run (5.2-31.0). The other lenses find some test gaps, mostly where a defect row
lives: the architect lens T2, T7, T13 and T22, the sre lens T1-T3 and T13. The lens costs 27.5%
of the lens spend over these 15 runs, weighted by token price.

## The sweep's zero marginal came from a ledger with no test-gap rows

The sweep's grade brief added extras only for bugs, so the lens could add to a run only by finding
a bug the other lenses missed. These commits introduced the advisory defects, and the advisory
defects C2, C3, C7, C8 and C10 each sit in a gap the branch's tests leave open (T1, T6, T10, T13,
T40).

## pr-test-analyzer beats any single lens run; the lens finds its test gaps across runs

pr-test-analyzer (one run per commit, from the sweep) scores 74.2 alone against the lens's
64.2-66.7. It holds 12 test-gap rows the other three qa-review lenses missed in run 1; the lens
finds all 12 in at least one of its three runs. Per run, on test-gap rows only, the analyzer holds
2-5 rows the lens lacks and the lens 0-1 the analyzer lacks. The analyzer also reports E45 and
C10 (half credit), which the lens never does; other qa-review lenses do. Swapping the lens for the
analyzer is not measured here.

## The lens stays in qa-review's roster

It is the main source of test-gap findings and adds no defect rows, here or in the sweep.

## Ruled out

- Dropping the lens: test-gap recall falls from 74-88 to 42-54.
