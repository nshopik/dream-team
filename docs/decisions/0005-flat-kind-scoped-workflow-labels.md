# Issue kinds take flat labels; workflow states and areas stay scoped

Skills label an issue's kind with a flat label (`bug`, `feature`, `maintenance`, `performance`,
`research`, `meta`) and keep `workflow::*` and `area::*` scoped, with one vocabulary on GitHub and
GitLab. Flat kinds are shorter and reuse GitHub's default `bug` and `wontfix`; a skill rule keeps
one kind per issue. Workflow states stay scoped because GitLab's scoped labels make them
exclusive, and an issue in two states at once is a real error, unlike a missing kind. Fully scoped
labels (the old `type::*`) and per-host vocabularies were rejected: the first duplicates GitHub's
defaults, the second makes every skill name each label twice. An issue closed as not planned also
gets `wontfix`, since GitLab has no close reason.
