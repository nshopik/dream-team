# dream-fixer-loop result fields

- **`ok: false` with `handBack: true`** — blocking findings survived. `reason` says which case:
  - *Fix rounds ran out.* Do not open an MR. Report the outstanding findings and hand the branch
    back.
  - *The fixer disputed every finding and the reviewers held.* Settle each entry in `disputes`
    yourself, per the `disputes` bullet below. With every entry in `blocking` settled and
    `deadReviewers` empty, carry on to step 6's lab steps and step 7; otherwise hand the branch
    back.
  - `deadReviewers` non-empty → those reviewers returned nothing on every try. Do not open the MR;
    hand the branch back.
- **`ok: false` otherwise** — the implement, gate, simplify or fix stage failed. Report the
  reason; the branch is where the agent left it.
- **`degraded`** — roster types that were not dispatchable and ran as a generic agent instead,
  `ponytail:ponytail-review` when that skill was missing and the Simplify phase was skipped, and
  `verify` when `claude` or its `/verify` was missing and the `/verify` gate was skipped.
- **`simplify`** — the over-engineering cuts made before review: `applied`, `disputed` with the
  implementer's reason, and `net`, the review's estimate of lines that could go. Put applied cuts in
  the MR description, and `net` only when nothing was disputed; treat a disputed cut like a minor
  finding. `unhandled` counts cuts the implementer neither applied nor disputed; above 0 → say so in
  the MR description. `null` → the phase was skipped.
- **`verifyRun`** — the last `/verify` gate run: `verdict`, `command`, `output`, `reason`,
  `recipePath`. `null` → the `/verify` gate did not run, or was skipped (see `degraded`). A FAIL
  was a blocking finding for the fix loop.
  - `PASS` → put its `command` and `output` in the MR description.
  - `BLOCKED` and its `reason` needs the lab → run it as a lab step through `dream-team:lab-runner`.
  - `BLOCKED` otherwise → name the verdict and its `reason` in the report.
  - `SKIP` → name the verdict and its `reason` in the report.
  - `recipePath` non-empty → never commit the recipe on the branch; report its path for the user
    to copy to `.claude/skills/verify/SKILL.md` and commit separately.
- **`disputes`** — the fixer refused a finding and gave evidence. Check it yourself. The fixer may
  be right; it may also be rationalizing. Apply the fix or accept the dispute.
- **`resolved`** — blocking findings a fix round fixed, each with its reviewer (`gate`) and round.
- **`minorFindings`** — never auto-fixed. Apply the ones worth applying, drop the rest.
- **`assumptions`** — anything the implementer had to invent.
- **`redEvidence`** — the new test's failing output from before the fix; the test reviewer checked
  it. Empty on a bug-fix issue means nobody saw the test fail.
