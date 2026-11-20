---
type: regex
pattern: '^(?!(?<=^(?:#+ |\*\*)[^\n*]*(?:(?:\bnot|n[’'']t|\bnever) (?:do|run|use|change|touch)\b[^\n*]*|\bleave\b[^\n*]*\balone:?)\**:?[ \t]*\n(?:[ \t]*\n|[ \t]*(?:[-*]|\d+\.) [^\n]*\n)*)[ \t]*(?:[-*]|\d+\.) )(?:(?!(?:n[’'']t|\bnot|\bnever) (?:run|use|touch)\b)[^\n])*?(gh (issue|label|api)|glab |git (add|commit)|>>\s*CLAUDE\.md|git config[^\n]*dream-team\.)'
flags: im
match: not_contains
---
