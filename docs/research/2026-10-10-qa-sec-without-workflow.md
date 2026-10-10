# qa-sec without the Workflow tool

**Date:** 2026-10-10 · **Issues:** #203, #207

`/dream-team:qa-sec HEAD^` on the thanos eval case (thanos-io/thanos `7ceeab15`, base `b255f373`),
dream-team at `ae762cc`, Claude Code 2.1.296. Orchestrator opus, lenses sonnet, merge sonnet except
in B, default four lenses, three headless `claude -p` runs per variant. Four variants: the shipped
workflow (W); the main session fans the lenses out with the Agent tool in one message, then one
`sonnet` agent merges (A); one `sonnet` coordinator agent fans out, merges and returns the merged
list (C); the main session fans the lenses out with the Agent tool in one message, then merges and
renders them itself on opus, with no merge agent and no report file (B). A, B and C replace only
qa-sec step 4, with the same focus, rules and merge text as the workflow; B, run after #203 merged,
also drops the step-5 report file. A `sonnet` judge mapped each raw lens finding to a merged item
per run; one run's mapping was checked by hand.

| Run | W | A | C | B |
|---|---|---|---|---|
| Raw findings (judge), runs 1/2/3 | 35 / 32 / 28 | 29 / 33 / 30 | 29 / 27 / 30 | 31 / 29 / 26 |
| Merged items | 19 / 16 / 16 | 19 / 18 / 15 | 15 / 14 / 16 | 20 / 18 / 17 |
| Findings dropped | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| Cost, USD | 1.62 / 1.56 / 1.60 | 2.23 / 2.04 / 2.09 | 1.77 / 2.28 / 1.80 | 1.76 / 1.26 / 1.35 |
| Orchestrator output tokens | 4.3K / 4.1K / 4.3K | 27.2K / 27.8K / 27.9K | 10.4K / 15.5K / 10.8K | 10.7K / 7.5K / 8.6K |
| Wall time, s | 159 / 285 / 156 | 334 / 309 / 310 | 271 / 190 / 735 | 160 / 138 / 165 |

## The main-session merge (B) replaces the workflow

B drops nothing, costs about the same as W ($1.26-1.76 per run, reading low by up to about $0.2,
against W's $1.56-1.62), and runs in 138-165 s against W's 156-285 s. It needs no Workflow
tool, no merge agent and no report file. In run 1 the lenses ran in the background and the main
session read code and set a wakeup while it waited, which added about $0.4.

## No variant dropped a finding

Every finding a lens reported reached a merged item or a question in all twelve runs, about 360
raw findings in all. The judge's one `MISSING` (W run 2) was a candidate the security-review
lens had itself "considered and dropped", not a finding. Every raw lens report in the saved
report matched the lens agent's own reply verbatim in W, A and C. The only merge
collapse on record is still the one in the earlier eval sweeps: a sonnet merge that kept 1
item of about 11, from haiku lenses.

## The workflow's floor check never fired

The floor check (merged items below the largest lens's count) never fired: the largest lens count
was 8-12 and the merge kept 14-19 items. It catches a collapse like the one on record, and nothing
finer. Its regex also undercounts: it missed one or two numbered or heading-style findings from the
architect or sre lens in 8 of 9 runs. A `<lens>#n` source-id check would catch a partial drop, but
no partial drop occurred in about 360 findings, so it would guard a failure not yet seen. #207
deletes the floor check with the workflow; B has no check. If one is built, the lens should write
the ids itself in its output line: the regex cannot number findings reliably.

## A and C render without schema enforcement

All nine W, A and C merged lists had every required field, and every severity and theme was one of
the allowed values. All nine runs rendered every merged item under the step-6 headings. One A merge
set `coveredBy` to `#4` and `#6` with no issue list given; the main session caught it and cleared
both. The workflow schema would not have caught it: `coveredBy` is a free string there too.

## The coordinator misroutes or stalls under `claude -p`

The coordinator's lenses ran in the foreground in run 1 only. In runs 2 and 3 they launched in
the background:

- Run 2: the coordinator handed back an empty merge three times before any lens finished. The
  lens reports then went to the main session, which collected them and merged on opus itself.
- Run 3: the coordinator waited in a nine-minute `sleep` loop over the task output files while
  its lens reports sat queued, then merged them: 735 s against 271 s for run 1.

A coordinator that returns only the merged list holds in one run of three.

## A sonnet merge agent costs more than the workflow

W cost $1.56-1.62 per run, A $2.04-2.23, C $1.77-2.28. The gap is orchestrator output: in A
the opus main session writes the step-5 report by hand, all four raw reports and the merged
JSON, about 27K tokens; in W the workflow result is already on disk and the main session writes
about 4K. A, B and C costs read low by up to about $0.2: Agent-tool subagent transcripts record
almost no output tokens, where workflow agent transcripts record 13-15K. A's median wall time
was about twice W's (310 s against 159 s). Runs ran three to six at a time, so wall times carry
contention noise.

## Ruled out

- The Agent-tool fan-out (A): it loses no findings, but costs about a third more per run and
  doubles wall time on this case.
- The coordinator (C): background lens launches broke the hand-back in two runs of three.
