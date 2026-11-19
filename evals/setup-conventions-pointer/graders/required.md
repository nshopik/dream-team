---
type: regex
pattern: '## Doc conventions(?:[\s+>]|\\n)+Decision records, specs, ROADMAP: `docs/CONVENTIONS\.md`\. Read the records touching your area first'
flags: i
---
---
type: regex
pattern: '\| *Decision records *\| *`?docs/adr/NNNN-slug\.md'
flags: i
---
---
type: regex
pattern: '^\s*\+?\s*Date: \{YYYY-MM-DD\}'
flags: im
---
