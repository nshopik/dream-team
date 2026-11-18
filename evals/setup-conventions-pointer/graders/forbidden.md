---
type: regex
pattern: '^\s*\+[^\n]*Repo layout:|ansible-lint`? before every commit\.?[ \t]*\n[ \t+]*(?:- )?Repo layout:'
flags: im
match: not_contains
---
