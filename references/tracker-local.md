# Issue tracker: local files

A clone where `git config --local --type=bool --get dream-team.own` prints anything but `true` keeps
its issues in local files; it files on the forge tracker only as the last section says. An own clone
uses the forge tracker only, even when a local file exists. The two never mix.

## Home

- `<main>` is the main checkout: the first `worktree` path `git worktree list --porcelain`
  prints. Use it from a worktree too.
- Issues live at `<main>/.dream-team/issues/NNNN-<slug>.md`.
- `NNNN`: four digits, the next free number in that folder, from `0001`.
- `$(git rev-parse --git-common-dir)/info/exclude` has no `/.dream-team/` line → append it before
  the first write.

## When a skill says

- **File an issue:** write a new file in `<main>/.dream-team/issues/`: the title as its first `#`
  line, then a `Status: open` line, then the body in `scope-issue` shape.
- **Read issue `<n>`:** read `<main>/.dream-team/issues/<n zero-padded to four digits>-*.md`.
  - No file matches → stop with "no local issue `<n>`: write it with `scope-issue`, or, if this is
    your own repo, run `setup-dream-team` to mark the clone and use the tracker".
- **Comment:** append the comment under a `## Comments` heading at the end of the file; add the
  heading with the first comment.
- **Close:** set the line to `Status: closed`.
- **Labels, milestones, `Blocked by` checks:** none; skip every step that sets or checks one.
- **Untriaged:** the file is not in `scope-issue` shape → stop with "rewrite issue `<n>` with
  `scope-issue` first".

## The upstream forge

- A commit, MR/PR or anything else pushed cites no local issue: no `Closes` line, no `#<n>`; on
  the forge `#<n>` names an upstream issue.
- An MR/PR → show its description as a draft in chat; push the branch and open the MR/PR only
  once the user confirms.
- The MR/PR merges → close the local issue.
- The user asks for an issue on the upstream tracker → show it as a draft in chat; file it
  upstream only once the user confirms the text.
