---
name: qa-review
description: >-
  Reviews design, reliability, test coverage and claims against the project's reference sources
  with parallel read-only lenses (dream-team's architect-reviewer, sre-engineer and
  test-coverage-reviewer agents, and a generic domain lens), whose findings the main
  session merges and deduplicates, with an opt-in verify pass that checks each finding against the
  code. Reviews the current branch by default, or audits the whole repository, asking the user to
  pick paths when it maps over ~10K lines of code. Use when the user runs /dream-team:qa-review or
  asks for a qa-review, audit or verify pass.
disable-model-invocation: true
argument-hint: "[audit] [verify] [base-ref | path ...]"
---

# qa-review

The main session runs one read-only agent per lens with the Agent tool, then merges and
deduplicates their reports itself (step 4).

On pi, read every Agent launch below this way:

- The Agent tool is `subagent`; launch every agent of one step in one call, one `tasks` entry
  `{agent, task}` each, `task` the prompt.
- `subagent_type` `Explore` is agent `scout`; `general-purpose` is `worker`.
- Drop the `dream-team:` prefix from a lens name.
- Pass no `model` or `effort`.

## 1. Pick the mode and scope

- `$ARGUMENTS` contains `audit` or `full`, or the user asked for an audit → **audit**: scope is the
  whole repository, or on a large repository the paths the user picks from the audit map below.
- Otherwise → **review**: changes from `git merge-base HEAD origin/<default-branch>` to the working
  tree, or from the base ref the user named. Empty diff → say so and stop.
- Paths in `$ARGUMENTS` narrow either mode to those paths.
- Audit with no paths in `$ARGUMENTS` → build the audit map below before writing `scope`.

Write `scope` as 2–4 sentences: repo path, what the project is (one line from its `CLAUDE.md` or
README), the mode, and for review the base ref, `git diff --stat` output and the line "Read the
diff with `git diff <base>`.", with ` -- <paths>` appended when paths narrow the review. Name the
repo docs a reviewer must read first if `CLAUDE.md` names them.

### Audit map

- Launch one Agent: `subagent_type` `Explore`, `model` `haiku`, `prompt` the map block below.
- Map agent errors, returns nothing or gives no total → say so, then ask the user for the paths
  to audit.
- Mapped code over ~10K lines → print the module table (path, lines, role) and the unmapped
  directories line, and end your turn.
- The user's reply names the paths to audit, at any depth → they become the scope.
- Mapped code at or under ~10K lines → keep the whole repository as scope.

Map block, verbatim:

```
Map this repository's code by module. Read only. Facts only: no judgments, findings or advice.
- A table of the directories holding code: path, code lines, one-line role. Split a directory over 10K lines into its subdirectories. Count lines with `wc -l` over `git ls-files`; skip vendored, generated and lock files, test data, fixtures and docs. Test source code counts as code.
Output: the table, then the total code lines, then one line naming the directories you did not map, or `none`, and nothing else.
```

## 2. Pick the lenses

Lenses: `dream-team:architect-reviewer`, `dream-team:sre-engineer`,
`dream-team:test-coverage-reviewer` and `domain`.

- Every file in scope is docs or config (Markdown, plain text, YAML, TOML, JSON, INI), and none
  is CI, build, test-runner or feature-flag config or an agent or skill prompt (`SKILL.md`,
  `agents/*.md`) → skip `dream-team:test-coverage-reviewer`.
- The project's `CLAUDE.md` names no reference source or invariant, or nothing in scope makes a
  claim checkable against one → skip `domain`.

Before launching, list the lenses that run as a bullet list, one bold name per bullet; list each
skipped lens the same way with its reason.

## 3. Existing open issues (optional)

If the repo's forge is reachable, list open issues as `#N title` lines, so the step-4 merge
marks findings an issue already covers. Use the host's forge tooling
skill if one is loaded. Forge unreachable → skip and say so.

## 4. Run

Launch one Agent per lens, all in one message, and wait for every report:

- `subagent_type`: the lens; `general-purpose` for `domain`.
- `model`: the session model's tier (`opus`, `sonnet`, `haiku` or `fable`), taken from the
  environment section of your system prompt.
- `prompt`: the lens prompt below.

A lens that errors or returns nothing goes in `missing`.

Lens prompt: `<scope>`, a blank line, `Your lens: <focus>`, a blank line, then the rules block.
Focus: the lens name after its last `:`; for `domain`, `<claim>` checked against
`<source files>` and `<invariant>`, as the project's `CLAUDE.md` names them; cite file and line
on both sides.

Rules block, verbatim:

```
Do not edit, create or delete files in the repository. Do not commit, push, or touch any forge or lab host.
Read only: no builds, test runs, benchmarks, profiles or experiments.
Output: findings only, ranked most severe first. Each finding: one emoji prefix (🔴 bug/security/data loss/crash, 🟡 risk/fragile/regression, 🔵 nit, ❓ genuine question), `file:line`, why, fix. Mark each [verified] (traced in code) or [suspected].
With a base ref in scope: also mark a finding [pre-existing] when its defect already exists at the base ref and the change neither introduces, newly reaches, nor worsens it.
No praise, no codebase summary. If a step could not run (tool missing, blocked), say so in one line.
End with one line naming the in-scope areas you did not read, or `none`.
```

Then merge the reports yourself into `items`, `questions` and `blocked`, items ranked most severe
first, `preExisting` items after the rest:

- Same defect reported by several lenses → one item; list every lens that found it; keep the
  strongest evidence (verified beats suspected; keep repro numbers and log lines in `why`). Set
  `disputed` when one lens marked it verified and another suspected.
- Never drop a finding. Never soften a severity; on disagreement take the higher one.
- ❓ findings go to `questions`, not `items`.
- Set `preExisting` only when every lens that reported the defect marked it pre-existing.
- A finding an open issue from step 3 already covers → keep it, set `coveredBy` to `#N`.
- `blocked`: lenses that reported a blocked or incomplete run, with what did not run, and the
  areas each lens did not read, unless it answered `none`.
- A report without the closing unread-areas line → list its lens in `blocked` as incomplete.

Each item carries `id` (`F1`, `F2`, ... in ranked order), `severity` (🔴, 🟡 or 🔵), `theme`
(🛡️ Security, 💾 Reliability / data loss, 🏗️ Architecture / contracts, 🧪 Tests / CI, ⚙️ Ops /
config / deploy, 📝 Docs drift / writing, 🚀 Performance), `claim`, `location` (`file:line`,
comma-separated if several), `status` (verified or suspected), `disputed`, `lenses`, `why`, `fix`,
`coveredBy`, `preExisting`.

## 5. Report to the user

- Top line, no heading: lenses run, each skipped lens with its reason, lenses in `missing`, and
  each `blocked` entry.
- Render `items` in compressed form, one or two lines each: `id`, status (☑️ verified, ❔
  suspected), claim, `location`, fix. Append `(disputed)` when `disputed` is set and `[#N]` from
  `coveredBy`.
- Section headings, in this order: `### 🔴 Critical`, `### 🟡 Important`, `### 🔵 Nit`,
  `### ❓ Questions`, `### 🟣 Pre-existing`. Omit an empty section.
- Render `preExisting` items under `### 🟣 Pre-existing` only, each line led by its `severity`
  emoji.
- Under 🟡, and under 🔴 when it has more than 5 items, group by `theme` with bold sub-headings.
  Omit an empty theme.
- End with one line offering verification: "Verify the N 🔴/🟡 and disputed 🔵 findings
  against the code? (~M agents)", with M = ceil(N / 6). Then the offer to file issues.

## 6. Verify (opt-in)

Run only when `$ARGUMENTS` contains `verify` or the user accepts the offer. Default set: every 🔴
and 🟡 item, plus each 🔵 item with `disputed` set; the user may name ids instead. Split the set
into batches of six items, each item with every step-4 field.

Launch one Agent per batch, all in one message, and wait for every report:

- `subagent_type`: `general-purpose`.
- `model`: the session model's tier, as in step 4.
- `effort`: `medium`.
- `prompt`: `<scope>`, a blank line, the verify block with `<scratch>` replaced by your scratchpad
  directory, a blank line, then the batch as JSON.

Verify block, verbatim:

```
Verify each finding below against the code. Return one verdict per id.

- confirmed: you traced the claim in the cited code or reproduced it. Evidence names the file:line or the command and its output.
- refuted: the code does not do what the finding claims. Evidence names the line that shows it.
- unverifiable: deciding needs a lab host, a real external service, root, or hardware. Evidence says what is needed.
- You may run local tests and small repros in <scratch>. Do not edit, create or delete files in the repository; no ssh, no forge, no external network.
- Judge each finding on its own; a confirmed bug with a wrong fix is still confirmed.
- severity: rate what your evidence shows, not the claim (🔴 bug/security/data loss/crash, 🟡 risk/fragile/regression, 🔵 nit). A confirmed finding whose real cost is larger or smaller than claimed gets the severity of the real cost; a refuted one keeps its severity.

Output: one line per finding and nothing else: `<id> | <confirmed, refuted or unverifiable> | <severity emoji> | <evidence, one line>`.
```

Re-render the report from the verdict lines:

- Confirmed → replace the status emoji after the item's `id` with ✅ and append the evidence line.
- Unverifiable → replace the status emoji with ❔ and append the evidence line.
- Refuted → move the item to a final `### ❌ Refuted` section with its evidence line.
- A sent item with no verdict line → list it as not verified.
- A confirmed or unverifiable item whose verdict-line severity differs from its `severity` → move
  it to that severity's section and append `(was <old emoji>)`.
- A confirmed or unverifiable `preExisting` item whose verdict-line severity differs → swap its
  lead emoji and append `(was <old emoji>)` instead.

Do not fix anything. Filing issues waits for the user to pick the items.
