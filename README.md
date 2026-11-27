# dream-team

A small crew of agents that plans, builds, reviews and ships your project with you, from spec to
release.

## Install

```
/plugin marketplace add nshopik/dream-team
/plugin install dream-team@dream-team
```

For Codex CLI:

```sh
codex plugin marketplace add nshopik/dream-team
codex plugin add dream-team@dream-team
```

Open `/hooks` to review and trust the convention hooks. They run with Python 3. Start a new
session and pick a Dream Team skill from `/skills`. Append arguments after the skill mention.

For pi, OpenCode, and other harnesses supported by the skills CLI:

```sh
npx skills add nshopik/dream-team --global
```

Choose your harness and install the shared skills together for workflows that use more than one
skill. For example, `craft-it`, `milestone-close`, and `triage-issue` use the dispatch instructions
and role prompts in `qa-review`. Leave `assemble-meta`, `friction`, and `review-bench` for Claude
Code. A skills-only install includes skill files and their resources, but no hooks.

For workflows that dispatch subagents on pi, also install the subagent extension:

```sh
pi install npm:pi-sub-agent
```

See the [harness tool references](skills/craft-it/SKILL.md#harness-tools) for skill lookup and
subagent tools.

## Start here

These examples use Claude Code syntax. For other hosts, see the
[harness reference](skills/craft-it/SKILL.md#harness-tools).

- **New project:** `/dream-team:setup-dream-team`, then `/dream-team:scope-spec`
- **Existing tracked project:** `/dream-team:craft-it <issue>`
- **Upstream or untracked one-off:** `/dream-team:brainstorm`
- **Not sure:** `/dream-team:ask-team`

Run `setup-dream-team` in each clone, and again after an upgrade note asks for it. In your own
project or fork it marks the clone with `git config --local dream-team.own true` and writes
`docs/CONVENTIONS.md`; in an upstream clone it writes the local tracker rules to
`.dream-team/TRACKER.md`. A git repo without that key gets the upstream-project rules.

## How it works

1. **Spec:** the project's design, written from a lean template.
2. **Milestones:** cut from the spec, each with a measurable exit criterion.
3. **Issues:** one per change.
4. **MR/PR:** one per issue, implemented, gated and reviewed by agents.
5. **Milestone close:** only when the exit criterion is met.

Each skill also runs on its own, in any order, without the tracked flow.

It works on GitHub and GitLab, for application code and infrastructure-as-code. The full
walkthrough is in [`WORKFLOW.md`](skills/ask-team/WORKFLOW.md).

## Contents

### Skills

- **[triage-issue](skills/triage-issue/SKILL.md)**: checks a legacy, outside-filed or
  needs-brainstorm issue against the code before it is built, and rewrites it in `scope-issue`
  form.
- **[craft-it](skills/craft-it/SKILL.md)**: takes one issue, from the tracker or, in an
  upstream clone, a local issue file, to an open MR/PR via the `craft-it-loop` workflow.
- **[assemble-meta](skills/assemble-meta/SKILL.md)**: takes a Meta issue's children to one MR/PR on
  one integration branch via the `assemble-meta-loop` workflow.
- **[setup-dream-team](skills/setup-dream-team/SKILL.md)**: marks a clone of your own project or
  fork, checks the project against the flow, applies fixes that change no code after one OK,
  commits its doc edits and files one issue for the rest; in an upstream clone it only writes
  `.dream-team/TRACKER.md` and keeps `.dream-team/` and `CLAUDE.local.md` out of git.
- **[ask-team](skills/ask-team/SKILL.md)**: answers which skill fits now, with one command to
  run and where it sits: its `WORKFLOW.md` step, or its group in the skill map.
- **[brainstorm](skills/brainstorm/SKILL.md)**: grills a vague idea in rounds of questions, then
  states the shared understanding and names the next skill.
- **[scope-spec](skills/scope-spec/SKILL.md)**: the project spec in the repo's specs folder,
  written from its template.
- **[cut-milestones](skills/cut-milestones/SKILL.md)**: drafts milestones from a spec, one exit gate
  each.
- **[milestone-close](skills/milestone-close/SKILL.md)**: checks a milestone's exit criterion,
  triages its open issues, checks docs against code, and offers a release.
- **[ship-it](skills/ship-it/SKILL.md)**: releases main, with or without a milestone: version
  bump, CHANGELOG move, then a tag, pushed when the version is the argument, else offered.
- **[build-rules](skills/build-rules/SKILL.md)**: the build rules a code change follows, loaded
  before the first edit and by `craft-it-loop`'s implementer and fixers.
- **[scope-commit](skills/scope-commit/SKILL.md)**: commit messages in
  [Scoped Commits](https://scopedcommits.com/) format.
- **[scope-mr](skills/scope-mr/SKILL.md)**: MR/PR descriptions.
- **[scope-issue](skills/scope-issue/SKILL.md)**: tracker issues, or local issue files in an
  upstream clone (problem, proposal, done when).
- **[friction](skills/friction/SKILL.md)**: reports agent friction in the current session with
  retro candidates, or with `all` the friction repeated across past `craft-it-loop` runs.
- **[qa-review](skills/qa-review/SKILL.md)**: reviews a branch or audits a repo with parallel
  read-only lenses.
- **[review-bench](skills/review-bench/SKILL.md)**: benchmarks code reviewers against qa-review on
  one pull request and prints a score table.

### Agents

The reviewer agents review a diff or paths, read-only.

- **[architect-reviewer](skills/qa-review/agents/architect-reviewer.md)**: design defects.
- **[docs-editor](skills/qa-review/agents/docs-editor.md)**: fixes docs a change made stale with
  minimal edits to the listed pages, or writes or revises one doc from a brief. Never invents
  facts or builds.
- **[docs-reviewer](skills/qa-review/agents/docs-reviewer.md)**: stale docs, style breaks and
  AI-writing patterns.
- **[lab-runner](skills/qa-review/agents/lab-runner.md)**: does work on a lab host, running every
  remote command in the foreground.
- **[performance-engineer](skills/qa-review/agents/performance-engineer.md)**: performance cost.
- **[sre-engineer](skills/qa-review/agents/sre-engineer.md)**: failure behaviour.
- **[test-coverage-reviewer](skills/qa-review/agents/test-coverage-reviewer.md)**: test gaps.

### Hooks

- `jit-context.py`: injects project conventions the first time a session touches each, and asks
  the agent to record corrections in `CLAUDE.local.md`.

## License

MIT
