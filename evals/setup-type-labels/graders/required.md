---
type: regex
pattern: '(#|\b(edit|update) |issues/)3\b[^\n]{0,80}type::bug[^\n]{0,40}\bbug\b|type::bug[^\n]{0,40}\bbug\b[^\n]{0,80}(#|\b(edit|update) |issues/)3\b'
flags: i
---
---
type: regex
pattern: '(#|\b(edit|update) |issues/)1\b[^\n]{0,80}type::research[^\n]{0,60}\bresearch\b'
flags: i
---
---
type: regex
pattern: 'delet[^\n]{0,80}type::'
flags: i
---
