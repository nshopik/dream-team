---
type: regex
pattern: '((?<!n[’'']t )(?<!not )\bfail|✗|❌)[^\n]{0,120}Sprint 4|Sprint 4[^\n]{0,120}((?<!n[’'']t )(?<!not )\bfail|✗|❌)|exit criteri[^\n]{0,60}((?<!n[’'']t )(?<!not )\bfail|✗|❌)|(?<!n[’'']t )(?<!not )rename[^\n]{0,40}Sprint 4|((?<!n[’'']t )(?<!not )\bfail|✗|❌)[^\n]{0,120}(reference (source|doc)|invariant)'
flags: i
match: not_contains
---
