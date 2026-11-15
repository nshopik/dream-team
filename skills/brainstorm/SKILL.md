---
name: brainstorm
description: >-
  Shapes a vague idea before any spec or issue exists: grills the user in rounds of numbered
  questions, each with a recommended answer, at the depth the CLAUDE.md `## Expertise` section
  sets, then states the shared understanding and proposes one path (spec, issue, Meta issue,
  research issue, decision record, inline edit or drop) and acts on it only once the user
  approves it. Use when the user voices an idea not yet worked out — "I have an idea",
  "let's brainstorm", "thinking about", "what if we", "new feature for X", "I want X but not
  sure how". Not for an issue number (use build-issue or triage-issue) or a routine,
  already-described task.
---

# brainstorm

- Terms: follow `<base directory>/../../references/glossary.md`.
- Unclear whether to grill or edit directly → grill.

## 1. Depth

- Read the `## Expertise` section of every loaded CLAUDE.md; each item names an area the user
  wants grilled in depth.
- A branch in a listed area → grill it fully.
- A branch outside every listed area → pick the recommended option and state it in one line.
- No `## Expertise` section → grill every branch at full depth.

## 2. Grill

- Ask in rounds; a round holds every decision whose prerequisites are settled.
- A question that depends on another still open in this round → a later round.
- Number each question and give its recommended answer, via AskUserQuestion.
- A round over 4 questions → several AskUserQuestion calls in the same turn.
- After each round's answers, recompute the next round from what they settled.
- A fact the code, docs, tracker or tools can answer → dispatch a subagent to find it; never
  ask the user.
- A fact still being looked up → hold only the questions that depend on it; ask the rest now.
- A decision → put it to the user and wait.
- Done when you and the user reach a shared understanding: no decision is left unsettled and
  nothing is silently assumed.

## 3. Handed-back choices

- Two answers in a row hand the choice back ("you decide", "whatever you think") on questions
  that need domain knowledge → offer, once per area, a map of that area's decisions, each with
  its default.
- Map declined → take its defaults and mark each `(default)` in its decision bullet.
- A user who can weigh the options but has not decided → normal questions.

## 4. Propose the path

- State the shared understanding in chat, then propose one path: spec, issue, Meta issue,
  research issue, decision record, inline edit, or drop.
- Issue or inline edit: needs a user decision, contradicts the spec, adds a component, or needs a
  lab check → issue; otherwise inline edit.
- Use the layout below as the default; adjust its sections to the result.
- Label each bullet by its decision; never repeat a label.
- Decisions span several aspects or artifacts → group them under bold section lines; else one
  flat list.
- A decision with parts (files, steps, checks) → sub-bullets under it.
- A fact that bears on the decision → one note paragraph of 1-2 sentences after the bullets.
- End with one question that names the path and its action.

```
**Shared understanding:** confirm or correct before I act.

**<section>**
- **<decision>:** <answer>
- **<decision>:** <answer>
  - <part>
  - <part>

<note>

<path>: <one-line reason>. <question naming the action>?
```

## 5. Hand off

- Wait for the user to confirm the shared understanding and approve or change the path.
- Spec → ask the user to run `/dream-team:scope-spec`.
- Issue, Meta issue or research issue → load `scope-issue`.
- Decision record → load `scope-issue` and follow its Decisions with no issue; skip the line
  that has an issue cite the record.
- Inline edit → make the edit.
- Drop → nothing.
