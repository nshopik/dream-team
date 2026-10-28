# dream-team

Every developer has wished for a dream team: everyone sharp, nobody dropping the ball, and the
impossible task still getting done. Before LLMs, putting one together was about as likely as
winning the lottery.

This plugin is that team, for Claude Code: agents that turn your spec into milestones, split the
milestones into issues small enough to finish, take each issue to a reviewed MR/PR, and stay
with you through release. Bring them your biggest task.

It works on GitHub and GitLab, for application code and infrastructure-as-code. The full
walkthrough is in [`WORKFLOW.md`](WORKFLOW.md).

## How it works

1. **Spec:** the project's design, written from a lean template.
2. **Milestones:** cut from the spec, each with a measurable exit criterion.
3. **Issues:** one per change.
4. **MR/PR:** one per issue, implemented, gated and reviewed by agents.
5. **Milestone close:** only when the exit criterion is met.

## Contents

### Skills

- **[dream-fixer](skills/dream-fixer/SKILL.md)**: takes one tracker issue to an open MR/PR via the
  `dream-fixer-loop` workflow.
- **[setup-dream-team](skills/setup-dream-team/SKILL.md)**: checks an existing project against the
  flow, fixes the mechanical failures directly and files one issue for the rest.
- **[scope-spec](skills/scope-spec/SKILL.md)**: the project spec in `docs/specs/`, written from its
  template.
- **[cut-milestones](skills/cut-milestones/SKILL.md)**: drafts milestones from a spec, one exit gate
  each.
- **[milestone-close](skills/milestone-close/SKILL.md)**: checks a milestone's exit criterion,
  triages its open issues, checks docs against code, and offers a release.
- **[ship-it](skills/ship-it/SKILL.md)**: releases main, with or without a milestone: version
  bump, CHANGELOG move and tag offer.
- **[scope-commit](skills/scope-commit/SKILL.md)**: commit messages in
  [Scoped Commits](https://scopedcommits.com/) format.
- **[scope-mr](skills/scope-mr/SKILL.md)**: MR/PR descriptions.
- **[scope-issue](skills/scope-issue/SKILL.md)**: tracker issues (problem, proposal).
- **[friction](skills/friction/SKILL.md)**: reports agent friction repeated across past
  `dream-fixer-loop` runs.
- **[qa-review](skills/qa-review/SKILL.md)**: reviews a branch or audits a repo with parallel
  read-only lenses.
- **[chaos-planning](skills/chaos-planning/SKILL.md)**: reviews a launch's failure-experiment plan
  for gaps.
- **[review-bench](skills/review-bench/SKILL.md)**: benchmarks code reviewers against qa-review on
  one pull request and prints a score table.

### Agents

The reviewer agents review a diff or paths, read-only.

- **[architect-reviewer](agents/architect-reviewer.md)**: design defects.
- **[docs-editor](agents/docs-editor.md)**: fixes docs a change made stale with minimal edits to
  the listed pages, or writes or revises one doc from a brief; never invents facts or builds.
- **[docs-reviewer](agents/docs-reviewer.md)**: stale docs, style breaks and AI-writing patterns.
- **[lab-runner](agents/lab-runner.md)**: does work on a lab host, running every remote command in
  the foreground.
- **[performance-engineer](agents/performance-engineer.md)**: performance cost.
- **[sre-engineer](agents/sre-engineer.md)**: failure behaviour.
- **[test-coverage-reviewer](agents/test-coverage-reviewer.md)**: test gaps.

### Hooks

- `body-cap.py` (PreToolUse): blocks MR/PR descriptions that break `scope-mr` rules.
- `branch-guard.py` (PreToolUse): blocks a design or spec document written on `main`/`master`.
- `jit-context.py`: injects project conventions the first time a session touches each, and asks
  the agent to record corrections in `CLAUDE.local.md`.

## Install

```
/plugin marketplace add nshopik/dream-team
/plugin install dream-team@dream-team
```

Requires `python3` on `PATH` and the Workflow tool.

For the [pi](https://github.com/earendil-works/pi) harness:

```
pi install git:github.com/nshopik/dream-team
```

pi loads the skills; the hooks and the `dream-fixer-loop` workflow are Claude Code only.

`qa-review` runs its lenses through the `pi-sub-agent` extension:

```
pi install npm:pi-sub-agent
```

On pi the agents get pi's default tools, `write` and `edit` included.

`review-bench` needs `git`, `gh` and the `claude` CLI on `PATH`.

## Configuration

- `DREAM_TEAM_OWN_REMOTES`: regex matching the git remote URLs you own. Default: unset.

## Development

Test a local checkout with:

```
claude --plugin-dir .
python3 hooks/test_body_cap.py
python3 hooks/test_branch_guard.py
python3 hooks/test_jit_context.py
python3 skills/dream-fixer/test_fold.py
python3 skills/friction/test_friction.py
python3 skills/review-bench/test_score.py
python3 skills/review-bench/test_extract.py
python3 skills/review-bench/test_run.py
node workflows/test_simplify.mjs
python3 test_frontmatter.py
```

## License

MIT
