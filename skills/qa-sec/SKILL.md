---
name: qa-sec
description: >-
  Reviews code quality and security with parallel read-only lenses (dream-team's
  architect-reviewer, performance-engineer and sre-engineer agents, the built-in security-review
  skill or a security audit), merged and deduplicated by a cheaper agent, with an opt-in verify pass that
  checks each finding against the code. Reviews the current branch by default, or audits the whole repository.
  Use when the user runs /dream-team:qa-sec or asks for a qa-sec review, audit or verify pass.
disable-model-invocation: true
argument-hint: "[audit] [verify] [base-ref | path ...]"
---

# qa-sec

Invoking this skill is the user's opt-in to the Workflow tool. The plugin workflow
`dream-team:qa-sec-review` runs one read-only agent per lens in parallel: a lens with `:` runs as
that agent type, and any other lens (`security-review`, `security-audit`) runs as a workflow
agent with its focus text. Then one `sonnet` agent merges and deduplicates their reports.
The workflow returns schema-checked JSON and re-runs a merge that drops findings. The plugin
workflow `dream-team:qa-sec-verify` is the opt-in verification pass (step 7).

## 1. Pick the mode and scope

- `$ARGUMENTS` contains `audit` or `full`, or the user asked for an audit → **audit**: scope is the
  whole repository.
- Otherwise → **review**: changes from `git merge-base HEAD origin/<default-branch>` to the working
  tree, or from the base ref the user named. Empty diff → say so and stop.
- Paths in `$ARGUMENTS` narrow either mode to those paths.

Write `scope` as 2–4 sentences: repo path, what the project is (one line from its `CLAUDE.md` or
README), the mode, and for review the base ref plus `git diff --stat` output. Name the repo docs a
reviewer must read first if `CLAUDE.md` names them.

## 2. Pick the lenses

Every run: `dream-team:architect-reviewer`, `dream-team:performance-engineer`,
`dream-team:sre-engineer`, and `security-review` in review mode or `security-audit` in audit mode.

Before launching, list the lenses that run as a bullet list, one bold name per bullet.

## 3. Open issues (optional)

If the repo's forge is reachable, list open issues as `#N title` lines and pass them as
`openIssues`, so the merge marks findings an issue already covers. Use the host's forge tooling
skill if one is loaded. Forge unreachable → skip and say so.

## 4. Run

```
Workflow({
  name: "dream-team:qa-sec-review",
  args: { scope, lenses, model, openIssues }
})
```

`model` is the session model's tier (`opus`, `sonnet`, `haiku` or `fable`), taken from the
environment section of your system prompt. This override runs every lens, including any agent
that pins its own model, on the session model. The merge agent stays on `sonnet`.

It returns `{ items, questions, blocked, raw, missing }`. Each item carries `id`, `severity`,
`theme`, `claim`, `location`, `status`, `disputed`, `lenses`, `why`, `fix`, `coveredBy`.

## 5. Keep the originals

Write every report to `<scratchpad>/qa-sec-report.md`: `items` and `questions` as a JSON block,
then each `raw[i].text` under a `## <lens>` heading. Append verdicts there when
step 7 runs. Answer later questions about a finding from this file,
quoting the lens report verbatim.

## 6. Report to the user

- Top line, no heading: lenses run, lenses in `missing`, and each `blocked` entry.
- Render `items` in compressed form, one or two lines each: `id`, status (☑️ verified, ❔
  suspected), claim, `location`, fix. Append `[#N]` from `coveredBy`.
- Section headings, in this order: `### 🔴 Critical`, `### 🟡 Important`, `### 🔵 Minor`,
  `### 🚀 Performance`, `### ❓ Questions`. Omit an empty section.
- Under 🟡, and under 🔴 when it has more than 5 items, group by `theme` with bold sub-headings.
  Omit an empty theme.
- End with the path to `qa-sec-report.md`, then one line offering verification: "Verify the N
  🔴/🟡/🚀 and disputed 🔵 findings against the code? (~M agents)", with M = ceil(N / 6). Then the
  offer to file issues.

## 7. Verify (opt-in)

Run only when `$ARGUMENTS` contains `verify` or the user accepts the offer. Default set: every 🔴,
🟡 and 🚀 item, plus each 🔵 item with `disputed` set; the user may name ids instead.

```
Workflow({
  name: "dream-team:qa-sec-verify",
  args: { items, scope, model, scratch }
})
```

It returns `{ verdicts, missing }`, one `{ id, verdict, evidence, severity }` per item. Re-render
the report: replace the status emoji after each item's `id` with ✅ confirmed or ❔ unverifiable, and
append the evidence line; move refuted items to a final `### ❌ Refuted` section with their
evidence line. List ids in `missing` as not verified.

- A confirmed or unverifiable item whose `severity` differs from its own → move it to that
  severity's section and append `(was <old emoji>)`.
- Write each changed severity into the `items` JSON in `qa-sec-report.md`.

Do not fix anything. Filing issues waits for the user to pick the items.
