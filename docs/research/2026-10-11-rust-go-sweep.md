# qa-review against pr-review-toolkit on Rust, Go and the unbound DS digest commit

**Date:** 2026-10-11 · **Issues:** #217

Ten commits that later needed a security advisory (five hickory-dns, five CoreDNS) and the
unbound commit that introduced the DS digest heap overflow, each reviewed against its parent tree.
qa-review is dream-team `2a416c9` (architect with the ownership list, performance, sre and
test-coverage lenses); pr-review-toolkit runs all six of its agents. Opus at effort high, headless
`claude -p`, one run per commit, graded from the raw per-agent reports on the commits' ledgers:
11 target rows (weight 10 each) and 17 further rows, weighted recall out of 100.

| Reviewer | Quality | Target rows found | Cost, USD, 11 runs | Wall clock per run, s |
|---|---|---|---|---|
| qa-review | 94.5 | 10/11 | 28.60 | 233 |
| pr-review-toolkit | 92.9 | 10.5/11 | 44.61 | 267 |

## qa-review matches pr-review-toolkit at 64% of the cost

The two score the same on 8 of 11 commits. Only qa-review found two CoreDNS rows: the PROXY
protocol setting reaches only the first listener of a server block, and the external zone's SOA
serial does not change with headless pod IPs. Only pr-review-toolkit rated the unbound DS digest
overflow critical; qa-review's sre and performance lenses traced the same unchecked write and
rated it low (half credit). With one run per commit, a one-row gap on a commit is within run
noise; on unbound pull request 1525
([qa-review against pr-review-toolkit](2026-10-11-qa-review-vs-pr-review-toolkit.md)), runs of
one variant spread 11-14 points.

## On defect rows the lenses overlap; none adds much to the other three

| Lens | Quality alone | Marginal | Share of lens cost |
|---|---|---|---|
| architect-reviewer | 89.6 | 2.2 | 28.6% |
| sre-engineer | 87.9 | 0 | 23.8% |
| performance-engineer | 75.8 | 2.2 | 19.6% |
| test-coverage-reviewer | 59.3 | 0 | 27.9% |

Marginal is the score lost when the lens is removed from the run. Cost share is token-weighted
over the 11 runs. The architect and sre lenses alone each score near the toolkit's total. The
four lenses start together, so a run's wall clock is its slowest lens plus about 60 s; dropping a
lens cuts cost, not wall clock, unless it is the slowest.

## The performance lens stays

It found one row no other lens found: the CoreDNS DNS over QUIC (DoQ) reader never reads a stream
to its end, so stream credit is not returned and a connection stops opening streams after the
256-stream limit the commit adds.

## The ownership list is not isolated here

The sweep has no run without the list. The architect lens carrying it is the strongest alone and
found one row no other lens found: hickory-dns loses the same-server UDP-to-TCP fallback once one
server entry holds both transports. On pull request 1525 the list added two ownership rows in 3
of 3 runs.

## The test-coverage lens earns its cost on test gaps

This sweep's ledger had no test-gap rows; scored with them, the lens adds 9.1-20.9 points per run
([test-coverage lens recheck](2026-10-11-test-lens-recheck.md)).

## Open: qa-review under-rates the DS digest overflow

Tracked in #222.

## Ruled out

- Dropping the performance lens: it holds a unique row here and 0-6.1 points on pull request
  1525.
