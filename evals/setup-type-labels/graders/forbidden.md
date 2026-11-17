---
type: regex
pattern: '^(?:(?!(?:n[’'']t|\bnot|\bnever) (?:run|use)\b)[^\n])*?(--label[= ]"?[^\n"]*(?<!::)\bmaintenance\b|labels(\[\])?=[^\n]*(?<!::)\bmaintenance\b|\s-l\s+"?maintenance\b)'
flags: im
match: not_contains
---
