# Exit eval: dropping the architect focus line

**Date:** 2026-10-13 · **Issues:** #257, #261

The eval ran qa-review at Opus high, same day, in two arms: main `dd44329` (control) and the same
tree with the architect-reviewer focus line removed, so the lens gets its bare name like the sre
and test lenses. Each arm ran unbound pull request 1525 three times and the 11 commits of the #224
set (hickory r1-r5, CoreDNS g1-g5, unbound t3) once: 28 headless runs plus one rerun, $118.3. A
subagent graded the raw lens reports blind against the existing ledgers; the ledger rows (C, I,
N, T and P IDs) live in the maintainer's local eval harness, outside the repo. A union score
counts a row when any lens in the run finds it.

## The drop meets the exit: the pull request 1525 union holds, no row lost on the 11 commits

The pull request 1525 union mean is 75.3 without the line and 73.5 with it, inside run-to-run
noise. On the 11 commits both arms hit the same rows on 10; on t3 only the no-line arm gave C1
full credit. The milestone exit's row clause (no row the control holds in 2 of 3 runs lost) is not
met on pull request 1525: I7 2/3 to 1/3, I9 2/3 to 1/3, N9 3/3 to 1/3, N23 3/3 to 0/3. The
maintainer waived it because no critical row was lost and critical rows found per run rose from 9,
10, 8 to 10, 11, 10.

| Run | main | no focus line |
|---|---|---|
| pull request 1525 r1, union | 73.5 | 76.8 |
| pull request 1525 r2, union | 74.2 | 77.0 |
| pull request 1525 r3, union | 72.7 | 72.1 |
| pull request 1525 mean, union | 73.5 | 75.3 |
| pull request 1525 mean, architect lens alone | 55.5 | 46.7 |
| 11 commits, weighted rows hit | 172 | 177 |

## The architect lens alone trades rows; the other lenses cover its losses

Without the line the architect lens alone scores 8.8 points lower on pull request 1525. It found
ownership and lifetime rows it missed with the line: I18 (1 of 3 runs vs 0), I20 (1 vs 0, never
found before by any lens) and I13 (1 vs 0); it found I2 more often (3 vs 1). It lost C2 (1 vs 3), I4
(0 vs 2), N23 (0 vs 3), C3, C5, I5, I7 and I21. Across all lenses, C2, I4, C5 and I21 hold; I5 (2 vs
3), I7 (1 vs 2), C3 (2 vs 3) and N23 (0 vs 3) drop. One no-line run found C10, from another lens; no
main run did.

## Run contamination

The headless runs, started from one Claude session, pointed their lenses at a shared diff file. One
main-arm r5 run, whose lenses all read the g1 diff, ran again alone and was regraded. Two pull
request 1525 domain lenses read one stray diff among several correct reads; their grades stand.
