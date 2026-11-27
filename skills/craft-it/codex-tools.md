# Codex CLI tools

- Use the plugin skill name advertised in `/skills`.
- For a skill lookup without a loader → read the advertised `SKILL.md`.
- Dispatch with `spawn_agent`.
- For edits → use the built-in `worker`.
- Use the session model for built-in agents.
- Translate stage labels to task names using letters, digits and underscores.
- Use the wait tool until every launched task has returned.
