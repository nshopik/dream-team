# qa-review without the performance lens

**Date:** 2026-10-11 · **Issues:** #224

qa-review with three lenses (architect-reviewer, sre-engineer, test-coverage-reviewer; branch
`issue-224-drop-perf-lens` at `f9e2d01`, carrying the moved cue lines) against four lenses
(dream-team `main` at `46be514`, whose skill and agents match the #217 runs at `2a416c9`). Opus
at effort high, headless `claude -p`, graded per lens from the raw lens reports on the
[Rust and Go sweep](2026-10-11-rust-go-sweep.md) ledger and the unbound pull request 1525
ledger. Every benchmark diff changes code, so none runs the docs-only skip of the test lens.

## Rust, Go and unbound commits: three lenses lose no row at 80% of the cost

| Roster | Quality | Cost, USD, 11 runs |
|---|---|---|
| Four lenses (#217 run) | 92.5 | 28.60 |
| Four lenses minus performance | 90.3 | - |
| Three lenses | 94.6 | 23.02 |

One run per commit. Quality is out of 186 weight: the #217 rows plus E81, a new row from these
runs. The three-lens runs hold every row the four-lens run holds. E81 is a second CoreDNS DNS
over QUIC (DoQ) stream-credit defect: when the plugin chain writes nothing, the server never
sends FIN, so the stream's credit is never returned.

## Pull request 1525: three lenses are within run noise of a same-day control

| Run | Four lenses, same day | Four minus performance | Three lenses |
|---|---|---|---|
| 1 | 79.4 (9/11 critical) | 74.7 | 77.3 (8/11) |
| 2 | 73.2 (7/11) | 66.7 | 68.4 (7/11) |
| 3 | 76.3 (7/11) | 76.3 | 65.8 (6/11) |
| Mean | 76.3 | 72.6 | 70.5 |
| Cost per run, USD | 8.57-9.18 | - | 6.62-7.02 |

The gap is 5.8 points on runs that spread 5-7 points. The same four-lens roster scored a mean of
80.5 in the #216 variant runs, so comparing against those runs alone would have shown a 10-point
gap, of which about 4 points was run-to-run drift. In the control, the performance lens alone
found I18 (the write thread reads `cfg->chrootdir` that fast_reload freed) in 2 of 3 runs, plus I4
(fast_reload joins a thread under the xfr lock) and P6; this is what the three lenses give up.

## The sre stream-credit cue finds E45

sre-engineer found E45 on CoreDNS g3 in 3 of 3 runs and E81 in 2 of 3. Before the cue, only the
performance lens found E45, in 2 of 3 runs (#221).

## The architect key-derived-field cue finds the stale rrset hash

On the held-out unbound case (`77f78152`: the synthesised wildcard answer keeps the cached
rrset's hash after its owner name changes), architect-reviewer reported the stale hash in 3 of 3
runs: once with the one-bin chain and CPU cost, twice as a misfiled cache entry.

## Generic cue wording did not do better

A rewording of each cue as a class (anything taken from a peer or pool is given back on every
exit path; a derived field is recomputed on every write to its sources) found E45 in 2 of 3 g3
runs plus one fix-only, E81 in 1 of 3, and the stale hash as 3 partials. #239 tracks testing it
on the cases only the generic wording names.

## Ruled out

- Comparing against the #216 four-lens runs from an earlier session: day-to-day drift of about
  4 points, larger than the change being measured.
- The generic cue wording, for now (#239).
