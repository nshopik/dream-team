# Codex CLI tools

- Use the plugin skill name advertised in `/skills`.
- For a skill lookup without a loader → read the advertised `SKILL.md`.
- Dispatch with `spawn_agent`.
- For edits → use the built-in `worker`.
- Use the session model for built-in agents.
- Translate stage labels to task names using letters, digits and underscores.
- Use the wait tool until every launched task has returned.
- For step 7's poll → no background call resumes the session; run it in the foreground.
- A step-7 poll call returns a `session_id` and no `exit_code` → call `write_stdin` on that
  session with empty `chars` and `yield_time_ms: 55000` until a reply carries `exit_code`.
