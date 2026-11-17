# dream-team

Every developer has wished for a dream team: everyone sharp, nobody dropping the ball, and the
impossible task still getting done. Before LLMs, putting one together was about as likely as
winning the lottery.

This plugin is that team, for Claude Code: agents that turn your spec into milestones, split the
milestones into issues small enough to finish, take each issue to a reviewed MR/PR, and stay
with you through release. Bring them your biggest task.

It works on GitHub and GitLab, for application code and infrastructure-as-code. The full
walkthrough is in [`WORKFLOW.md`](skills/ask-team/WORKFLOW.md).

## How it works

1. **Spec:** the project's design, written from a lean template.
2. **Milestones:** cut from the spec, each with a measurable exit criterion.
3. **Issues:** one per change.
4. **MR/PR:** one per issue, implemented, gated and reviewed by agents.
5. **Milestone close:** only when the exit criterion is met.

Each skill also runs on its own, in any order, without the tracked flow.

## Start here

- **New project:** `/dream-team:setup-dream-team`, then `/dream-team:scope-spec`
- **Existing tracked project:** `/dream-team:build-issue <issue>`
- **Upstream or untracked one-off:** `/dream-team:brainstorm`
- **Not sure:** `/dream-team:ask-team`

## Contents

### Skills

- **[triage-issue](skills/triage-issue/SKILL.md)**: checks a legacy, outside-filed or
  needs-brainstorm issue against the code before it is built, and rewrites it in `scope-issue`
  form.
- **[build-issue](skills/build-issue/SKILL.md)**: takes one issue, from the tracker or, in an
  upstream clone, a local issue file, to an open MR/PR via the `build-issue-loop` workflow.
- **[assemble-meta](skills/assemble-meta/SKILL.md)**: takes a Meta issue's children to one MR/PR on
  one integration branch via the `assemble-meta-loop` workflow.
- **[setup-dream-team](skills/setup-dream-team/SKILL.md)**: marks a clone of your own project or
  fork, checks the project against the flow, applies fixes that change no code after one OK,
  commits its doc edits and files one issue for the rest; in an upstream clone it only keeps
  `CLAUDE.local.md` out of git.
- **[ask-team](skills/ask-team/SKILL.md)**: answers which skill fits now, with one command to
  run and where it sits: its `WORKFLOW.md` step, or its group in the skill map.
- **[brainstorm](skills/brainstorm/SKILL.md)**: grills a vague idea in rounds of questions, then
  proposes its path.
- **[scope-spec](skills/scope-spec/SKILL.md)**: the project spec in the repo's specs folder
  (`docs/specs/` by default), written from its template.
- **[cut-milestones](skills/cut-milestones/SKILL.md)**: drafts milestones from a spec, one exit gate
  each.
- **[milestone-close](skills/milestone-close/SKILL.md)**: checks a milestone's exit criterion,
  triages its open issues, checks docs against code, and offers a release.
- **[ship-it](skills/ship-it/SKILL.md)**: releases main, with or without a milestone: version
  bump, CHANGELOG move, then a tag, pushed when the version is the argument, else offered.
- **[craft-rules](skills/craft-rules/SKILL.md)**: the build rules a code change follows, loaded
  before the first edit and by `build-issue-loop`'s implementer, fixers and simplify pass.
- **[scope-commit](skills/scope-commit/SKILL.md)**: commit messages in
  [Scoped Commits](https://scopedcommits.com/) format.
- **[scope-mr](skills/scope-mr/SKILL.md)**: MR/PR descriptions.
- **[scope-issue](skills/scope-issue/SKILL.md)**: tracker issues, or local issue files in an
  upstream clone (problem, proposal, done when).
- **[friction](skills/friction/SKILL.md)**: reports agent friction repeated across past
  `build-issue-loop` runs.
- **[qa-review](skills/qa-review/SKILL.md)**: reviews a branch or audits a repo with parallel
  read-only lenses.
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

pi loads the skills; the hooks and the `build-issue-loop` and `assemble-meta-loop` workflows are
Claude Code only.

`qa-review` runs its lenses through the `pi-sub-agent` extension:

```
pi install npm:pi-sub-agent
```

On pi the agents get pi's default tools, `write` and `edit` included.

`review-bench` needs `git`, `gh` and the `claude` CLI on `PATH`.

## Configuration

Run `setup-dream-team` once in each clone of your own project or fork; it marks the clone with
`git config --local dream-team.own true`. A git repo without that key gets the upstream-project
rules.

## License

MIT
