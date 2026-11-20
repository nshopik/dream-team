---
type: regex
pattern: '#4[14]\b[^\n.]{0,60}(?<!(n[’'']t|\bnot|\bnever)\b(?:(?!\b(and|but|so|then)\b)[^\n,;.:])*)(?<!milestone-|\bor )(close|move|carry|defer)|byte-identical[^\n]{0,80}\b(met|pass(es|ed)?|ran|checked)\b'
flags: im
match: not_contains
---
