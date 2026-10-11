# code-reviewer's out-of-diff tracing on the CVE-introducing unbound commits

**Date:** 2026-10-11 · **Issues:** #218

qa-review ran on three unbound commits that introduced a CVE, each against its parent tree: t1
`5c6f56f8f`, t2 `f5dcd84d2` and t4 `3163a9312`. 11 runs used dream-team `0fe04e7` (architect with
the ownership list, performance, sre and test-coverage lenses) and 2 used `77c7c5c` (before the
test lens), Opus, headless `claude -p`, $36.12 in total, graded from the raw lens reports on the
CVE-introducing commits' ledger.

## qa-review finds C10 and C2; C3 stays at half credit

In earlier toolkit runs, code-reviewer found three memory-safety rows qa-review missed: C3 with
Opus at effort xhigh, C10 and C2 with Fable at effort high.

- C3, t1: the DNAME TTL is written into the received packet; a compression pointer into it
  overflows the heap.
- C10, t2: use-after-free after the auth-xfr callback deletes the comm point.
- C2, t4: the first RR's space check leaves out the owner name; heap overflow.

| Row | `0fe04e7`, effort high | `0fe04e7`, effort xhigh | `77c7c5c`, effort high |
|---|---|---|---|
| C3, t1 | ◐ ◐ | ◐ | |
| C10, t2 | ● ● | ● | |
| C2, t4 | – – ● ● | ● | ● ● |

● names the defect and its impact, ◐ flags the hunk but misses the impact, – not found.

The performance or architect lens found C10 in 3 of 3 runs. The gap on C2 between 2 of 4 runs at
`0fe04e7` and 2 of 2 at `77c7c5c` is run noise at these counts. C3 got half credit in all three
runs. Every lens flagged the write into the received packet, then called it safe because the
buffer is restored between callbacks. No lens checked whether `rdata_copy` decompresses the names
again into buffers sized at parse time.

## The trace comes from the orchestrator's focus lines, not code-reviewer's text

code-reviewer's agent file asks for bug detection in general and names no trace outside the diff.
pr-review-toolkit's orchestrator read the diff and the code around it, then wrote diff-specific
questions as focus lines into each agent's prompt. For t1 it asked: "ttl_data of the DNAME rr
points into the wire packet buffer: is writing into it safe (validator, RRSIG original TTL, later
reparse, anything reading the pkt after scrub)?" code-reviewer answered with the
compression-pointer overflow. For t2 the orchestrator asked whether the re-read can run after the
handler is reclaimed, and code-reviewer went on to the auth-xfr callback that frees the comm point
(C10). The t4 prompt named no space check, and C2 sits inside the diff, so C2 needed no trace
outside it.

## Ruled out

- A separate agent for the trace: code-reviewer's agent text has no trace cue; its C3 and C10
  came from focus lines in its prompt.
- Diff-specific questions per lens from qa-review's main session: C3 still at half credit in 3
  of 3 runs (#226, [diff questions in lens prompts](2026-10-11-diff-questions-in-lens-prompts.md)).
