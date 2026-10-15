# Reviewer benchmark: methodology

Compares code reviewers on one pull request by weighted recall against a frozen, verified findings
ledger.

## Ledger build

- Run qa-review as warm-up: 3 runs at effort high, then 2 at max.
- The grader verifies every row against the code before it enters the ledger.
- Freeze the ledger as version 1 after the fifth run.

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
{"version": 1, "rows": [{"id": "C1", "finding": "…", "location": "src/a.c:412",
  "severity": "critical", "plausible": false, "nit": false}]}
```

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
QR1.arch C1 I1 P1 T1~
QR1.sre C1 C2~
CR1 C1~ I1
Rejected (CR1): <claim> (<why the code refutes it>).
Excluded (QR1.sre): <claim> (<pre-existing or own-rule>).
Candidate (QR1.arch, CR1): <claim>.
```

- Scored line: `<PREFIX><run>[.<lens>] ID ID~ …`; the prefix (capital letters A-Z) names the
  reviewer, prefix plus number the run.
- Bare ID: full credit (1). ID with `~`: partial credit (0.5).
- A run with no credited finding still gets a bare `<PREFIX><run>` line.
- Other lines (`#` comments, `Rejected`, `Excluded`, `Candidate`) are not scored.

## Scoring

```
w_i     = base(severity_i) × (0.5 if plausible_i else 1)
base    = critical 10, important 4, performance 3, test 3, minor bug 1, nit 0.5
quality = 100 × Σ_i w_i·c_i / Σ_i w_i        per run, c_i in {1, 0.5, 0}
```

- Per reviewer: mean and standard deviation (sd) of run quality, and mean criticals found per
  run (full credit only).
- Tiers: 2000 bootstrap resamples of ledger rows on mean quality.
- Walking down the quality order, a reviewer stays in the current tier when it matches or beats
  the tier head in at least 10% of resamples; otherwise it starts a new tier.
- Order inside a tier is noise; tiers capture ledger-sampling noise, sd run-to-run noise.

Run `python3 score.py <ledger.json> <marks.txt>`; it prints a ledger summary line (version,
findings, weight, criticals), then one row per reviewer: tier, runs, mean quality, sd, mean
criticals.
