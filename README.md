# dream-team

A Claude Code plugin marketplace with two plugins: `scope-style` and `dream-team`.

```
/plugin marketplace add nshopik/dream-team
```

## scope-style

A plugin that keeps commit messages, MR/PR descriptions, and issues short and useful
to the people who read them.

- `scope-commit` skill: [Scoped Commits](https://scopedcommits.com/) subjects
  (`<scope>: <description>`), and a body only when it carries a fact the diff can't show.
- `scope-mr` skill: review-facing descriptions in up to four parts (why, how, root cause,
  behaviour), never a restatement of the commits.
- `scope-issue` skill: issues in three parts (context, problem, proposal) that can be started
  without the conversation that produced them.
- `body-cap.py` PreToolUse hook: checks `git commit`, `gh pr|issue create|edit`, and
  `glab mr|issue` commands before they run. It blocks rule violations and quotes the matching skill section back
  to Claude, so the fix happens in the same turn.

Status: under active tuning. Rules and caps change as they're measured against real repositories.

### Install

```
/plugin install scope-style@dream-team
```

Requires `python3` on `PATH`.

For the [pi](https://github.com/earendil-works/pi) harness:

```
pi install git:github.com/nshopik/dream-team
```

pi loads the three skills; the `body-cap.py` hook is Claude Code only.

The rules themselves are in each `SKILL.md`. The hook allows anything it can't parse.

## dream-team

A plugin that takes tracker issues to open MR/PRs, and plans and closes the milestones around
them. How the flow runs, step by step: [`WORKFLOW.md`](plugins/dream-team/WORKFLOW.md).

Skills:

- `dream-fixer`: takes one tracker issue to an open MR/PR by running the `dream-fixer-loop`
  workflow: implement, build/test gate, reviewers, bounded fix rounds.
- `align-project`: checks an existing project against the flow and files one issue per failing
  check.
- `cut-milestones`: drafts milestones from a spec, one exit gate each.
- `milestone-close`: checks a milestone's exit criterion, triages its open issues, and checks
  docs against code.

Agent:

- `lab-runner`: does work on a lab host, running every remote command in the foreground.

Hooks:

- `branch-guard.py` (PreToolUse): blocks a design or spec document written on `main`/`master`.
- `changelog-cap.py` (PreToolUse): blocks a CHANGELOG entry past one sentence or 40 words.
- `jit-context.py`: injects git, forge, changelog, spec, prose and lab conventions the first time
  a session touches each. At session start, tells the agent to record corrections in the
  project's `CLAUDE.local.md`.

### Install

```
/plugin install dream-team@dream-team
```

Needs the Workflow tool. Uses:

- `scope-mr` and `scope-issue` from `scope-style`.
- `pr-review-toolkit` reviewers.

A missing agent type runs as a generic agent.

### Configuration

- `DREAM_TEAM_OWN_REMOTES`: regex matching the git remote URLs you own. Default: unset.

## Development

Rules live in the `## <id>` sections of each `SKILL.md`; the hook holds only detection logic and
caps. `hooks/body-cap.py` quotes a section back verbatim when it blocks a command. Keep heading ids
stable and sub-headings at `###`, since any `##` closes a section. `{over_cap}`, and in
`scope-commit` also `{subject}` and `{problems}`, are placeholders the hook fills.

Test a local checkout with:

```
claude --plugin-dir .
claude --plugin-dir plugins/dream-team
python3 hooks/test_body_cap.py
python3 plugins/dream-team/hooks/test_changelog_cap.py
python3 plugins/dream-team/hooks/test_jit_context.py
```

## License

MIT
