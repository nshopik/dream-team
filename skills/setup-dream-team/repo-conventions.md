# Repo doc conventions

What `setup-dream-team` writes to an own clone's `docs/CONVENTIONS.md`: where the repo keeps its
decision records, specs, ROADMAP and glossary, how it names them, and the record template.

## Lookup

Take each of the paths, the file naming and the record template from the first that sets it:

1. The project's `CLAUDE.md` or `AGENTS.md`, or a doc it links (such as `docs/CONVENTIONS.md`).
2. An existing records folder with a known name: `docs/adr/`, `docs/decisions/`, `doc/adr/`; its
   files give the naming and the template.
3. The defaults below.

## Defaults

- Decision record: `docs/decisions/NNNN-slug.md`, the record template below.
- Spec: `docs/specs/NNNN-<topic>-design.md`.
- ROADMAP: `ROADMAP.md`, or `docs/ROADMAP.md` when that one exists.
- Glossary: `GLOSSARY.md`.

## Conventions doc

- `docs/CONVENTIONS.md` records the paths, naming and template the lookup resolved; a ROADMAP row
  only when the repo has one.
- The block for the project’s selected `AGENTS.md` or `CLAUDE.md`, verbatim:

```md
## Doc conventions

Decision records, specs, ROADMAP: `docs/CONVENTIONS.md`. Read the records touching your area first.
```

- `setup-dream-team` writes both, the block in place of any layout the file declares.

## docs/CONVENTIONS.md template

````md
# Doc conventions

| Doc | Path |
|---|---|
| Decision records | `docs/decisions/NNNN-slug.md` |
| Specs | `docs/specs/NNNN-<topic>-design.md` |
| ROADMAP | `ROADMAP.md` |
| Glossary | `GLOSSARY.md` |

`NNNN` is four digits, the next free number in its folder on the target branch, from `0001`. The
target takes that number before merge → rename the file to the next free one at rebase.

## Decision records

```md
# {Short title of the decision}

{1-3 sentences: the context, what was decided, and why.}
```

Add these sections only when they add real value; most records need none:

- **Considered Options**: only when the rejected alternatives are worth remembering.
- **Consequences**: only when non-obvious downstream effects need to be called out.
- **Diagram**: only when the decision relates 3 or more named parts; one fenced `mermaid` block
  of at most 12 nodes, no styling, replacing the prose it shows.

A record replaced by a later decision keeps its file and gets `Superseded by <record-file>` under
its title. The new record says why the old decision lost.
````
