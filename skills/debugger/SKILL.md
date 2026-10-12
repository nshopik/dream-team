---
name: debugger
description: >-
  Diagnoses errors, failing tests, unexpected behaviour, regressions and slow paths to a root
  cause: ranks falsifiable hypotheses, tests one per probe, runs lab-host probes through
  lab-runner, and reports the cause with its evidence; writes no fix. Runs in the main session,
  not inside dream-fixer-loop agents. Use when something is broken, failing, flaky or slower than
  before and the cause is unknown, e.g. "debug this", "why does this test fail", "find the root
  cause", "this regressed on the lab host". Not for one-shot lab work with nothing to explain (a
  perf gate, a deploy, a single check); dispatch lab-runner for that.
---

# debugger

- Diagnose only; stop at the report. The user, or the skill that loaded this one, decides the fix.
- Show the ranked hypotheses to the user before the first probe; do not wait for a reply.
- A failure that does not reproduce → rerun it several times and report the failure rate.
- Still zero failures → report `Root cause: unknown` with what you ran, and stop.
- A second round of hypotheses all refuted → report `Root cause: unknown` with the evidence so far.
- Before reporting, restore the checkout and the lab host to their state at load: `git bisect
  reset`, probe edits removed, debug builds replaced.

## Lab host

- Run each probe on a lab host as one `dream-team:lab-runner` dispatch; never ssh inline.
- Each brief names the hypothesis and its prediction, and asks for the result that decides it.
- Measure the base before any change, on the same host in the same lab-runner dispatch as the
  branch.
- Report measured numbers only, never estimates.

## Report

```
- **Root cause:** <cause, at its file:line, commit or config; or `unknown`>
- **Evidence:** <the probes and results that confirm it and refute the rest>
- **Fix check:** <the test or measurement that would confirm a fix>
```
