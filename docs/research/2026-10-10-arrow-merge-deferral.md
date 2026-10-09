# Architect lens defers the arrow-decimal parser merge

**Date:** 2026-10-10 · **Issues:** #180

`dream-team:architect-reviewer` run through `/dream-team:qa-sec` on the arrow-decimal eval case
(apache/arrow-rs `078c0f17b`, base `00fadf96`), sonnet and opus, dream-team at `2c24379`. Eight
headless sessions, about $7. The rubric is the #176 hand score's: the merge offered as the fix
in this change is a hit, the merge deferred to a later change or never proposed is a partial,
and no comparison of the two parsers is a miss.

| Arm | sonnet | opus |
|---|---|---|
| Unchanged, run 1 | miss | partial ("Longer term, choose one parser") |
| Unchanged, run 2 | partial ("Longer term, … share one core") | hit ("make one parser call the other") |
| qa-sec `RULES` block removed | partial (question, docs only) | partial ("Longer term, share one … core") |
| Agent body cut to its two hard rules | partial ("Decide separately whether to converge") | partial (question, docs only) |

## Neither the RULES block nor the agent body causes the deferral

The deferral persists with each candidate removed. With qa-sec's `RULES` set to `''`, both
models still offer docs first and push the merge to "longer term" or leave it out. With the agent
body reduced to its two hard rules, both models still defer or only ask whether the split is
intended. The cue comes from the model's default for a diff review, not from dream-team text.

## The deferral mostly follows a "pre-existing" remark

Of the 9 partials on this case (#176's four runs plus this sweep), 8 call the split or the second
parser older than the commit just before deferring: "existed before this commit", "already true
before the PR", "predates the PR". The remark is accurate: `parse_string_to_decimal_native`
predates the commit, which rewrote it. The remark does not decide the outcome: opus unchanged run 2 makes the same
remark and still puts the merge first, and sonnet unchanged run 2 defers with no such remark.

Upstream also merged the parsers in a separate PR (apache/arrow-rs#10850), so "a separate
change" matches what the project did. A rule that forces the merge into the same change would be
derived from this one case, against upstream's own sequence.

## The opus flip on arrow is run noise

Two runs of the unchanged lens on opus split: one partial, one hit. Opus on the current text has
1 hit in 3 runs (#176 after, plus this sweep); with the FOCUS line it had 2 in 2. Runs this few
cannot separate those rates. Sonnet has no hit on arrow in 5 runs of the shipped agent, with or
without the line.

## Ruled out

- A deferral line in `agents/architect-reviewer.md`: the agent has none, and cutting the body did
  not change the outcome.
- The qa-sec output rules ("findings only", "why, fix"): removing the whole block did not change
  the outcome.
