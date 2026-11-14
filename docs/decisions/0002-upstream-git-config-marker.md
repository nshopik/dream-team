# An upstream clone is marked by an untracked git config key

Superseded by 0003-own-repo-git-config-marker.md

`setup-dream-team` marks an upstream clone with `git config --local dream-team.upstream true`, and
`jit-context.py` adds the `<upstream_repo>` rules only where that key is `true`. The marker lives
in `.git/config`, so an upstream project never takes a committed dream-team file, and each clone
is marked once by the setup skill instead of an environment variable the user has to find.

## Considered Options

- An environment-variable regex over remote URLs: set outside the plugin, and when unset it
  turned the guard off with no sign, so a new user started unguarded.
- A committed file in the repo: an upstream project cannot take committed dream-team files.
