# pi tools

- For interactive skill invocation → use `/skill:<name>`.
- For a skill lookup → read the advertised `SKILL.md`.
- For generic dispatch → pass `task` without an agent name to `pi-sub-agent`'s `subagent` tool.
- For a parallel batch → pass a `tasks` array to `subagent`.
- Collect the full batch's results from one tool reply.
- Set the issue worktree as `cwd`.
- When the prompt expects project rules → set `projectContext: true`.
- When the prompt names skills → set `skills: true`.
- For a reviewer that needs `git diff` → keep Bash available.
- For a reviewer that needs `git diff` → require read-only work in the prompt.
