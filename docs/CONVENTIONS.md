# Doc conventions

| Doc | Path |
|---|---|
| Decision records | `docs/decisions/NNNN-slug.md` |
| Specs | `docs/specs/NNNN-<topic>-design.md` |

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
