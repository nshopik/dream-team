# qa-review against pr-review-toolkit on unbound PR 1525

**Date:** 2026-10-11 · **Issues:** #216, #217

Unbound pull request 1525 (branch `auth-load-thread`, a C threading change), graded on its
58-row ledger: weighted recall out of 100, 11 criticals. Opus at effort high, headless `claude -p`,
three runs per variant. qa-review is dream-team `77c7c5c` (architect, performance and sre
lenses); pr-review-toolkit runs all six of its agents. Each run is graded from the raw per-agent
reports, not the merged output.

| Run | qa-review | pr-review-toolkit | qa-review + test lens + ownership list |
|---|---|---|---|
| 1 | 75.2 (8) | 72.7 (8) | 86.5 (10) |
| 2 | 69.3 (8) | 82.0 (9) | 79.2 (8) |
| 3 | 80.8 (9) | 68.1 (7) | 75.9 (7) |
| Mean | 75.1 | 74.3 | 80.5 |
| Cost per run, USD | 7.2-7.4 | 12.2-13.1 | 8.7-9.3 |

Criticals found in brackets. Runs of one variant spread 11-14 points.

## qa-review and pr-review-toolkit tie on this pull request

Means differ by under one point against a 5.7-7.0 standard deviation. qa-review costs about 60% as
much. Rows only the toolkit found in most runs were test gaps (pr-test-analyzer), stale comments
(comment-analyzer), and ownership defects (type-design-analyzer, code-reviewer). Rows only
qa-review found were performance costs and two sre rows.

## The toolkit's extra rows come from its orchestrator's focus lines

Two eval-only agents were built from the toolkit: a failure-path agent (silent-failure-hunter,
type-design-analyzer's ownership checks, and the orchestrator's focus lines) and a test-coverage
agent (pr-test-analyzer plus focus lines). Run alone, three times each, they scored 49.6-61.4 and
35.1-40.7. The test agent recovered the toolkit-only test rows in every run. The failure-path
agent overlapped the sre lens: in one run it added no row qa-review lacked.

## A test lens and an ownership list close the gap

qa-review with test-coverage-reviewer as a fourth lens, and the failure-path agent's ownership
list appended to architect-reviewer, scored 80.5 on average (table). The architect lens rose from
47.5 to 54.4 and reported both ownership rows, one critical, in 3 of 3 runs. The overall gain is
about one standard deviation; the architect gain is the steady part. Removing the test lens from a
run cost 3.5-7.5 points.

## The performance lens, not the architect lens, is weakest here

Points lost when each lens is removed from a qa-review run: sre 20.6-23.9, architect 6.6-8.9,
performance 0-6.1. #217 decides whether to keep it, on Rust and Go commits where this pull
request's C threading bias does not apply.

## Open: recheck on other languages and on the DS digest commit

Tracked in #217: the shipped roster on 10 Rust and Go commits, and on the unbound DS digest commit
that #215's sre line lost.

## Open: code-reviewer's out-of-diff memory-safety tracing

Not measured here; tracked in #218.

## Ruled out

- A failure-path agent of its own: its rows overlap the sre lens, and its ownership list works
  inside architect-reviewer.
- Porting comment-analyzer: its rows are nits, under 2 points in total; docs-reviewer covers stale
  comments.
- Porting code-simplifier: no ledger row; the simplify pass covers it.
- Porting code-reviewer's text: generic, with no domain cues; its rows on this pull request came
  from the orchestrator's focus lines.
