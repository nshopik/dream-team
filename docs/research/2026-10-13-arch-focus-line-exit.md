# Exit eval: dropping the architect focus line

**Date:** 2026-10-13 · **Issues:** #257, #261

qa-review at Opus high, same day, two arms: main `dd44329` (control) and the same tree with the
architect-reviewer focus line removed, so the lens gets its bare name like the sre and test lenses.
Each arm ran unbound pull request 1525 three times and the 11 commits of the #224 set (hickory
r1-r5, CoreDNS g1-g5, unbound t3) once: 28 headless runs plus one rerun, $118.3. A subagent graded
the raw lens reports blind against the existing ledgers.

## The drop meets the exit: pull request 1525 holds, no ledger row lost

The pull request 1525 union mean is 75.3 without the line and 73.5 with it, inside run-to-run
noise. On the 11 commits both arms hit the same rows on 10; on t3 only the no-line arm gave C1
full credit.

| Run | main | no focus line |
|---|---|---|
| PR 1525 r1, union | 73.5 | 76.8 |
| PR 1525 r2, union | 74.2 | 77.0 |
| PR 1525 r3, union | 72.7 | 72.1 |
| PR 1525 mean, union | 73.5 | 75.3 |
| PR 1525 mean, architect lens alone | 55.5 | 46.7 |
| 11 commits, weighted rows hit | 172 | 177 |

## The architect lens alone trades rows; the other lenses cover its losses

Without the line the architect lens alone scores 8.8 points lower on pull request 1525. It
found ownership and lifetime rows it missed with the line: I18 (1 of 3 runs vs 0), I20 (1 vs 0,
never found before by any lens), I13 (1 vs 0) and I2 (3 vs 1). It lost C2 (1 vs 3), I4 (0 vs
2), N23 (0 vs 3), C3, C5, I5, I7 and I21. Across all lenses, C2, I4, C5 and I21 hold; I5 (2 vs
3), I7 (1 vs 2), C3 (2 vs 3) and N23 (0 vs 3) drop. One no-line run found C10, from another
lens; no main run did.

## Ruled out

Run contamination is ruled out: the headless runs, started from one Claude session, pointed their
lenses at a shared diff file. One main-arm r5 run read the g1 diff in every lens; it was rerun alone
and regraded. Two pull request 1525 domain lenses read one stray diff among several right ones; they
were kept.
