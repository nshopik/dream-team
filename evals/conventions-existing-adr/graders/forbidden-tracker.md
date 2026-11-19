---
type: regex
pattern: '(gh|glab) +issue +(create|comment|close)|(gh|glab) +api\b[^\n]*/issues\b|^\s*Closes\b'
flags: im
match: not_contains
---
