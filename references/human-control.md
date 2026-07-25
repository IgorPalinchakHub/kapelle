# Human-controlled development workflow

Kapelle's preferred workflow is a progressive, reviewable decision pipeline:

```text
start -> spec -> design -> plan -> base-functional-tests
      -> implement -> unit-tests -> verify -> finalize
```

`amend` may interrupt implementation, verification, or developer testing.

There is no legacy runtime pipeline. Unmarked feature directories route to `migrate`.

For eligible XS/S features, `start` combines `spec + design + plan` into a fast-lane draft with one
planning approval. Standard lane retains separate business, architecture, and delivery approvals.
See `fast-lane.md`.

## Human control

The agent researches and proposes. The developer owns product and technical decisions.
Whenever a decision requires developer input, follow
[`developer-questions.md`](./developer-questions.md): ask a standalone plain-language question
about the intended change and its trade-offs, never about internal artifact notation.

Standard lane has five explicit review gates:

1. high-level feature outline;
2. detailed business specification;
3. architecture package;
4. delivery plan;
5. final as-built result.

Fast lane replaces the first four with one `feature-plan` gate and retains final approval.

Silence is never approval. Starting the next gated phase, using its explicit approval option, or
answering the stage's approval prompt is the required affirmative action. Persist accepted gates
only through `scripts/review_gate.py`. Canonical gate names and exact artifact sets come from
`dispatcher/artifact-dependencies.json`; every fingerprint is a full SHA-256.

The standard outline gate fingerprints stable `proposal.md` and `_context/architecture.md`. The
following `spec` stage expands `spec.md`, so the outline gate must not fingerprint that mutable
draft. The later `business-spec` gate fingerprints `proposal.md`, the completed `spec.md`, and
`specs/`. An accepted business specification therefore remains mechanically distinguishable from
its earlier outline.

`proposal.md` carries
`<!-- kapelle-workflow: human-controlled-v1; lane: fast|standard -->`. This durable marker
lets `/kapelle:status` recover the correct route when `_kapelle/` was deleted; lost approvals and
test output are still never fabricated.

Every stage response is short and contains:

- what changed;
- decisions required from the developer, normally at most three;
- human-readable files to review;
- the exact next command.

## Progressive artifacts

Keep the feature root readable:

```text
proposal.md
spec.md
specs/
design.md
design/
contracts/
test-plan.md
tasks.md
diagrams/
```

Create subfiles only when they make an independent business process or technical boundary easier
to review. Do not create one file per minor rule.

`specs/` may contain business rules, scenarios, subprocesses, integrations, and edge cases.
`design/` may contain bounded component designs, an optional domain model, status flows, and
integration designs. Domain-model artifacts are created only when domain impact is `extend` or
`new`.

## Test timing

Kapelle deliberately uses this sequence:

```text
contracts
-> base endpoint/use-case functional tests
-> production implementation
-> all unit tests
-> complete verification
```

Before implementation, create only a small executable behavioral safety net:

- endpoint inputs, outputs, status codes, and principal validation errors;
- public use-case method happy paths, principal business errors, and observable side effects;
- critical boundary contracts when directly affected.

Do not write unit tests during production task implementation. This timing is a fixed workflow
decision, not an adaptive TDD choice. Design must still keep business logic testable.

After all production tasks are implemented, `unit-tests` plans and writes unit tests for changed
or new units. `verify` then runs functional, unit, integration, contract, static-analysis, lint,
and build checks under the explicit validation policy.

## Implementation checkpoints

`implement` accepts:

```text
--checkpoint=task
--checkpoint=workstream
--checkpoint=none
```

- `task`: stop after every task for developer review;
- `workstream`: stop after each coherent workstream;
- `none`: implement all dependency-ready work before returning.

Regardless of checkpoint, each task records code paths and a short behavior summary. It does not
claim validation completion until the later unit-test and verification phases pass.

## Amendments and finalization

Developer testing may invoke `amend`. The amendment captures a revision, determines affected
business/design/contracts/tests/tasks/code, invalidates downstream evidence, and updates canonical
human documents. History remains internal; do not create versioned copies of every document.

`finalize` performs as-built convergence, fresh independent review, generates diff-friendly
Mermaid feature-flow and architecture diagrams by default, and writes the approved release
version. Draw.io may be added when a project capability exists and manual layout is valuable.

Kapelle never performs git operations.
