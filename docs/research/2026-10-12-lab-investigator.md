# Investigator for lab and perf investigations

**Date:** 2026-10-12 · **Issues:** #238, #250

dream-team `6808184`: `lab-runner` runs lab commands and returns a summary without a diagnosis;
`performance-engineer` is a read-only reviewer in neither lens roster (#224). Subagent and skill
behaviour is from the Claude Code
[sub-agents](https://code.claude.com/docs/en/sub-agents.md) and
[skills](https://code.claude.com/docs/en/skills.md) docs.

## The investigator is a skill loaded in the main session

A new skill, not an agent and not a rewrite of `performance-engineer`. It holds the diagnosis
loop and calls `lab-runner` once per probe; `lab-runner` and `performance-engineer` stay as they
are. `MAINTAINING.md` "Building agents" builds a skill for the project's own conventions and never
an agent for a broad role. Follow-up: #250.

## Past use cases come from local session data and stay out of the repo

The use cases and how often each came up were mined from local session transcripts. Per this
repo's `CLAUDE.md`, they were reported in chat and are not recorded here.

## The main session loads the skill when lab work needs a diagnosis

- A regression, a failure reproduced on a lab host, or a slow path with an unknown cause → load
  the skill.
- One-shot lab work (a perf gate, a deploy, one check) → a plain `lab-runner` dispatch, as today.
- `dream-fixer` step 5: a lab failure whose cause `lab-runner`'s summary does not show → load the
  skill before fixing it or handing the branch back.
- `dream-fixer-loop`: never; its agents never ssh.

## The skill needs no new tools, so dream-fixer's lab rule holds

The skill runs with the main session's tools, and every lab command still goes through
`lab-runner`. `dream-fixer`'s "Lab work is yours, not the workflow's" rule is unchanged.
`lab-runner` does not get the `Skill` tool: the skill's brief carries the probe, and a
`lab-runner` that loads a diagnosis skill diagnoses, which its description rules out. The context
cost in the main session is one compact `lab-runner` summary per probe.

## investigate-first and diagnosing-bugs are not enough on their own

They ship in other plugins (caveman, mattpocock-skills), so dream-team cannot depend on them. Both
are generic. Neither says to run each probe through `lab-runner` with one hypothesis and its
prediction in the brief, to measure base and branch on the same host in one session, or to put
measured numbers in the MR. The new skill carries those conventions.

## Ruled out

- An investigator agent: a subagent returns once, so it cannot show ranked hypotheses to the user
  or take a steer mid-loop. Nested dispatch (three levels by default) would let it call
  `lab-runner`, which settles the tool question but not the steering one.
- A forked skill (`context: fork`, `agent: lab-runner`): same steering gap, and it makes
  `lab-runner` diagnose.
- `lab-runner` with the `Skill` tool or a preloaded `skills:` entry: same role break. The docs do
  not say whether `skills:` accepts a plugin-prefixed name; untested, since no design here needs
  it.
- Rewriting `performance-engineer`: its keyword lists are review cues for a read-only lens, and it
  still ships as one.
