---
type: regex
pattern: '(\bfail|✗|❌)[^\n]{0,120}Sprint 4|Sprint 4[^\n]{0,120}(\bfail|✗|❌)|exit criteri[^\n]{0,60}(\bfail|✗|❌)|rename[^\n]{0,40}Sprint 4|(\bfail|✗|❌)[^\n]{0,120}(reference (source|doc)|invariant)'
flags: i
match: not_contains
---
