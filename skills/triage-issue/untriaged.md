# Untriaged

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
