# setup-dream-team writes docs/CONVENTIONS.md eagerly in an own clone

Superseded by 0009-repo-data-via-setup.md

`setup-dream-team` checks an own clone for a `docs/CONVENTIONS.md` and a `## Doc conventions`
block pointing at it, writes whichever is missing from what the `references/repo-conventions.md`
lookup resolves, and moves a layout `CLAUDE.md` declares into the file. It checks only that both
exist, since the lookup then reads the file itself; the first writer stays as the fallback where
setup never ran, and 0004's lookup order and fixed decision test still stand. 0004 left the file
to the first skill writing a record, spec or ROADMAP and rejected a setup-time copy because it
drifts from the plugin, but own repos then went months with records and no conventions doc, and
agents guessed the layout; that reference rarely changes, and a guessed layout costs more than a
copy that drifts.
