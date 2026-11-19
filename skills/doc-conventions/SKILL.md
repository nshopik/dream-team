---
name: doc-conventions
description: >
  Holds a repo's doc conventions: the lookup for where its decision records, specs and ROADMAP
  live and how they are named, the defaults, the decision-record test, the record template and
  the docs/CONVENTIONS.md template. Use when a skill writes or finds a decision record, spec or
  ROADMAP, or checks whether a choice passes the decision-record test.
user-invocable: false
---

# doc-conventions

Where a repo keeps its decision records, specs and ROADMAP, how it names them, when a decision
gets a record, and the record template.

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

- Decision record: `docs/decisions/NNNN-slug.md`, template in **Decision records** below.
- Spec: `docs/specs/NNNN-<topic>-design.md`.
- ROADMAP: `ROADMAP.md`, or `docs/ROADMAP.md` when that one exists.
- `NNNN`: four digits, the next free number in its folder on the target branch, from `0001`.
- The target takes that number before merge → rename the file to the next free one at rebase.

## Decision records

### Template

```md
# {Short title of the decision}

{1-3 sentences: what's the context, what did we decide, and why.}
```

### Optional sections

Only include these when they add genuine value. Most decision records won't need them.

- **Considered Options**: only when the rejected alternatives are worth remembering
- **Consequences**: only when non-obvious downstream effects need to be called out
- **Diagram**: only when the decision relates 3 or more named parts; one fenced `mermaid` block
  of at most 12 nodes, no styling, replacing the prose it shows

### Superseding

A record replaced by a later decision keeps its file and gets one line under its title:
`Superseded by <record-file>`. The new record says why the old decision lost.

### Decision-record test

All three of these must be true:

1. **Hard to reverse**: the cost of changing your mind later is meaningful
2. **Surprising without context**: a future reader will look at the code and wonder "why on earth
   did they do it this way?"
3. **The result of a real trade-off**: there were genuine alternatives and you picked one for
   specific reasons

A decision that fails the test keeps its rationale in the commit body.

A spec the change supersedes gets a record only when the reason it lost passes the same test.

#### What qualifies

- **Architectural shape.** "The write model is event-sourced; the read model is projected into
  Postgres." "Each environment is its own Terraform root module with its own state file, not one
  root with workspaces."
- **Integration patterns between systems.** "Ordering and Billing talk through domain events, not
  synchronous HTTP." "Hosts pull config from the Ansible control node on a timer; nothing pushes
  over SSH."
- **Technology choices that carry lock-in.** Database, message bus, auth provider, state backend,
  secrets store, orchestrator. Not every library or module: just the ones that would take a
  quarter to swap out.
- **Boundary and scope decisions.** "Customer data is owned by the Customer module; others
  reference it by ID only." "The network team owns the VPC and its subnets; app stacks read them
  through remote state and never create their own." The explicit no-s are as valuable as the
  yes-s.
- **Deliberate deviations from the obvious path.** "Queries are hand-written SQL, not an ORM,
  because the reports need window functions." "Nodes run a pinned kernel instead of the distro's
  latest because the NIC driver breaks on newer ones." Anything where a reasonable reader would
  assume the opposite. These stop the next engineer from "fixing" something that was deliberate.
- **Constraints not visible in the code.** "Responses must return in 200 ms because of the
  partner API contract." "The vendor API allows 100 requests a minute, so the provider runs with
  `parallelism = 4`." "Card data stays in one region for PCI scope."
- **Rejected alternatives when the rejection is non-obvious.** If you considered GraphQL and
  picked REST, or considered Kubernetes and picked plain systemd units, for subtle reasons, record
  it; otherwise someone will suggest it again in six months.

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
