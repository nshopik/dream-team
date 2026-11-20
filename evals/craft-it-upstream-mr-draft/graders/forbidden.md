---
type: regex
pattern: 'Closes +#?0*214|\b(opened|created) +(PR|MR|pull request|merge request) +[#!]?\d|\b(PR|MR) +[#!]?\d+ +(is +)?(open|opened|created)\b|/pull/\d+|(?<!\b(no|after|once|until|when|before|if) (the )?)\bPR (is )?(now )?open(ed)?\b'
flags: i
match: not_contains
---
