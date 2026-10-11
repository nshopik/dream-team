# How qa-review and pr-review-toolkit rate the unbound DS digest overflow

**Date:** 2026-10-11 · **Issues:** #222

Each reviewer ran three times on unbound target t3 (`7726691af`), the commit that introduced the
DS digest heap overflow (CVE-2026-81642: owner name plus DNSKEY rdata written into the 64 KiB
scratch buffer with no space check), at Opus effort high in headless `claude -p`. qa-review is
dream-team `15a5e88`, whose agents are unchanged since the #217 sweep, so the sweep's run counts
as run 1; pr-review-toolkit ran five of its six agents (its orchestrator skipped
type-design-analyzer), and grading used the raw per-agent reports.

| Reviewer | Merged report critical | sre lens critical | Cost per run, USD |
|---|---|---|---|
| qa-review main | 1/3 | 1/3 | 1.92-2.29 |
| qa-review with the sre bound line | 2/3 | 1/3 | 1.92-2.29 |
| pr-review-toolkit | 2/3 | — | 3.13-3.75 |

## pr-review-toolkit rates it critical in 2 of 3 runs, qa-review in 1 of 3

In the toolkit, code-reviewer rated it critical once and silent-failure-hunter once; the third run
rated it important. In qa-review, the performance and sre lenses rated it critical together in one
run; the other two runs rated it important. A one-run gap in three runs is run noise.

## The rating hinges on the bound the lens works out

Every lens on either side that rated it critical showed that owner name plus rdata can exceed
65536 bytes from the wire: a 65535-byte TCP reply whose DNSKEY owner name is a compression pointer
into its own rdata, or one with no question section. All but one lens that rated it lower stopped
at "the 64 KiB message limit keeps it in bounds", assuming the reply carries the owner name
uncompressed. The exception, test-coverage-reviewer in qa-review run 2, found the compression path
but rated it important, as a heap write only in builds without asserts.

silent-failure-hunter's own prompt says nothing about buffer bounds. The toolkit orchestrator
writes each agent a focus line after reading the diff, and in 3 of 3 runs it named the hunk for
code-reviewer and silent-failure-hunter: the scratch-buffer capacity, asserts, or malformed wire
data from the network. That gets the hunk read in every run, but silent-failure-hunter still rated
it critical only once. qa-review lens prompts carry repo context and a fixed focus, never the hunk;
in run 1 the context included "`log_assert` is always on" from the repo's `CLAUDE.md`. This
matches the focus-line finding of
[code-reviewer's out-of-diff tracing](2026-10-11-code-reviewer-out-of-diff-trace.md).

## The sre bound line does not change the sre lens's rating

The sre lens rated it critical in 1 of 3 runs with the line, as on main. The line, added to
sre-engineer as an "Also check:" item with sre-engineer's focus unchanged, asks for the largest
value peer-controlled input can produce and a check of each fixed-size buffer it reaches. The sre
lens followed it in 3 of 3 runs, but in two it assumed an uncompressed owner name and found the
overflow unreachable. The merged report's second critical came from the architect and
test-coverage lenses.

On unbound pull request 1525 the line is within noise (main and toolkit columns are the #216 runs
of the same agents):

| Run | main | with the sre bound line | pr-review-toolkit |
|---|---|---|---|
| 1 | 86.5 | 77.4 | 72.7 |
| 2 | 79.2 | 82.4 | 82.0 |
| 3 | 75.9 | 80.8 | 68.1 |
| Mean | 80.5 | 80.2 | 74.3 |

The sre lens alone averaged 54.0 against 57.5 on main. Main alone found N11 (a performance row),
in one run; the line's runs alone found I12, I14 and N12, each in one run. The line is not
shipped.

## Ruled out

- The sre bound line: sre lens rating unchanged on t3, within noise on pull request 1525.
- Diff-specific questions per lens from qa-review's main session: merged report critical in 2 of
  3 runs, within noise (#226,
  [diff questions in lens prompts](2026-10-11-diff-questions-in-lens-prompts.md)).
