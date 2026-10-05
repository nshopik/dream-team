---
name: scope-issue
description: >
  Issue description writer. Use when writing or editing an issue (`gh issue create`,
  `glab issue create`, `-f description=`). Commit messages: use `scope-commit`; MR/PR
  descriptions: use `scope-mr`.
---

Issue is actionable items, not prose. Read days or weeks later with zero conversation context.

## issue-style

Reader starts the task from the description alone — no comment threads, no chat history.

### Goal

- Every issue answers: what do I do next.
- Every issue answers: how do I know it's done.

### Shape

- Three parts, in order: context, problem, proposal.
- Context: the conditions that led here.
- Context opens the description unlabeled. No `## Context` heading.
- Problem: the defect or gap the context leads to, under `## Problem`.
- Proposal: the next step, under `## Proposal`. Always present.
- Proposal is concrete: a list of actions, a person to engage, or a scout's questions.
- Proposal ends with a `Done when …` paragraph after its items, naming an observable check. Never a bullet.
- Never end at the problem.
- Meta issue: context, then the checklist. No `## Problem` or `## Proposal`.

### Scout

- Proposal would need a guess or an assumption → scout issue, not a guessed proposal.
- Title starts `Scout:`.
- Proposal lists the questions to answer and a time box.
- Deliverable: a note in the repo's research docs plus one follow-up issue per gap found. No code.
- Done when every question has an answer or its own issue.

### Evidence

- Milestone exit gate is field evidence → one evidence issue in that milestone.
- Title starts `Evidence:`.
- Proposal lists what to deploy and where, the start date, the measurement, and how to collect it.
- Closes with the milestone.

### Meta

- Work spans milestones, or waits on features not built yet → one meta issue tracking it.
- Title starts `Meta:`.
- The checklist follows the context, under no heading; one line per piece of work.
- A line is a child issue link, or plain text naming the feature it waits on.
- File a child issue only when its work can start; tick its box when it closes.
- No milestone; each child carries its own.
- Closes when every line is ticked or ruled out.

### Blockers

- Work cannot start until another issue closes → a `Blocked by #<n>` line, one per blocker.
- Blocker lines end the description.
- Filed into a milestone whose description's `Depends on:` has an open milestone → the host's waiting label (`workflow::future` on GitLab).

### Title

- Under 80 chars.
- Name the thing, not the history.
- ❌ "Refactoring the plugins structure to take into account changes in the Express.js library".
- ✅ "Plugins structure refactoring".

### Items

- Multi-part work → `-` bullet list.
- Each item independently completable and verifiable.
- Default: plain `-` bullets.
- `- [ ]` boxes only for complex multi-stage work, or a meta issue's checklist.
- A paragraph contains an action → pull the action into an item; the paragraph keeps only the why.
- Terse only after the next action is stated. "Stand up the lab" is a title, not a description.

### Skimming

- Context: one paragraph, ~80 words. Never two.
- Context holds only what's needed to act. The reader already works on the project.
- Cite the brief or docs for depth; don't repeat them.
- Problem carries the substance. Longest part.
- Proposal is the outro.

### Format

- Bold the claim a skimmer must land on, not a keyword.
- One bolded phrase per paragraph at most.
- Inline code for identifiers only: file, path, command, config key, label, version, symbol.
- No inline code for emphasis or ordinary nouns.
- Two or more commands or snippets → one fenced block, a `#` comment per case; never inline code in bullets.
- One line per paragraph or list item; never hard-wrap.

### Names

- Describe behaviour in plain words; a backticked code name is the exception.
- User-facing name (flag, config key, metric, exit code, error string) → no limit.
- Code name (function, type, field — own code or library) → at most three backticked
  occurrences in the whole text.
- Detail that locates a site or person (city, address, coordinates) → leave it out unless the
  work depends on it.
- Issue, MR or repo the target forge's readers cannot open → describe it in plain words, or
  drop it.

### Updates

- Findings, decisions, progress → comments.
- A finding changes the work remaining → update the description too.
- Description is the current spec. Comments are the log.

### Length

- ~250 words the shape. 500 hard cap.
- Fenced blocks are evidence, not prose; they don't count toward the cap.
- Context overgrows first. Cut it first.
