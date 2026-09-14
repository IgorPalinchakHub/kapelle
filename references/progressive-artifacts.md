# Detailed feature artifacts

Use [artifact-basics.md](./artifact-basics.md) for root documents. Read this file only when a detail
trigger applies, a material quality constraint changes, or final verification reconciles details.
Simple edits use the basic contract alone.

## Proportional completeness review

During start/amend, review the affected behavior for success, failure/edge cases, permissions,
domain invariants, and interactions with other components. This is an internal applicability pass,
not five required scenarios or five developer questions. Translate applicable concerns into
observable acceptance scenarios and preserved behavior. Summarize unrelated categories together
in exclusions when useful; do not invent authorization or integration requirements for an isolated
change. Every committed use-case outcome must have an acceptance scenario or an explicit link to
one in a detailed specification. Candidates remain outside this coverage.

Review architecturally significant concerns: workload/performance, availability/recovery,
consistency/concurrent or repeated operations, security/privacy, observability, and
deployment/compatibility/rollback. Reuse scoped project defaults when applicable. In existing
spec/design sections, record only constraints or changes that affect a decision:

`operating context -> agreed observable target -> design response -> how to verify`

Targets come from the user or cited project evidence. Never invent latency, capacity, retention,
or recovery numbers. Record unknowns and ask only when they block a safe current-slice decision.
Choose verification appropriate to the requirement: load tests for capacity/latency, recovery
checks for restore guarantees, permission checks for access, migration checks for compatibility.
A numeric requirement does not automatically require a load test. These checks can be planned now
and performed at verify; planning does not require a new early suite.

For a small improvement that reuses existing boundaries and policies, a sentence about the
applicable default and unchanged concerns is enough. Keep the existing root headings and one
workstream. Do not add an applicability document, an Arc42 bundle, a diagram, an ADR quota, or a
test-planning stage. Additional detail follows the existing triggers below.

## Detailed use-case specifications

Create `specs/<use-case>.md` only when the use case is being promoted into committed behavior and
has alternatives, authorization, meaningful failures, subprocess reactions, or enough rules that
an inline section would be hard to review. Use:

```md
# <Use-case name>

## Outcome
## Trigger and actors
## Preconditions
## Main flow
## Alternatives and failures
## System reactions
## Acceptance scenarios
```

Simple behavior remains in `spec.md`. Candidate use cases are never expanded speculatively.

Within these existing headings, make the scenario executable in prose:

- `Outcome` states success postconditions: what is true after completion, not just the intention.
- `Main flow` numbers the steps and distinguishes actor actions from system responses.
- `Alternatives and failures` names the branch point (for example, "At step 3, storage fails"),
  response, and failure postconditions: what is persisted, unchanged, or partially completed.
- State retry, cancellation, duplicate/concurrent operation, and compensation behavior only when
  applicable. Do not infer a guarantee such as atomicity from the happy path.
- `Acceptance scenarios` covers the meaningful outcomes and references the owning rule when useful.

No new mandatory heading or retroactive detail-file migration is introduced.

## Domain model

Use the `Domain and data` section of `design.md` for a simple CRUD-shaped change. Create
`design/domain-model.md` when the feature introduces or changes an aggregate, lifecycle/status
transition, money or authorization invariant, domain event, ownership boundary, or non-trivial
relationship:

```md
# Domain model

## Domain language
## Aggregates and ownership
## State and behavior
## Invariants
## Events and side effects
## Persistence mapping
```

Describe behavior, not only fields. Observable business rules remain in `spec.md` or a use-case
specification; this document explains which model owns and enforces them.

## Other detail triggers

| Evidence | Durable detail |
|---|---|
| Public API, command, event, or external boundary | `contracts/` |
| Three or more interacting components or asynchronous flow | focused `design/*.md` or sequence |
| Independent backend, frontend, or worker ownership | one focused aspect design |
| Expensive-to-reverse architectural choice | ADR |
| No independently useful detail | no additional file |

Detail is just-in-time. `/kapelle:amend` promotes one requested use case, updates the high-level map,
adds only its necessary details, and proposes changes to earlier documents when the new evidence
contradicts them.

## Evidence-triggered diagrams

Diagrams are zero-by-default. Add the smallest visual only when it materially clarifies evidence
that prose would make hard to review:

| Evidence | Diagram |
|---|---|
| Changed system boundary, ownership, security boundary, or three or more architectural participants | focused architecture flow |
| Ordering, async handoff, retry, rollback, or meaningful cross-component failure | runtime sequence |
| Non-trivial lifecycle and constrained transitions | state diagram |
| Sensitive or external data movement | data-flow diagram |
| Refactor moves responsibilities and the delta is hard to see in prose | concise before/after architecture |

Use diffable Mermaid source. Prefer one focused block inline in `design.md`; move complex detail to
`design/<aspect>.md`. New work does not create root `sequences.md`; that path remains compatibility
read-only context for a new feature. A normal slice has zero or one diagram; a genuinely complex slice
may have two or three focused diagrams rather than one crowded visual.

Every diagram is followed by a short plain-language explanation of participants, responsibilities,
ordering, and important branches. Show runtime or architectural behavior, not every method, class,
or line-by-line code path. Do not ask for separate diagram approval: the diagram is reviewed with
the active slice. Candidate architecture is labelled directional and never presented as as-built.

`/kapelle:verify` reconciles triggered diagrams with confirmed participants, ordering, failures,
state, and boundaries. Correct or remove a stale visual. Structural validation checks closed,
non-empty Mermaid blocks and nearby prose; semantic and syntax accuracy remain an evidence-based
review responsibility, using a project-native renderer or checker when available.

## Compact workstream

New or explicitly revised living-contract packages keep one active walking-skeleton workstream,
split into at most three top-level unchecked checkboxes only when reviewability requires it. Each
active checkbox includes:

```md
- [ ] **W1 Deliver the observable outcome**
  - Changes: affected behavior and technical areas.
  - Done when: one objective completion signal.
  - Verify: focused evidence that will demonstrate the outcome.
```

Dependencies are added only when there is more than one workstream and the dependency is real.
Do not expand a small slice into layer tasks, ownership metadata, estimates, or a DAG by default.
Checked implemented-base entries may keep their historical shape. Adding the living-contract marker
does not require backfilling `Changes`, `Done when`, or `Verify` into unrelated completed work.

## Lightweight traceability

For a living-contract active slice, each acceptance scenario has a stable `AC-NN` identifier. Each
active workstream names the scenarios it covers on its checkbox line, using individual identifiers
or a compact numeric range. Its required `Verify` field completes the readable path:

```text
observable acceptance scenario -> coherent workstream -> focused verification
```

Deterministic validation requires at least one active scenario, rejects unknown references from an
unchecked workstream, and requires every active scenario to be covered by the active workstream.
When no unchecked work remains, checked implemented-base work provides the completed coverage.
Checked historical work does not satisfy coverage while a new slice is active. It may retain
historical coverage that is no longer in the active committed section. Candidate
capabilities and high-level use-case-map items are not traced until promoted.

Do not introduce a mandatory machine DAG, owners, estimates, or file inventories for this purpose.
Internal identifiers never appear in developer questions.

At planning time, `Verify` names the smallest useful evidence for the covered outcomes. At final
verification, reconcile active scenarios in both the root and detailed specifications with actual
test paths/names or specific manual observations. A detailed scenario may reference a root AC;
otherwise give it a stable local reference when needed for unambiguous evidence. Keep this mapping
in existing workstream results or scenario prose, using a small inline table only when clearer.
Do not create a separate traceability report by default. Structural AC/workstream validation alone
does not prove detail-scenario or test coverage; verify owns that semantic check.

## Final as-built convergence

`/kapelle:verify` reconciles root documents and every triggered detail file with confirmed code,
tests, contracts, data behavior, and architecture guidance. It updates `Current behavior` to the
confirmed resulting behavior, preserves the implemented slice description as useful context, and
keeps remaining candidates non-binding. A detailed user or technical file is added during
verification only when implementation evidence meets its normal trigger and the file remains
independently useful after completion.

An implementation contradiction that changes approved observable behavior or architecture returns
through `/kapelle:amend`; verification does not silently redefine intent.

## Validation boundary

Kapelle deterministically checks markers, required headings, order, non-empty sections, detail-file
shape, and size caps. The developer and agent still review semantic quality, project fit, and
trade-offs; a structural validator cannot prove that a design is correct.
