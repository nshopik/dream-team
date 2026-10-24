---
name: review-bench
description: >-
  Benchmarks qa-review on one pull request, and any other code reviewer the user names against
  it: runs each reviewer headless several times, builds a verified findings ledger from qa-review
  warm-up runs, grades every run against the frozen ledger, and prints a score table of mean
  quality, run-to-run sd, criticals found and noise tiers. Use when the user asks to benchmark,
  score, rank or compare code reviewers, review commands, models or effort levels against
  qa-review, or to measure a reviewer's recall on a pull request.
---

# review-bench

`<skill-dir>` below is this skill's base directory, as the harness prints it.

- Read `<skill-dir>/METHODOLOGY.md` and the usage header of `<skill-dir>/run.sh` before step 1.
- `run.sh` runs, grades and scores; this skill covers the calls it cannot make.
- Run every `run.sh` call with Bash `run_in_background`.
- Run `run.sh` calls on one `<out>` one at a time: wait for each to finish before the next; use
  `P` for parallel runs, and parallel grades on a frozen ledger, inside one call.
- Before step 3 and before reporting, check every `<out>/<run>/marks.txt` exists and is non-empty;
  if one is not, rerun the same `run.sh` command, which regrades only the ungraded runs.

## 1. Pick the pull request

- Pick a pull request in a public repo whose diff holds real defects and fits one review run.
- Clone the repo outside the output directory and fetch the head:
  `git fetch origin pull/<n>/head`.
- Read `baseRefOid` and `headRefOid` from
  `gh pr view <n> -R <owner>/<repo> --json baseRefOid,headRefOid`.
- Use `git merge-base <baseRefOid> <headRefOid>` as `<base-sha>`, `<headRefOid>` as `<head-sha>`.
- Run `git checkout --detach <head-sha>` in the clone; step 5 checks candidates against it.
- Pick an output directory `<out>` outside the clone; every step below uses the same one.

## 2. Warm up the ledger

- Name a qa-review reviewer file `<out>/qa-<effort>.txt` and its prefix `QA-<EFFORT>`, so its run
  directories read `QA-HIGH-r1`, `QA-MAX-r1`.
- Write `<out>/qa-high.txt` as `QA-HIGH:lenses /dream-team:qa-review {base}`.
- Write `<out>/qa-max.txt` as `QA-MAX:lenses /dream-team:qa-review {base}`.
- Run `N=3 EFFORT=high <skill-dir>/run.sh <clone> <base-sha> <head-sha> <out>/qa-high.txt <out>`.
- Then run `N=2 EFFORT=max <skill-dir>/run.sh <clone> <base-sha> <head-sha> <out>/qa-max.txt <out>`.
- These five runs are the warm-up; no stop rule ends it earlier or later.
- A warm-up run with `early-exit` and a non-zero `exit=` in `stats.txt` → delete `<out>/<run>` and
  rerun its command before step 3.
- The score tables these calls print grade against a growing ledger; they are not results.

## 3. Freeze the ledger

- Set `"frozen": true` in `<out>/ledger.json`; leave `version` at 1.
- Delete `<out>/QA-HIGH-r{1..3}/marks.txt` and `<out>/QA-MAX-r{1,2}/marks.txt`.
- Rerun the step 2 `qa-high.txt` command to regrade all five; the warm-up runs stay scored runs.

## 4. Run each reviewer the user named

- No reviewer named → skip to step 6; the table holds qa-review alone.
- qa-review at another effort → `<out>/qa-<effort>.txt` per step 2, run with `EFFORT=<effort>`.
- A reviewer named later → reuse the same `<out>` and run steps 4 to 6.
- Write each reviewer as a `<PREFIX>[:lenses] [model=<m>] [effort=<e>] <prompt>` line in a file
  under `<out>`; prefix is capital letters, digits and `-`, unique per reviewer; write a version
  `4-6`, never `4.6`.
- `:lenses` only for a reviewer whose subagents each return a report.
- Write the prompt so the reviewer reviews `<base-sha>..<head-sha>`; `{base}` alone is a base
  ref only to qa-review; another reviewer may read a bare SHA as one commit.
- Run `N=1` first and check its `report.md` covers the pull request's files before the rest.
- A reviewer differing only in model or effort needs its own prefix, such as `QA-OPUS-4-6`, and
  its own `model=` or `effort=` field; one `run.sh` call can hold all such reviewers.
- Then run `N=3` per reviewer; the rerun skips the first run.
- `run.sh` grades each new run against the frozen ledger and prints the score table.

## 5. Promote candidates

After each `run.sh` call from step 3 on:

- List `grep -h ^Candidate <out>/*/marks.txt`.
- Check each against the code: drop one that is refuted, pre-existing, already a row, or a
  duplicate of another candidate.
- A non-nit candidate survives → add every surviving candidate as a row per METHODOLOGY
  "Ledger file", and bump `version` by one.
- Only nit candidates survive → bump nothing; they wait for the next bump.
- On a bump, read each earlier run's `report.md` or `lenses/*.md` against the new rows only, per
  METHODOLOGY "Grading a run"; add the IDs each report or lens earns to its own scored line;
  existing marks stand.
- Rescore: `cat <out>/*/marks.txt > <out>/marks.txt`, then
  `python3 <skill-dir>/score.py <out>/ledger.json <out>/marks.txt`.

## 6. Read and report

- Reviewers in one tier are not ranked; their order is noise.
- With 3 runs a reviewer's sd is often 3 to 7 points; a mean gap inside that is not a result.
- Compare scores only within one ledger version.
- `early-exit` in a run's `stats.txt` scores 0; name the run.

```
- **Ledger:** <score.py summary line>; pending candidates: <n or none>
- **Table:**
  <score.py table as a markdown table, its columns and values verbatim>
- **Reading:** <tiers in words; gaps within sd called noise; rejected claims and $/run beside
  quality; a multi-lens reviewer's rejected claims are raw lens claims>
- **Early exits:** <runs, or none>
```
