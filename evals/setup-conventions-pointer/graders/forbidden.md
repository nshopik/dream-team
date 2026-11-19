---
type: regex
pattern: '^\s*\+[^\n]*Repo layout:|ansible-lint`? before every commit\.?[ \t]*\n[ \t+]*(?:- )?Repo layout:'
flags: im
match: not_contains
---
---
type: regex
pattern: '^\s*\+?\s*Write a record only when all three hold'
flags: im
match: not_contains
---
---
type: regex
pattern: '^\s*\+?\s*1\.\s*Hard to reverse'
flags: im
match: not_contains
---
