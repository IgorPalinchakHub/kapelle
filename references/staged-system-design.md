# Staged system design

Read only when a feature needs several independently meaningful architecture decisions, shared
contracts across components, or the developer explicitly requests staged architecture approval.
A local improvement with one clear solution keeps the ordinary single slice approval.

## 1. Agree on the whole

Follow the project's architecture-rules skill first. Explain current behavior and architecture,
the intended outcome, boundaries, owners, constraints, and the proposed end-to-end path. Name the
main alternatives and why the recommended direction fits this project. Separate facts from
assumptions; do not invent throughput, latency, availability or recovery targets.

Keep `design.md` as the compact map and add `<!-- kapelle-design: staged-v1 -->`. Write
`design/architecture-review.md` with the overall direction and a dependency-ordered review table:

```markdown
# Architecture direction
Current architecture, proposed boundaries, ownership, main flow, constraints and trade-offs.

## Review order
| Part | Design | Contracts |
| --- | --- | --- |
| reservation | design/reservation.md | contracts/reservation.md |
| checkout | design/checkout.md | contracts/reservation.md, contracts/payment.md |

## Candidates and open decisions
Future capabilities, assumptions and unresolved decisions outside the current slice.
```

Use plain relative Markdown paths and lower-case part identifiers; no links/backticks in the table.
List only parts required by the active slice. Each row owns a distinct detail document. Contracts
lists **every consumed or produced shared contract**, or `-` when none. Outline each contract's
ownership and boundary before detailing consumers. Keep future capabilities outside the table.
This human table is the durable review order; no machine coordination graph is required.

Present the concrete whole and decomposition, then request explicit direction approval. Stop
before detailed part design. Approval covers direction, not implementation. Use `--approve-vision`
only after the developer explicitly approves that direction.

## 2. Design and approve one part at a time

After direction approval, `--part <id>` drafts or revises the next part in table order. Read the
approved direction, relevant project rules, upstream boundaries and only the required contracts.
An architectural part is a responsibility boundary; it is not a separate implementation slice.
Split further only when the part contains another independently consequential decision.

Cover what is applicable, and explain consequential exclusions briefly:
- current responsibility, intended change, inputs/outputs, owner and dependency direction;
- main runtime flow, alternatives and errors; domain invariants and state transitions;
- contracts, compatibility, data ownership and transaction/consistency boundaries;
- authorization, idempotency, concurrency, retries/timeouts and partial failure recovery;
- relevant quality constraints, observability, rollout/rollback, trade-offs and open risks;
- acceptance scenarios satisfied and the basic or critical checks needed before implementation.

Use a small sequence or boundary diagram when it clarifies interaction. Keep extensive detail in
the part document; the root design remains navigable. No compulsory diagrams, ADRs or test quota.
Remaining noncritical tests stay at `verify`.

Summarize in chat: **what exists → what changes → why → consequences → decision needed**.
For example: “Today a reservation is written before payment. I propose an expiring reservation
and idempotent payment confirmation. That avoids duplicate charges, but requires expiration
handling. Approve this interaction, or should payment precede reservation?” Link the design only
after this explanation. Never present raw gate IDs or paragraph references as the question.

Wait for explicit part approval (`--approve-part <id>`). Then continue with the next part on the
next planning turn; never treat approval as permission to implement. A contradiction with the
overall direction requires updating and reapproving the direction first. Do not silently expand
scope or detail future candidates.

## 3. Integrate and approve the slice

Once all active parts are approved, write `design/integration.md`: the complete user-to-system
flow, matching producer/consumer contracts, ordering and data ownership, permission boundaries,
cross-part failure handling, unresolved risks, and acceptance coverage. Reconcile conflicting
assumptions and duplicate responsibilities. Unknown blocking decisions prevent approval.

Update the compact `design.md` map and `tasks.md` with the smallest coherent end-to-end slice,
not one task per component. Explain the integrated result and its trade-offs in chat. A single
explicit `--approve` approves this integration and the implementation slice together. Only then
offer `implement`. Structural validation cannot establish that the architecture is semantically
correct; the main agent must perform this integration review before requesting approval.

## Revisions and recovery

Approval fingerprints enforce freshness. A private part-document change invalidates that part
and the overall slice; independent parts remain approved. A shared-contract change invalidates
all rows listing that contract. Direction, scope/specification or architecture-guidance changes
invalidate all affected direction-dependent approvals conservatively. Table changes require
direction reapproval. Never delete the staged marker or review table to bypass pending review.

Reapprove stale parts in table order, then reconcile integration and renew slice approval.
`amend` promotes only the next requested capability, preserves implemented behavior, and updates
the review table when the active slice changes. Candidate parts need no approval until promoted.
Missing review state routes to `start`; rebuilding state never fabricates human approval. Old
feature packages remain read-only context and never supply reusable approvals.
