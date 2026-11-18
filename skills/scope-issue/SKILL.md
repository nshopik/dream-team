---
name: scope-issue
description: >
  Writes issue descriptions: a problem paragraph opening with the defect, a proposal, then a
  `## Done when` section of observable checks, and states a hard-to-reverse design choice the
  build records in the change's commit. Use when writing or editing an issue (`gh issue
  create`, `gh api …/issues`, `glab issue create`, `-f description=`). Commit messages: use
  `scope-commit`; MR/PR descriptions: use `scope-mr`.
---

Issue is actionable items, not prose. Read days or weeks later with zero conversation context.

- `git config --local --type=bool --get dream-team.own` prints anything but `true` → file, comment
  on and close issues per `<base directory>/../setup-dream-team/tracker-local.md`.

## issue-style

Reader starts the task from the description alone — no chat history. Comments carry the issue's
history; a run that resumes the work reads them too.

### Goal

The reader opens the issue days or weeks later, with none of this conversation, and starts the
work from the description alone. So every issue answers two questions: what do I do next, and how
do I know it's done. An issue that leaves one out sends the reader back to ask, and the person
who knew may be gone.

### Shape

- Three parts, in order: problem, proposal, `## Done when`.
- Problem opens the description unlabeled. No `## Problem` heading.
- Problem opens with the defect or gap, bolded.
- Background the defect or gap needs follows it.
- Several defects, effects or sites → a `-` list after the opening sentence.
- Evidence (a table, a fenced block) sits under the claim it backs.
- Origin is one clause ("Found by a docs review").
- Each fact appears once.
- Proposal: the next step, under `## Proposal`. Always present, except a meta issue.
- Proposal is concrete: a list of actions, a person to engage, or a research issue's questions.
- `## Done when` follows `## Proposal`: one plain `-` bullet per observable check. No `- [ ]` boxes. Not in a meta issue.
- Never end at the problem.
- Meta issue: a paragraph on the work it tracks, then the checklist. No bolded defect, no `## Proposal`.
- One kind label: `bug`, `feature`, `maintenance`, `performance`, `research` or `meta`.

### Open questions

- User asked for the issue in chat, no open question or each one settled by reading the code or
  the reference source → ask nothing.
- User asked for the issue in chat, a choice that would pass the test in
  `<base directory>/../craft-it/reference/decision-record.md` once decided, its options not yet
  known, or a `## Done when` check with no observable form → run `dream-team:brainstorm`, skipping
  its path proposal and hand-off, until the choice is decided and each check is observable; the
  issue is the path (Decisions).
- User asked for the issue in chat, any other open question, milestone included → ask it with
  AskUserQuestion before writing it; write the answers into the issue.
- Issue found during other work (craft-it, a review, a lab check) → do not prompt; list the
  open questions as open items in the proposal, or file a `Research:` issue.
- Issue found during other work, not a `Research:` issue, open items in its proposal → add the
  `workflow::needs-brainstorm` label.

### Decisions

- Proposal carries a decided design choice that passes the test in
  `<base directory>/../craft-it/reference/decision-record.md` → state the choice in the
  proposal and say it gets a decision record in the change's commit; write no record now.
- The body never argues the choice.
- A choice still undecided after Open questions has no record: it stays an open question.

### Research

- Proposal would need a guess or an assumption no Open questions tier settles → research issue,
  not a guessed proposal.
- Title starts `Research:`.
- Proposal lists the questions to answer.
- Deliverable: a findings comment on the issue plus follow-up issues for the gaps found. No code.
- User asks for a file → a note in the repo's research docs; the comment carries the rest.
- A research issue's `## Done when`: every question has an answer or an issue tracking it.

### Evidence

- Milestone exit gate is field evidence → one evidence issue in that milestone.
- Title starts `Evidence:`.
- Proposal lists what to deploy and where, the start date, the measurement, and how to collect it.
- Closes with the milestone.

### Meta

- Work spans milestones, waits on features not built yet, or is a milestone's unattended issues
  (below) → one meta issue tracking it.
- Title starts `Meta:`.
- The checklist follows the opening paragraph, under no heading; one line per piece of work.
- A line is a child issue link, or plain text naming the feature it waits on, outside the meta
  issue.
- File a child issue when its work can start; tick its box when it closes.
- Every open blocker of a piece is another child of the same meta issue → file it as a child,
  with one `Blocked by #<n>` line per sibling.
- A meta issue for work spanning milestones has no milestone; each child carries its own.
- Closes when every line is ticked or ruled out.
- User asks to file a milestone's issues under one meta issue → one meta issue set to that
  milestone, its lines the milestone's issues that can run unattended.
- A run files two or more non-`Research:` issues in one milestone that pass step 2 of
  `<base directory>/../craft-it/SKILL.md`, carry no `workflow::needs-brainstorm` or
  `workflow::blocked` label and need no lab work → file them under one meta issue set to that
  milestone, without prompting, whatever their kind label.
- Filing a milestone's meta issue on request → propose the issues that stay off it as
  human-loop issues (they need a lab run, credentials, or a product or UX call) in the same
  AskUserQuestion batch, for the user to confirm.

### Blockers

- Work cannot start until another issue closes → a `Blocked by #<n>` line, one per blocker.
- Blocker lines end the description.
- Filed into a milestone whose description's `Depends on:` has an open milestone → the `workflow::future` label.

### Title

- Under 80 chars.
- Name the thing, not the history.
- ❌ "Refactoring the plugins structure to take into account changes in the Express.js library".
- ✅ "Plugins structure refactoring".

### Items

Write multi-part work as a `-` bullet list, each item independently completable and verifiable:
the reader does the items one at a time and checks each without rereading the rest. Plain `-`
bullets are the default. Keep `- [ ]` boxes only for complex multi-stage work or a meta issue's
checklist, where someone tracks progress in the issue itself. An action inside a paragraph gets
missed, so pull it into an item and leave the paragraph only the why. Be terse only after the next
action is stated: "Stand up the lab" is a title, not a description, and nobody can start from it.

### Skimming

The reader already works on the project, so the problem holds only what they need to act. It
carries the substance and is the longest part, because the reader decides there whether and how
to do the work; the proposal and `## Done when` are the outro. Cite a brief or doc the target
forge's readers can open by URL or path, at the claim it backs, and don't repeat it: a copy goes
stale and the link does not.

### Format

A skimmer reads the bold text first, so bold the claim they must land on, not a keyword, and at
most one phrase per paragraph: two bolded phrases compete and neither lands. Inline code tells
the reader the text is literal and searchable, so use it for identifiers only (file, path,
command, config key, label, version, symbol), never for emphasis or ordinary nouns. Two or more
commands or snippets go in one fenced block with a `#` comment per case, never as inline code in
bullets, so the reader can copy them whole. Write one line per paragraph or list item and never
hard-wrap: the forge renders a hard line break as a break in the text.

### Diagram

- Defect or new design is a relationship between 3 or more named modules or paths → one fenced
  `mermaid` diagram showing it.
- The diagram replaces the prose it depicts.
- At most 8 nodes.
- No styling.
- Each node names a real file, symbol or output.
- Never on a `Research:`, `Evidence:` or `Meta:` issue.
- Syntax: `graph TD`, `id["label"]`, `-->`, `-.->` and `subgraph` only; never `flowchart`,
  `%%{` or `@{`.
- Node id is a short alphanumeric word, never `end`.
- Unsure whether to draw, user asked for the issue in chat → ask the user.

### Names

- Describe behaviour in plain words; a backticked code name is the exception.
- Terms in the issue: follow `./glossary.md`.
- User-facing name (flag, config key, metric, exit code, error string) → no limit.
- Code name (function, type, field — own code or library) → at most three backticked
  occurrences in the whole text.
- Detail that locates a site or names a customer or person outside the project (city, address,
  coordinates, company, contact) → leave it out unless the work depends on it.
- Issue, MR, repo, link or path the target forge's readers cannot open (chat thread, shared doc,
  local file, internal host) → describe it in plain words, or drop it.

### Updates

- An open issue's comments hold every result a later run needs: findings, decisions, progress.
- Repo docs hold only facts that outlive the issue.
- Small amendment that leaves the work remaining unchanged → a new comment; leave the
  description as written.
- Finding with no decision on direction yet → a new comment; leave the description as written.
- Direction decided, title and problem paragraph still hold → rewrite the proposal and
  its `## Done when` section, then comment why it changed with the replaced proposal quoted.
- Direction decided, title or problem paragraph no longer holds → file a new issue that links the
  findings comment, then close this one with a `Superseded by #<n>` comment.
- Description is the current spec. Comments are the log.

### Length

Aim for about 250 words; 500 is the hard cap, except the two cases below. A longer issue gets
skimmed and the reader misses the action. Fenced blocks are evidence or a diagram, not prose, so
they don't count toward the cap. Background overgrows first; cut it first.

- Still over 500 with every fact one the next run needs, user asked for the issue in chat → before filing, give the word count and ask: split into a meta issue with children, or file over the cap.
- Still over 500 with every fact one the next run needs, issue found during other work → file it over the cap; name the issue and its word count in the run's report.
