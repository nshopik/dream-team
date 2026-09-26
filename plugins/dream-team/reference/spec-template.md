# <topic>

**Date:** YYYY-MM-DD
**Status:** Draft | Accepted | Superseded by `<spec-file>`

Every section below is optional except Context, Decision, and Consequences. An
empty section is deleted, never filled with "N/A" or "None". One spec lands one
feature; if it needs two, split it.

## Context

The problem, and enough of the current model to judge the decision. One or two
paragraphs. No restating of the title.

## Decision

What we are doing, stated flatly. Not why the alternatives lost — that is below.

## Expertise required

Which domains and capabilities this needs, and for what. Name domains, not specific
agents. A fresh agent reads this to pick reviewers and implementers before reading
the Design, so it sits high; humans skip it.

## Rejected alternatives

One bullet each: the option, then what killed it. Bullets, not a pros/cons matrix.
Delete the section if nothing real was considered.

## Consequences

What gets worse, not just what gets better. A section with no negative entry is
not finished. This is the section future-you rereads.

## Design

The detail: invariants, seams, signatures, config surface, edge cases. Subsections
scaled to their complexity. This is usually the bulk of the document.

## Affected files

Path — what changes. Include the files that deliberately do **not** change when a
reader would expect them to.

## Testing (TDD)

Numbered cases, each pinning one behavior. Note any test-harness gotcha.

## Out of scope

Adjacent work this spec deliberately does not do, and where it lives instead.

