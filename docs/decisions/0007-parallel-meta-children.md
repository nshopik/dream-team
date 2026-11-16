# A Meta issue's children build in per-child worktrees, two at once, and land in finish order

`assemble-meta-loop` runs up to 2 ready children at once, each `build-issue-loop` in its own git
worktree on a branch cut from the integration tip, so a Meta run no longer takes as long as all
its children added together. A child that passes its gate lands one at a time by a rebase onto
the integration tip, a re-run of the gate commands and a fast-forward; a rebase conflict or a red
re-gate reruns it once from the new tip. Child gates run in parallel with no guard, because the
re-gate on the tip catches a collision between them.

## Considered Options

- One child at a time on the integration branch: a Meta run takes as long as all its children
  added together.
- The Workflow API's per-agent `isolation: 'worktree'`: gives each agent a fresh worktree, while
  one child loop's 8 or more agents need one shared checkout.
- More than 2 children at once: each child already starts several reviewers in parallel, and
  concurrent agents are capped at min(16, CPUs−2) per workflow.

## Consequences

- A fresh worktree lacks the main checkout's ignored files other than symlinks, such as
  `node_modules/` or a `.venv/`, so gate commands that need them fail there.
