# craft-it-loop without the Workflow tool

You run the `craft-it-loop` stages yourself: each stage through the host’s subagent tool, the gate in your
own shell. You end with the result object `workflow-result.md` documents, so step 5 on reads it
as it reads a workflow return.

- `<loop>` is `<base directory>/craft-it-loop.js` in a local Codex install, or
  `<base directory>/../../workflows/craft-it-loop.js` in the source checkout.
- Before stage 1, read `<loop>` once as reference: it holds every prompt function, schema, label
  and result shape named below.

## Dispatch

- Build each prompt with the `<loop>` function the stage names, from step 4's `args`, with
  `worktree` set to the worktree's absolute path.
- End each prompt with "End your reply with one fenced `json` block, an object matching this
  JSON Schema:" and the stage's schema from `<loop>`, as JSON.
- Set each Agent call's `description` to the label `<loop>` gives that call, e.g. `impl:#42`,
  `fix:#42:r1`.
- A writing agent (implementer, build fixer, fixer) → a `general-purpose` agent with
  `model: opus`, in the foreground, one at a time.
- A reviewer → `model: opus`; a lens gets its `dream-team:` type as `subagent_type`, the
  domain and external reviewers `general-purpose`.
- Several reviewers in one stage → one message with one Agent call each, all at once.
- On Codex, use the parent skill’s dispatch rules for every stage.
- A reply with no fenced block, or a block missing a required field → redispatch it once with
  `agentR`'s retry sentence appended.
- Still no block → that call has no result; take the stage's no-result branch from `<loop>`.
- A lens type that fails to dispatch → dispatch it as `general-purpose` from then on and list
  its type in `degraded`.
- Drop `friction` from each block before using it.

## Gate

- No stage after a writing agent starts until your own run of every `gateCommands` entry exits
  0 on that head.
- Never hand the gate to an agent.
- Run each gate command in the foreground with the Bash tool's maximum timeout, its output
  redirected to a log file under `<scratchpad>`, never into your context.

1. Run `git status --porcelain` in the worktree; set `untrackedPaths` to its `??` paths.
2. Any other line → stop with a `gate` failure: "uncommitted edits in the working tree".
3. Run each `gateCommands` entry from the worktree, in order; the exit codes are the verdict.
4. All exit 0 → record `git rev-parse HEAD` as the gated head.
5. All exit 0 → set `changedFiles` to `git diff --name-only <base>..HEAD`; the gate passed.
6. A red run after 3 build-fix rounds in this Gate → stop with a `gate` failure: "build/test
   still failing after 3 fix rounds".
7. Read each failing command's key error lines from its log's tail or a grep.
8. Dispatch a build fixer: `buildFixPrompt` with each failing command and those lines,
   `BUILD_FIX_SCHEMA`.
9. No result or `committed: false` → stop with a `gate` failure; otherwise go to 1.

## Stages

1. Implement: `implPrompt`, `IMPL_SCHEMA`.
2. Gate.
3. Review, every reviewer at once: the three `LENSES` with `lensPrompt` and stage 1's
   `redEvidence`, the domain lens with `domainPrompt`, and with `externalReview` set the
   external reviewer with `externalPrompt` and `EXTERNAL_SCHEMA`; `VERDICT_SCHEMA` otherwise.
4. Fix rounds, below.
5. Write the result `<loop>`'s last `return` builds to `<scratchpad>/craft-it-result.json`.

- Set each stage's outcomes (stops, `degraded` entries, nits, questions, `preExisting`,
  `doneWhen`) as `<loop>` sets them after that stage's call.
- A stop → write the failure result `<loop>` returns there, then go on to step 5 with it.

## Fix rounds

- A blocking finding is a critical or important one not marked `preExisting`.
- A dead reviewer is one that returned no result.

Each round, numbered from 1:

1. No blocking finding and no dead reviewer → leave the loop.
2. 3 rounds already ran → hand back: "<n> blocking finding(s) and <m> dead reviewer(s)
   outstanding after 3 fix rounds".
3. No live reviewer holds a blocking finding → go to 8.
4. Dispatch the fixer: `fixPrompt` with the live reviewers' blocking findings and the dispute
   list, `FIX_SCHEMA`.
5. No result, or nothing committed, addressed or disputed → stop with a `fix` failure.
6. Add its `disputed` entries to the dispute list with the round.
7. Gate.
8. Re-review in one message:
   - Each reviewer holding blocking findings → `reReviewPrompt` with its numbered prior findings
     and open questions, the fixer's report and the head gated before this fix,
     `RE_REVIEW_SCHEMA`; a dead one gets the fix it missed.
   - Each dead reviewer with no findings → its stage-5 prompt again.
   - Each other live reviewer, when the fixer committed → `fixDiffPrompt` on the fix diff only,
     `VERDICT_SCHEMA`.
9. Merge the replies as `<loop>`'s round does: `findings` plus `added` replace a re-reviewer's
   verdict, its blocking `resolved` entries and answered questions go to `resolved` with the
   round.
10. A re-review with no result → that reviewer is dead and keeps its findings; a fix-diff review
    with no result keeps its pass.
11. The fixer addressed nothing, disputed something, and a re-review that returned still holds a
    blocking finding → hand back: "the fixer disputed every finding it was given and the
    reviewers held".

- A hand-back → write `<loop>`'s `handBack` result.
