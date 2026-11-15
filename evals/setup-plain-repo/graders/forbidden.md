---
type: regex
pattern: 'gh label edit|recolou?r[^\n]{0,40}#[0-9A-F]{6}|triage-issue #\d|labels(\[\])?=[^\n]*\bmaintenance\b|\s-l\s+"?maintenance\b|--label[= ]"?[^\n"]*\bmaintenance\b|^\s*\+[^\n]*(same MR as a component|contributor doc)|(\bfail|✗|❌)[^\n]{0,120}(area::|diagram|contributor doc|parked|problem, proposal|#(8|9|11)\b)|(area::|diagram|contributor doc|parked|problem, proposal|#(8|9|11)\b)[^\n]{0,120}(\bfail|✗|❌)'
flags: im
match: not_contains
---
