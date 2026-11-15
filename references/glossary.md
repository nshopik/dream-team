# Glossary

The project's agreed terms, kept in a root `GLOSSARY.md`.

## Terms

- `GLOSSARY.md` exists → read it before writing; use its terms, never a word under `_Avoid_:`.
- A thing with no glossary term → the field-standard word, or a plain phrase.
- No field word or plain phrase fits → propose a term and its definition with AskUserQuestion, and
  use it only after the user's OK.
- A term the user coined or OK'd in the conversation → approved; do not re-ask.
- A run that must not prompt (an issue found during other work) → never coin; use the plain phrase.

## Writing an approved term

- `GLOSSARY.md` exists → add the term's entry.
- No `GLOSSARY.md` and `git config --get dream-team.own` prints `true` → create `GLOSSARY.md` with
  the entry, and in the same commit add the pointer line to `CLAUDE.md` (to `AGENTS.md` when only
  that exists).
- No `GLOSSARY.md` and `dream-team.own` prints anything else → write neither.
- Commit the entry with the spec or decision record that first uses the term.
- Term used in an issue body alone, and a write above applies → make that write an item of the
  issue's proposal, quoting the entry and, when the item creates `GLOSSARY.md`, the pointer line
  verbatim.
- An entry: the term in bold, one or two sentences on what it is, then an `_Avoid_:` line of
  rejected synonyms.
- Project-specific terms only: no general programming concept, no implementation detail.
- Pointer line, verbatim:

```md
Terms: `GLOSSARY.md`; use its terms, never a word under `_Avoid_:`.
```

## GLOSSARY.md template

```md
# Glossary

**Shadow zone**:
A copy of a zone signed with the next key and served only to the validator under test.
_Avoid_: staging zone, test zone
```
