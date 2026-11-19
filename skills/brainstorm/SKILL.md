---
name: brainstorm
description: >-
  Shapes a vague idea before any spec or issue exists: grills the user in rounds of numbered
  questions, each with a recommended answer, then states the shared understanding, names the
  next skill in one line and waits for the user. Use when the user voices an idea not yet worked
  out — "I have an idea", "let's brainstorm", "thinking about", "what if we", "new feature for
  X", "I want X but not sure how". Not for an issue number (use craft-it or triage-issue) or
  a routine, already-described task.
---

# brainstorm

## 1. Grill

- Map the idea as a design tree: each decision branches into the decisions that depend on it.
- Ask in rounds; a round holds every decision whose prerequisites are settled.
- A question that depends on another still open in this round → a later round.
- Number each question and give its recommended answer, via AskUserQuestion.
- A round over 4 questions → several AskUserQuestion calls in the same turn.
- After each round's answers, recompute the next round from what they settled.
- A fact the code, docs, tracker or tools can answer → dispatch a subagent to find it; never
  ask the user.
- A fact still being looked up → hold only the questions that depend on it; ask the rest now.
- A decision → put it to the user and wait.
- Done when you and the user reach a shared understanding: every branch of the tree is visited,
  no decision is left unsettled and nothing is silently assumed.

## 2. Close

- State the shared understanding in chat.
- Use the layout below as the default; adjust its sections to the result.
- Label each bullet by its decision; never repeat a label.
- Decisions span several aspects or artifacts → group them under bold section lines; else one
  flat list.
- A decision with parts (files, steps, checks) → sub-bullets under it.
- A fact that bears on the decision → one note paragraph of 1-2 sentences after the bullets.
- End with one line naming the next skill: `scope-spec`, `scope-issue`, or none.
- Wait for the user to confirm the shared understanding.
- The user asks for the issue → load `scope-issue` before any further question.

```
**Shared understanding:** confirm or correct before I act.

**<section>**
- **<decision>:** <answer>
- **<decision>:** <answer>
  - <part>
  - <part>

<note>

Next: `/dream-team:<skill>` | none
```
