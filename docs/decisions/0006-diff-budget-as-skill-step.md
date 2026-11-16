# MR/PR diff budget is a warning-only skill step, not a hook

A PreToolUse hook on `gh` and `glab` calls checked MR/PR descriptions by parsing the description
out of the shell command, which needed a patch for each new command shape and ran only under
Claude Code. It is dropped for wider harness support and to stop the parser patches. Only the diff
budget (description words against `max(80, 5 × diff lines)`) is kept, as a script `scope-mr` runs
on the description file before posting; it warns and exits 0, and the model decides whether to
cut. The 300-word cap, rubric headings, `--fill` and left-out-item checks stay as `scope-mr` text.

## Considered Options

- A hook that checks only the budget: keeps the shell parsing and the Claude Code dependency.
- A CI check on the PR body: does not cover PRs to upstream repos.
