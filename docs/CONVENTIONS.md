# Doc conventions

| Doc | Path |
|---|---|
| Decision records | `docs/decisions/NNNN-slug.md` |
| Specs | `docs/specs/NNNN-<topic>-design.md` |
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
