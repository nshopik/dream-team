# Bundled agent prompts

- For a missing named role → look for `agents/<role>.md` in the `qa-review` directory under
  the same install root as this reference.
- If that file is absent → use the advertised `qa-review` directory only if it contains the file.
- For a generic role dispatch → prepend that file's body to the task prompt.
- For path variables in a generic role's body → replace the plugin-root prefix through
  `skills/qa-review` with the absolute `qa-review` directory that supplied the prompt.
- For a generic read-only role → use read-only tools that can inspect the requested diff.
- For a generic writing role → constrain edits to the paths in the task.
