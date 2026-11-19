# craft-it-loop result fields

- **`ok: false` with `handBack: true`** — blocking findings survived. `reason` says which case:
  - *Fix rounds ran out.* Do not open an MR. Report the outstanding findings and hand the branch
    back.
  - *The fixer disputed every finding it was given and the reviewers held.* Settle each entry in
    `disputes` yourself, per the `disputes` bullet below. A `blocking` entry with no `disputes`
    entry was not given to the fixer that round → hand the branch back. With every entry in
    `blocking` settled and `deadReviewers` empty, carry on to step 5's lab steps and step 6;
    otherwise hand the branch back.
  - `deadReviewers` non-empty → those reviewers returned nothing on their last try; one that died
    on a re-review keeps its earlier findings in `blocking`; a dead fix-diff review keeps its pass
    and is not listed. Do not open the MR; hand the branch back.
- **`ok: false` otherwise** — the implement, gate or fix stage failed. Report the reason; an
  `implement` stop the issue or a recorded decision asked for carries its measured values in
  `reason`. The branch and its worktree are where the agent left them.
- **`degraded`** — what ran with less than planned:
  - A roster type: its agent call threw, and every later call of that type ran as a generic agent.
  - `external`: the `externalReview` command was missing or exited non-zero, and was skipped.
- **`untrackedPaths`** — untracked paths `git status --porcelain` listed before the latest gate run;
  they do not fail the gate.
- **`disputes`** — the fixer refused a finding and gave evidence. Check it yourself. The fixer may
  be right; it may also be rationalizing. Apply the fix or accept the dispute.
- **`resolved`** — blocking findings a fix round fixed and questions a re-review answered, each
  with its reviewer (`gate`) and round.
- **`nitFindings`** — every nit the reviewers raised; no agent fixes them.
- Take no action on `nitFindings` in step 5.
- **`questions`** — genuine questions reviewers raised and no re-review answered, each with its
  reviewer (`gate`) and `file`; they never block and never reach the fixer. Step 5 settles them
  before the MR/PR opens. Returned on an `ok` result, a `handBack`, a `fix` stage failure, or a
  `gate` stage failure after a fix round.
- **`preExisting`** — findings on a defect already at the base ref that the change neither
  introduces, newly reaches nor worsens, each with its reviewer (`gate`) and any `file`; they never
  block and never reach the fixer. Merge entries for the same defect and skip any defect also in
  `blocking`, `resolved`, `nitFindings` or `questions`; step 5's adjacent-defect rules apply to
  the rest, except that step 5 settles an entry with severity `question` like a `questions`
  entry. Returned wherever `questions` is.
- **`assumptions`** — anything the implementer had to invent.
- **`redEvidence`** — the new test's failing output from before the fix; the test reviewer checked
  it. Empty on a bug-fix issue means nobody saw the test fail.
- **`doneWhen`** — the domain lens's first-review report on each check in the issue's `## Done
  when` section or older `Done when …` paragraph. A check it reports as not held, with no
  `resolved` entry for it → hand the branch back.
