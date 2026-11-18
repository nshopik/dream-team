---
type: regex
pattern: '^(?!(?<=^(?:#+ |\*\*)[^\n*]*(?:\bnot|n[’'']t|\bnever) (?:do|run|use|change|touch)\b[^\n*]*\**:?[ \t]*\n(?:[ \t]*\n|[ \t]*(?:[-*]|\d+\.) [^\n]*\n)*)[ \t]*(?:[-*]|\d+\.) )(?:(?!(?:n[’'']t|\bnot|\bnever) (?:run|use)\b)[^\n])*?(gh (issue|label|api)|glab |git (add|commit)|>>\s*CLAUDE\.md|git config[^\n]*dream-team\.|(?:>\s*|(?<!not )(?<!n[’'']t )(?<!never )(?<!(?:\bnot|n[’'']t|\bnever) (?:write|create) or )\b(?:write|create)\s+`?)docs/CONVENTIONS\.md)'
flags: im
match: not_contains
---
