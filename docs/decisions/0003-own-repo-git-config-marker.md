# An own clone is marked by an untracked git config key; an unmarked repo is upstream

`setup-dream-team` marks a clone of the user's own project or fork with
`git config --local dream-team.own true`, and `jit-context.py` adds the `<upstream_repo>` rules in
every git repo where that key is not `true`. 0002 marked upstream clones instead, so every
upstream clone the setup run missed got no guard against unprompted pushes and issues; with the
marker on own clones, a missed clone gets the guard. A user's own repos and forks are fewer than
the outside code checked out on one machine, so this default also needs fewer setup runs.
