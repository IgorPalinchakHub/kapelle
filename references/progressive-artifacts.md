# Progressive feature artifacts

Kapelle keeps a complete high-level feature map while detailing and implementing only the currently
approved vertical slice. High-level coverage is not permission to implement candidate behavior.

## Durable format markers

New lightweight features begin `spec.md` with both markers:

```md
<!-- kapelle-workflow: lightweight-v1 -->
<!-- kapelle-artifacts: progressive-map-v1 -->
```

The workflow marker supports recovery. The artifact marker enables deterministic structural
validation. Features migrated from an older Kapelle layout may keep their historical structure
until the developer explicitly revises them.

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

## Validation boundary

Kapelle deterministically checks markers, required headings, order, non-empty sections, detail-file
shape, and size caps. The developer and agent still review semantic quality, project fit, and
trade-offs; a structural validator cannot prove that a design is correct.
