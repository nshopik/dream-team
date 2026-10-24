# Reviewer benchmark: methodology

Compares code reviewers on one pull request by weighted recall against a frozen, verified findings
ledger and, on a clean change, by false alarms.

## Ledger build

- Run qa-review as warm-up: 3 runs at effort high, then 2 at max.
- The grader verifies every row against the code before it enters the ledger.
- Freeze the ledger as version 1 after the fifth run: set `frozen` to true.
- After freezing, delete each warm-up run's `marks.txt` and rerun `run.sh` to regrade it.

## Frozen ledger

- Grade scored runs, the warm-up runs included, only against the frozen ledger.
- A verified claim outside the ledger becomes a candidate.
- A candidate counts only after a ledger version bump.
- After grading a batch of runs, bump `version` once if the batch left a non-nit candidate.
- A nit candidate alone bumps nothing; it waits and enters the ledger with the next bump.
- Any row change (added row, severity, plausible, nit) bumps `version`.
- On a version bump, regrade every earlier run against the new rows only; existing marks stand.
- Compare scores only within one ledger version.

## Ledger file

`ledger.json`:

```json
{"version": 1, "frozen": true, "rows": [{"id": "C1", "finding": "…", "location": "src/a.c:412",
  "severity": "critical", "plausible": false, "nit": false}]}
```

- `frozen`: true or false; default false (absent).
- `id`: the severity's letter (C, I, P, T, or N for minor) and the next free number.
- `severity`: `critical` (crash, use-after-free, deadlock, data loss, build break), `important`
  (risk, race, regression, silent failure), `performance`, `test` (test gap) or `minor` (bug or
  nit).
- `plausible`: true when every reviewer who reported the row marked it suspected or unverified,
  even if the grader later traced it.
- `nit`: true for a minor row that is a nit.
- IDs stay stable across versions.

## Grading a run

- Grade the reviewer's final reported list, or each lens's raw report for a multi-lens reviewer;
  its own confidence scores or filters are not verification.
- Map each finding to a ledger ID; never credit a finding without checking the code.
- Full credit: the finding names the row's defect.
- Partial credit: adjacent, fix-only or under-rated findings.
- A finding that states a critical outcome (use-after-free, deadlock, stall) gets full credit
  under a lower emoji.
- A finding the report itself downplays ("low probability", a nit emoji) gets partial credit,
  unless it states a critical outcome.
- A claim the code refutes is rejected: listed, not scored.
- A pre-existing defect, or a claim that applies the user's own rules rather than the project's
  conventions, is excluded: listed, counts for nothing.
- A multi-lens reviewer is graded as one unit: per row, the best credit among its lenses.

## Marks file

One line per run, or per lens of a run:

```
qa-high-r1.arch C1 I1 P1 T1~
qa-high-r1.sre C1 C2~
code-review-r1 C1~ I1
Rejected (code-review-r1): <claim> (<why the code refutes it>).
Excluded (qa-high-r1.sre): <claim> (<pre-existing or own-rule>).
Candidate (qa-high-r1.arch, code-review-r1): <claim>.
```

- Scored line: `<PREFIX>-r<k>[.<lens>] ID ID~ …`; the prefix (ASCII letters, digits and `-`,
  no dot) names the reviewer, prefix plus `-r<number>` the run.
- Bare ID: full credit (1). ID with `~`: partial credit (0.5).
- A run with no credited finding still gets a bare `<PREFIX>-r<k>` line.
- An early-exit run (errored, empty report, or its main turn ended before its subagents) gets a
  bare line: it scores 0.
- Other lines (`#` comments, `Rejected`, `Excluded`, `Candidate`) are not scored for quality.
- A `Rejected` line counts one refuted claim for each distinct run it names; one with no run list
  counts for nothing.
- A multi-lens reviewer's rejected claims come from its raw lens reports, before its own synthesis
  drops any.

## Scoring

```
w_i     = base(severity_i) × (0.5 if plausible_i else 1)
base    = critical 10, important 4, performance 3, test 3, minor bug 1, nit 0.5
quality = 100 × Σ_i w_i·c_i / Σ_i w_i        per run, c_i in {1, 0.5, 0}
```

- Per prefix: mean and standard deviation (sd) of run quality, mean criticals found per run
  (full credit only), mean rejected claims per run, and mean cost per run.
- Cost comes from the `cost=$X` field of each run's `<run>/stats.txt` beside the marks file; a run
  without one leaves its prefix's cost blank.
- Tiers: 2000 bootstrap resamples of ledger rows on mean quality.
- Walking down the quality order, a prefix stays in the current tier when it matches or beats
  the tier head in at least 10% of resamples; otherwise it starts a new tier.
- Order inside a tier is noise; tiers capture ledger-sampling noise, sd run-to-run noise.

Run `python3 score.py <ledger.json> <marks.txt>`; it prints a ledger summary line (version,
findings, weight, criticals), then one row per prefix, named by its reviewer and model: tier,
reviewer (the prompt's first word without a leading `/` and plugin prefix, such as
`qa-review`), model (`shown=`, else `model=` without a leading `claude-`, then `-<effort>`,
from the prefix's first run's `stats.txt`), runs, mean quality, sd, mean criticals, mean
rejected claims, mean $/run.

## Clean-PR case

- Measures false alarms on a change with no known defect, for example the merged fix commit of a
  benchmarked pull request (`run.sh` base `<fix-sha>^`, head `<fix-sha>`).
- Run each reviewer on it the same number of times as on the benchmarked pull request.
- Use a separate output directory; `run.sh` skips a run whose `stats.txt` exists.
- Before the first run, write `{"version": 1, "frozen": true, "rows": []}` to its `ledger.json`;
  without it the warm-up grader writes ledger rows.
- Ignore that directory's marks and the `score.py` error the empty ledger raises; grade by
  hand.
- Count each run's final reported list (`<run>/report.md`, never its lenses), its findings mapped
  to critical or important.
- Report each reviewer's critical and important findings per run as false alarms.
- A finding the code confirms is not a false alarm.
- The clean-PR case's runs are not scored for quality.
