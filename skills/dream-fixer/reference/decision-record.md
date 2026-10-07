# Decision record format

Decision records live in `docs/decisions/` and use sequential numbering: `0001-slug.md`,
`0002-slug.md`, etc.

## Template

```md
# {Short title of the decision}

{1-3 sentences: what's the context, what did we decide, and why.}
```

## Optional sections

Only include these when they add genuine value. Most decision records won't need them.

- **Considered Options**: only when the rejected alternatives are worth remembering
- **Consequences**: only when non-obvious downstream effects need to be called out

## Superseding

A record replaced by a later decision keeps its file and gets one line under its title:
`Superseded by <record-file>`. The new record says why the old decision lost.

## Numbering

Use the next free number in `docs/decisions/` on the target branch. If the target takes that
number before merge, rename the record to the next free one at rebase.

## When to write a decision record

All three of these must be true:

1. **Hard to reverse**: the cost of changing your mind later is meaningful
2. **Surprising without context**: a future reader will look at the code and wonder "why on earth
   did they do it this way?"
3. **The result of a real trade-off**: there were genuine alternatives and you picked one for
   specific reasons

A decision that fails the test keeps its rationale in the commit body.

A spec in `docs/specs/` that the change supersedes gets a record only when the reason it lost
passes the same test.

### What qualifies

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
