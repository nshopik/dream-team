# Repo doc conventions

Where a repo keeps its decision records, specs and ROADMAP, how it names them, and the record
template.

## Lookup

Take each of the paths, the file naming and the record template from the first that sets it:

1. The project's `CLAUDE.md` or `AGENTS.md`, or a doc it links (such as `docs/CONVENTIONS.md`).
2. An existing records folder with a known name: `docs/adr/`, `docs/decisions/`, `doc/adr/`; its
   files give the naming and the template.
3. The defaults below.

- A convention other than a default is used → one line in the chat report, for example
  `Conventions: docs/adr/ (existing folder)` or
  `Conventions: docs/adr/, ADR-NNN-slug.md (CLAUDE.md)`.
- The decision-record test and the record landing in the change's commit stay fixed, whatever
  the repo declares.

## Defaults

- Decision record: `docs/decisions/NNNN-slug.md`, template in
  [decision-record.md](../skills/craft-it/reference/decision-record.md).
- Spec: `docs/specs/NNNN-<topic>-design.md`.
- ROADMAP: `ROADMAP.md`, or `docs/ROADMAP.md` when that one exists.
- `NNNN`: four digits, the next free number in its folder on the target branch, from `0001`.
- The target takes that number before merge → rename the file to the next free one at rebase.

## Conventions doc in an own clone

- `docs/CONVENTIONS.md` records the paths, naming and template the lookup resolved; a ROADMAP row
  only when the repo has one.
- The block for the project `CLAUDE.md` (`AGENTS.md` when only that exists), verbatim:

```md
## Doc conventions

Decision records, specs, ROADMAP: `docs/CONVENTIONS.md`. Read the records touching your area first.
```

- `setup-dream-team` writes both in an own clone, the block in place of any layout the file
  declares.
- Writing a new decision record, spec or ROADMAP,
  `git config --local --type=bool --get dream-team.own` prints `true`, and the project's `CLAUDE.md`
  or `AGENTS.md` declares none of these conventions → in the same commit as that file, add
  `docs/CONVENTIONS.md` from the template below and the block.
- `dream-team.own` prints anything else → write neither.

## docs/CONVENTIONS.md template

````md
# Doc conventions

| Doc | Path |
|---|---|
| Decision records | `docs/decisions/NNNN-slug.md` |
| Specs | `docs/specs/NNNN-<topic>-design.md` |
| ROADMAP | `ROADMAP.md` |

## Decision records

Write a record only when all three hold:

1. Hard to reverse: changing your mind later costs something real.
2. Surprising without context: a future reader would ask why it was done this way.
3. A real trade-off: there were genuine alternatives and one was picked for specific reasons.

A decision that fails the test keeps its rationale in the commit body. A record goes in the
commit of the change it records.

```md
# {Short title of the decision}

{1-3 sentences: the context, what was decided, and why.}
```

A record replaced by a later decision keeps its file and gets `Superseded by <record-file>` under
its title.
````
