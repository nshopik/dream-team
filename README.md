# dream-team

A Claude Code plugin that gives a project one development process, from first spec to release,
on GitHub or GitLab. Work is planned as small, self-contained issues, and each one ships as a
single reviewed MR/PR.

## How it works

1. **Spec:** the project's design, written from a lean template.
2. **Milestones:** cut from the spec, each with a measurable exit criterion.
3. **Issues:** track your feature specs and bug reports, one per change, each with its context,
   problem and next step. Anyone can start one without the chat that produced it.
4. **MR/PR:** one per issue, implemented, gated and reviewed by agents.
5. **Milestone close:** only when the exit criterion is met.

It works for application code and infrastructure-as-code. The full walkthrough is in
[`WORKFLOW.md`](WORKFLOW.md).

## Contents

### Skills

- **[dream-fixer](skills/dream-fixer/SKILL.md)**: takes one tracker issue to an open MR/PR by
  running the `dream-fixer-loop` workflow: implement, build/test gate, reviewers, bounded fix
  rounds.
- **[setup-dream-team](skills/setup-dream-team/SKILL.md)**: checks an existing project against the
  flow, fixes the mechanical failures directly and files one issue per other failing check.
- **[scope-spec](skills/scope-spec/SKILL.md)**: the project spec in `docs/specs/`, written from its
  template.
- **[cut-milestones](skills/cut-milestones/SKILL.md)**: drafts milestones from a spec, one exit gate
  each.
- **[milestone-close](skills/milestone-close/SKILL.md)**: checks a milestone's exit criterion,
  triages its open issues, and checks docs against code.
- **[scope-commit](skills/scope-commit/SKILL.md)**: [Scoped Commits](https://scopedcommits.com/)
  subjects (`<scope>: <description>`), and a body only when it carries a fact the diff can't show.
- **[scope-mr](skills/scope-mr/SKILL.md)**: review-facing descriptions in up to four parts (why,
  how, root cause, behaviour), never a restatement of the commits.
- **[scope-issue](skills/scope-issue/SKILL.md)**: issues in three parts (context, problem, proposal)
  that can be started without the conversation that produced them.
- **[friction](skills/friction/SKILL.md)**: reports agent friction repeated across past
  `dream-fixer-loop` runs; run it as `/dream-team:friction`.
- **[qa-sec](skills/qa-sec/SKILL.md)**: reviews a branch or audits a repo with parallel read-only
  lenses and an opt-in verify pass; run it as `/dream-team:qa-sec`.

### Agents

- **[architect-reviewer](agents/architect-reviewer.md)**: reviews a diff or paths for design
  defects, read-only; never builds, runs or edits.
- **[docs-editor](agents/docs-editor.md)**: fixes docs a change made stale with minimal edits to
  the listed pages, or writes or revises one doc from a brief; never invents facts or builds.
- **[docs-reviewer](agents/docs-reviewer.md)**: reviews a diff or paths for docs a change made
  stale, style breaks and AI-writing patterns, read-only; never builds, runs or edits.
- **[lab-runner](agents/lab-runner.md)**: does work on a lab host, running every remote command in
  the foreground.
- **[performance-engineer](agents/performance-engineer.md)**: reviews a diff or paths for
  performance cost, read-only; never builds, benchmarks or edits.

### Hooks

- `body-cap.py` (PreToolUse): checks `gh pr|issue create|edit` and `glab mr|issue` commands before
  they run. It blocks rule violations and quotes the matching skill section back to Claude, so the
  fix happens in the same turn. It allows anything it can't parse.
- `branch-guard.py` (PreToolUse): blocks a design or spec document written on `main`/`master`.
- `changelog-cap.py` (PreToolUse): blocks a CHANGELOG entry past one sentence or 40 words.
- `jit-context.py`: injects git, forge, changelog, prose and lab conventions the first time a
  session touches each. At session start, tells the agent to record corrections in the project's
  `CLAUDE.local.md`.

## Install

```
/plugin marketplace add nshopik/dream-team
/plugin install dream-team@dream-team
```

Requires `python3` on `PATH`. Needs the Workflow tool. Uses `pr-review-toolkit` reviewers; a
missing agent type runs as a generic agent. qa-sec needs no third-party reviewer plugin.

For the [pi](https://github.com/earendil-works/pi) harness:

```
pi install git:github.com/nshopik/dream-team
```

pi loads the skills; the hooks and the workflows are Claude Code only.

## Configuration

- `DREAM_TEAM_OWN_REMOTES`: regex matching the git remote URLs you own. Default: unset.

## Development

Rules live in the `## <id>` sections of each `SKILL.md`; the hook holds only detection logic, caps
and deny headers. `hooks/body-cap.py` quotes a section back verbatim, after its deny header, when
it blocks a command. Keep heading ids stable and sub-headings at `###`, since any `##` closes a
section.

Test a local checkout with:

```
claude --plugin-dir .
python3 hooks/test_body_cap.py
python3 hooks/test_branch_guard.py
python3 hooks/test_changelog_cap.py
python3 hooks/test_jit_context.py
python3 skills/dream-fixer/test_fold.py
python3 skills/friction/test_friction.py
node workflows/test_simplify.mjs
node workflows/test_qa_sec.mjs
python3 test_frontmatter.py
```

## License

MIT
