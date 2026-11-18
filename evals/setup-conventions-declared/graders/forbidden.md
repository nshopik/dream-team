---
type: regex
pattern: 'ansible-lint`? before every commit\.?[ \t]*\n[ \t+]*(?:- )?Architecture decision records live in'
flags: i
match: not_contains
---
