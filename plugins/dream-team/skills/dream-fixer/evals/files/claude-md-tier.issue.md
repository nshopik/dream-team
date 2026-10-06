The CLI reference in `docs/cli/` is written by hand and has drifted from the commands: `export
--since` and `tail --follow-name` are missing, and `rotate --keep` still documents the old
default of 7.

## Proposal

- Add a hidden `flowlog gen-docs <dir>` subcommand that walks the cobra command tree and writes
  the reference with `cobra/doc`.
- Replace the hand-written pages in `docs/cli/` with its output, and add a CI step that fails
  when the committed pages differ from a fresh run.
- One page per command or a single `cli.md` page: either works, pick whichever reads better.

Done when `docs/cli/` matches `flowlog gen-docs` output and CI checks it.
