# dream-team

A Claude Code plugin that takes tracker issues to open MR/PRs, plans and closes the milestones
around them, and keeps commit messages, MR/PR descriptions and issues short and useful to the
people who read them. How the flow runs, step by step: [`WORKFLOW.md`](WORKFLOW.md).

Status: under active tuning. Rules and caps change as they're measured against real repositories.

Skills:

- `dream-fixer`: takes one tracker issue to an open MR/PR by running the `dream-fixer-loop`
  workflow: implement, build/test gate, reviewers, bounded fix rounds.
- `setup-dream-team`: checks an existing project against the flow, fixes the mechanical failures
  directly and files one issue per other failing check.
- `cut-milestones`: drafts milestones from a spec, one exit gate each.
- `milestone-close`: checks a milestone's exit criterion, triages its open issues, and checks
  docs against code.
- `scope-commit`: [Scoped Commits](https://scopedcommits.com/) subjects
  (`<scope>: <description>`), and a body only when it carries a fact the diff can't show.
- `scope-mr`: review-facing descriptions in up to four parts (why, how, root cause, behaviour),
  never a restatement of the commits.
- `scope-issue`: issues in three parts (context, problem, proposal) that can be started without
  the conversation that produced them.
- `friction`: reports agent friction repeated across past `dream-fixer-loop` runs; run it as
  `/dream-team:friction`.

Agent:

- `lab-runner`: does work on a lab host, running every remote command in the foreground.

Hooks:

- `body-cap.py` (PreToolUse): checks `gh pr|issue create|edit` and `glab mr|issue` commands
  before they run. It blocks rule violations and quotes the matching skill section back to
  Claude, so the fix happens in the same turn. It allows anything it can't parse.
- `branch-guard.py` (PreToolUse): blocks a design or spec document written on `main`/`master`.
- `changelog-cap.py` (PreToolUse): blocks a CHANGELOG entry past one sentence or 40 words.
- `jit-context.py`: injects git, forge, changelog, spec, prose and lab conventions the first time
  a session touches each. At session start, tells the agent to record corrections in the
  project's `CLAUDE.local.md`.

## Install

```
/plugin marketplace add nshopik/dream-team
/plugin install dream-team@dream-team
```

Requires `python3` on `PATH`. Needs the Workflow tool. Uses `pr-review-toolkit` reviewers; a
missing agent type runs as a generic agent.

For the [pi](https://github.com/earendil-works/pi) harness:

```
pi install git:github.com/nshopik/dream-team
```

pi loads the skills; the hooks and the workflow are Claude Code only.

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
python3 hooks/test_changelog_cap.py
python3 hooks/test_jit_context.py
python3 skills/friction/test_friction.py
```

## License

MIT
