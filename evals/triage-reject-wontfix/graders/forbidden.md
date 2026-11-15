---
type: regex
pattern: 'gh issue close\b(?![^\n]*not[ _]planned)|state_reason=completed'
flags: i
match: not_contains
---
