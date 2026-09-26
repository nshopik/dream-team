# scope-style

A Claude Code plugin that keeps commit messages, MR/PR descriptions, and issues short and useful
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

## Install

```
/plugin marketplace add nshopik/scope-style
/plugin install scope-style@scope-style
```

Requires `python3` on `PATH`.

For the [pi](https://github.com/earendil-works/pi) harness:

```
pi install git:github.com/nshopik/scope-style
```

pi loads the three skills; the `body-cap.py` hook is Claude Code only.

The rules themselves are in each `SKILL.md`. The hook allows anything it can't parse.

## dream-team

A second plugin in this marketplace. The `dream-fixer` skill takes one tracker issue to an open
MR/PR by running the `dream-fixer-loop` workflow: implement, build/test gate, reviewers, bounded
fix rounds.
The `align-project` skill checks an existing project against the flow and files one issue per
failing check.
The `cut-milestones` skill drafts milestones from a spec, one exit gate each.
The `milestone-close` skill checks a milestone's exit criterion, triages its open issues and
checks docs against code. Two PreToolUse hooks: `branch-guard.py` blocks a design or spec document
written on `main`/`master`, and `changelog-cap.py` blocks a CHANGELOG entry past one sentence or
40 words.
The `lab-runner` agent does work on a lab host, running every remote command in the foreground.
`jit-context.py` injects git, forge, changelog, spec, prose and lab conventions the first time a
session touches each, and at session start tells the agent to record corrections in the
project's `CLAUDE.local.md`.

- `DREAM_TEAM_OWN_REMOTES`: regex matching the git remote URLs you own. Default: unset.

```
/plugin install dream-team@scope-style
```

Needs the Workflow tool. Uses `scope-mr` and `scope-issue` from `scope-style`, the
`pr-review-toolkit` reviewers, and `caveman:cavecrew-builder` for docs-only issues; a missing
agent type runs as a generic agent.

## Development

Rules live in the `## <id>` sections of each `SKILL.md`; the hook holds only detection logic and
caps. Test a local checkout with:

```
claude --plugin-dir .
claude --plugin-dir plugins/dream-team
python3 hooks/test_body_cap.py
python3 plugins/dream-team/hooks/test_changelog_cap.py
python3 plugins/dream-team/hooks/test_jit_context.py
```

## License

MIT
