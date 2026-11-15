---
type: regex
pattern: '--label[= ]"?[^\n"]*\bmaintenance\b|labels(\[\])?=[^\n]*\bmaintenance\b|\s-l\s+"?maintenance\b'
flags: im
match: not_contains
---
