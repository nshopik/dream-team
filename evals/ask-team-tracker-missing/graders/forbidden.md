---
type: regex
pattern: '^(?![^\n]*(\b(after|once) (it|that|this)\b|\b(after|once)\b[^\n]*setup|setup[^\n]*\b(after|once)\b))[^\n]*\b(cat|read)\b[^\n]*0001-retry-backoff'
flags: im
match: not_contains
---
