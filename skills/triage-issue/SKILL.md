---
name: triage-issue
description: >-
  Triages one tracker issue before it is built: checks whether the code already does what it
  asks, reproduces a bug claim, asks the reporter for facts only they know and parks the issue
  on `workflow::blocked`, puts design and scope choices to the user, and rewrites the body in
  scope-issue form with the original report kept at the end. On an issue with
  `workflow::needs-brainstorm`, runs brainstorm's question rounds and rewrites its proposal. With no
  argument, lists the untriaged open issues, the blocked ones whose reporter replied and the
  needs-brainstorm ones. Use when the user asks to triage, check or vet an issue, a legacy issue
  or one filed by someone outside the project — e.g. "triage #42", "triage-issue", "what needs
  triage" — or when build-issue stops and names triage-issue. Not for building the issue (use
  build-issue) or filing a new one (use scope-issue).
argument-hint: "[<issue-number>]"
---

# triage-issue

One issue per invocation.

- Never start the build.
- Create no label, and write no AI disclaimer line.

## Untriaged

An open issue is untriaged when its body has no collapsed `Original report` block and either
holds:

- Its body is in none of: the shape `scope-issue` gives its kind; the older problem, proposal
  and `Done when …` paragraph; the older context, problem, proposal.
- Its author is outside the project.

Outside the project, by forge permission:

- GitHub: an `author_association` other than `OWNER`, `MEMBER` or `COLLABORATOR`
  (`gh api repos/<owner>/<repo>/issues/<n> --jq .author_association`).
- GitLab: an access level below Developer (30)
  (`glab api projects/<p>/members/all/<author id> | jq .access_level`; a 404 is none).

An outside author's body counts its `Original report` block only when a project member made the
last body edit:

- GitHub: the issue's `editor` is set and is not the author; only collaborators edit another
  user's issue:
  `gh api graphql -f query='{repository(owner:"<o>",name:"<r>"){issue(number:<n>){editor{login}}}}'`
- GitLab: the issue's `lastEditedBy` has Developer access or above, by the check above:
  `glab api graphql -f query='{project(fullPath:"<p>"){issue(iid:"<n>"){lastEditedBy{id}}}}'`

## Queue: no argument

- List the open untriaged issues, oldest first, leaving out those with `workflow::blocked` and
  triage notes.
- Add the open issues with `workflow::blocked` whose author commented after the last triage
  notes.
- Add the open issues with `workflow::needs-brainstorm`.
- Ask which one to triage, then run the steps below on it.

```
- **#<n>** <title> — <not in scope-issue form | outside author | reporter replied | needs brainstorm>
```

## 1. Read

- Fetch title, body, labels and comments per `<base directory>/../build-issue/SKILL.md` step 1.
- Triaged, with no triage notes and no `workflow::needs-brainstorm` → report it ready and stop.
- Read every earlier triage notes comment and the replies after it.
- Never re-ask a question a reply answered.
- The reporter answered every question → remove `workflow::blocked`.

## 2. Already done

- Search the code for the requested behaviour by what it does, not the issue's wording.
- Read the commits since the issue opened for a change that did it.
- Found → close the issue with a comment naming the file, symbol or commit where it lives; stop.

## 3. Bug claim

- The issue reports a bug → reproduce it from the reporter's steps on the default branch,
  locally first.
- It needs a lab host the project's `CLAUDE.md` or `AGENTS.md` names → run it through
  `dream-team:lab-runner`.
- Record one verdict: confirmed, with the code path; not reproduced; or not enough detail.

## 4. Facts only the reporter knows

- A missing step, version or environment, or a bug not reproduced → post the triage notes
  comment, add `workflow::blocked`, leave the body unchanged, and stop.
- Each question names the exact command output, version, setting or step wanted.

```
## What we've established so far
- <fact, and how it was checked>

## What we still need from you
- <question>
```

## 5. Design and scope choices

- Load `scope-issue`.
- No `workflow::needs-brainstorm`, a design or scope choice open → settle it with the user per its
  Open questions, as for an issue the user asked for in chat, before the rewrite.
- The issue has `workflow::needs-brainstorm` → run `dream-team:brainstorm` on its proposal's open
  items, skipping its path proposal and hand-off; the issue is the path.
- The user rejects the request → close the issue as not planned with a comment giving the reason,
  add `wontfix`, write no repo file, and stop.

## 6. Rewrite

- Rewrite the body in `scope-issue` form, carrying the verified facts, the bug verdict and the
  user's answers.
- End the body with the reporter's text, verbatim, in a collapsed block.
- The body already has that block → keep it as it is.
- The issue has `workflow::needs-brainstorm` → rewrite its proposal per `scope-issue` Updates with
  the user's answers, in place of the three bullets above.
- No open item is left in its proposal → remove `workflow::needs-brainstorm`.

```
<details><summary>Original report</summary>

<reporter's text, verbatim>

</details>
```

## Report

- Leave out a line with nothing to report.

```
- **Issue:** #<n> <title>
- **Outcome:** closed, already done | closed, rejected | waiting on the reporter | needs brainstorm | ready
- **Searched:** <paths, symbols and commit ranges the already-done check read>
- **Bug:** confirmed at <code path> | not reproduced | not enough detail
- **Still open:** <open items left in the proposal; `workflow::needs-brainstorm` stays>
- **Next:** `build-issue #<n>`
```
