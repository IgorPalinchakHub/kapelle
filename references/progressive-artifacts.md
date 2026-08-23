# Progressive feature artifacts

Kapelle keeps a complete high-level feature map while detailing and implementing only the currently
approved vertical slice. High-level coverage is not permission to implement candidate behavior.

## Durable format markers

New lightweight features begin `spec.md` with both markers:

```md
<!-- kapelle-workflow: lightweight-v1 -->
<!-- kapelle-artifacts: progressive-map-v1 -->
<!-- kapelle-artifact-contract: living-v1 -->
```

The workflow marker supports recovery. The artifact marker enables deterministic structural
validation. The living-contract marker enables the compact current/change/result, technical-delta,
and workstream checks below. Existing progressive packages without that marker remain compatible
until the developer explicitly revises their active slice; revision adds the marker and the missing
compact structure without rewriting unrelated history.

## High-level specification

`spec.md` uses these headings in this order:

```md
# Feature specification

## 1. Problem and intent
## 2. Current behavior
## 3. Committed behavior
## 4. Use-case map
## 5. Business rules and invariants
## 6. Candidate capabilities
## 7. Exclusions, assumptions, and open decisions
```

- `Committed behavior` contains only observable behavior approved for the implemented base or the
  current slice.
- `Use-case map` names all currently known user/business outcomes at high level. It is a map, not a
  task backlog.
- `Candidate capabilities` contains non-binding hypotheses. They are not requirements, tasks, or
  implementation permission until promoted through `/kapelle:amend`.
- Unknown behavior stays explicit. Do not complete the map by inventing requirements.

For a new or explicitly revised active slice, `Committed behavior` uses these subheadings:

```md
### Intended change
### Resulting behavior
### Preserved behavior
### Acceptance scenarios
```

- `Intended change` says what this slice changes, not how every file will be edited.
- `Resulting behavior` says what a user, caller, operator, or downstream system can observe after
  the slice.
- `Preserved behavior` names relevant compatibility and invariants. For a brand-new isolated
  capability it may say that no prior behavior exists, but it is never left empty.
- `Acceptance scenarios` contains at least one observable success scenario and adds only relevant
  failure or edge scenarios. It may use compact Given/When/Then prose without forcing identifiers.

For brownfield work, `Current behavior` describes the affected as-built flow before the committed
delta. Do not describe the requested result as though it already exists.

Prefer at most 250 lines and remain below 320 lines. Move genuinely independent behavior into
`specs/`, not into more root documents.

## High-level system design

`design.md` uses these headings in this order:

```md
# System design

## 1. Context and constraints
## 2. System boundaries and responsibilities
## 3. End-to-end flow
## 4. Domain and data
## 5. Contracts and integrations
## 6. Decisions, risks, and deferrals
## 7. Current walking skeleton
```

The document maps the likely end-state boundaries at high level but designs only committed behavior
in implementation detail. Candidate components and integrations are labelled directional and
unconfirmed. Prefer at most 180 lines and remain below 240 lines.

For a new or explicitly revised active slice, `System boundaries and responsibilities` uses:

```md
### Current architecture
### Resulting architecture
### Technical delta
```

- `Current architecture` is a brief evidence-backed view of only the affected scope. For a new
  isolated capability, state the existing integration point or that the capability is absent.
- `Resulting architecture` gives enough as-designed responsibility and boundary detail to guide
  this slice.
- `Technical delta` names moved, added, removed, or compatibility-sensitive responsibilities.

For behavior-preserving refactoring, also make preserved observable behavior and public contracts
explicit in the corresponding specification section. If observable behavior changes, treat the
slice as a behavior change rather than hiding it under refactoring.

`Current walking skeleton` describes one production-shaped path across every boundary needed to
prove the first usable outcome. It must not be a list of empty endpoints, services, mocks, or TODOs.

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
input until explicitly migrated. A normal slice has zero or one diagram; a genuinely complex slice
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
