---
type: regex
pattern: '((gh|glab) +issue +(comment|note)|(gh|glab) +api\b[^\n]*/(comments|notes)\b)[\s\S]*((gh|glab) +issue +(comment|note)|(gh|glab) +api\b[^\n]*/(comments|notes)\b)'
flags: im
match: not_contains
---
