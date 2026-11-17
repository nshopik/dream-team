---
type: regex
pattern: '^[\s>*\d.-]*`?\$? *git (worktree add|checkout -b|switch -c)|^[\s>*\d.-]*`?\$? *(gh pr|glab mr) create|docs/decisions/\d{4}-'
flags: im
match: not_contains
---
