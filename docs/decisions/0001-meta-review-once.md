# A Meta issue's children are reviewed once, over the whole integration branch

`assemble-meta-loop` runs `build-issue-loop` on each child only up to the gate, then runs its
Simplify, Review and Fix phases once over the integration branch's diff from its base.
A reviewer of one child judges it against a partial design: it flags a function no caller uses
yet or an error path a later child fills, and misses defects between children, such as a helper
written twice or a mismatched interface, which show only in the whole diff.

## Considered Options

- Per-child review: each child runs the full `build-issue-loop` on the integration branch. It
  pays the review and fix cost, most of a loop run's cost, once per child.
- Parallel children: left out; they need `build-issue-loop` to run in a per-child worktree.
