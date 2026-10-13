# Lens prompts: contradiction audit, miss critique and cue wording

**Date:** 2026-10-13 · **Issues:** #239

The audit covers the architect-reviewer and sre-engineer prompts as a qa-review lens receives them
(agent body, focus line, rules block) at dream-team `main` `5b20469`. The audit and the critique
ran as subagents over the prompts and over the raw lens reports of eight Opus runs on unbound pull
request 1525 (#224 at high, #239 effort runs at xhigh and max). The A/Bs ran headless `claude -p`
at Opus high, graded per lens from the raw lens reports. The ledger rows (C, I, N, T and P IDs)
live in the maintainer's local eval harness, outside the repo.

## The audit found one conflict: the architect focus line

The qa-review focus line for architect-reviewer names boundaries, data flow, backpressure and
contracts, and leaves out the agent's ownership and invariants section (who frees each field, which
lock protects it, invariants under background work). It came over from the old qa-sec workflow,
whose generic agents needed steering. The architect-reviewer description covers ownership, locking,
invariants and contracts the code breaks; the sre-engineer description covers backpressure; neither
covers where docs and code disagree. The sre and test lenses already get only their bare names.
Nothing in the sre prompt contradicts another line. #257 tracks dropping the focus line.

## No prompt line suppressed a miss; each is a missing cue

| Row | Lens | Found in 8 runs | What the misses did |
|---|---|---|---|
| C10 | arch | 2 + 1 partial | Read the per-change stop, not the old set's free in unchanged code |
| I18 | arch | 2 | Read the reload's config copy, never asked which thread still reads it |
| I7 | sre | 4 | Reached the quit return, reported only its data and log effects |
| I13 | sre | 1 | Applied the waiter hang only to a thread that never started |
| I19 | sre | 2 | Read the callback, never noted the persistent event fires again |

C10 and I18 share one root: fast_reload frees the old config and zone tree after an ack that
polls only worker threads. The critique proposes two architect cues and three sre cues, one per
row, all derived from pull request 1525, so a rerun there proves nothing; #257 needs a held-out
case for each.

## Open: the sre stream-credit cue may anchor slot leaks

Since the cue shipped (#224), sre found I13 in 1 of 8 runs (5 of 9 before) and I19 in 2 of 8
(9 of 9 before). Two reports file slot leaks under the cue's wording instead. The same-day pair
was within noise, and the cue carries the CoreDNS E45 hit. #259 ran sre without it and kept the
cue: with it the sre lens found the CoreDNS stream-credit leak in 3 of 3 runs, without it 0 of 3.

## The generic sre wording does not beat the current one

| Row | Generic, 3 runs | `5b20469`, #224 3 runs |
|---|---|---|
| I7 | 1 | 1 |
| I13 | 1 | 1 |
| I19 | 2 partial | 2 |
| sre lens score | 51.8 | 52.5 |

The generic cue names counted tokens taken from someone else; a file handle or a thread to join
is neither, so it does not reach I7 and reaches I13 only weakly.

## The generic architect wording ties on a held-out count

Held-out case: BIND 9 commit `99b4f01b33` adds a tuple count to its diff object, kept by hand,
while other code still moves tuples directly; a stale count aborts named on an assertion (fix
`115c1971cb`, merged 2026-09-03). Architect found it in 3 of 3 runs with the generic wording,
and 2 plus 1 partial with the `5b20469` wording. On the #224 stale hash case the `5b20469`
wording led (1 hit against 0). Both variants keep the `5b20469` count line, which already names
this case. No consistent win, so the `5b20469` wording stays.

## Ruled out

- Keyword trimming (MAINTAINING.md, "Building agents").
- Both generic cue wordings.
- Extending the architect focus line with the ownership section: the misses already applied
  that section's lines.

Eval caveat: in headless eval runs qa-review has no scratchpad for its diff file (#229), so there
the lens prompt says to run `git diff`, which a lens cannot. The shipped skill writes the diff to a
scratchpad file and passes its path. Every run here and in #224 shares the caveat.
