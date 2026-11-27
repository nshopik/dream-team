# Bundled agent prompts

- For a missing named role → use `agents/<role>.md` beside this file.
- For a generic role dispatch → prepend that file's body to the task prompt.
- For path variables in a generic role's body → replace the plugin-root prefix through
  `skills/qa-review` with the absolute path of this file's directory.
- For a generic read-only role → use read-only tools that can inspect the requested diff.
- For a generic writing role → constrain edits to the paths in the task.
