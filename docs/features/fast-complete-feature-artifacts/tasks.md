# Implementation tasks

## Implemented base

- [x] **BASE Deliver living artifacts, simple questions, and focused diagrams**
  - Changes: living user/technical artifacts, refactoring delta, compact workstreams,
    recommendation-first questions, optional code examples, and evidence-triggered diagrams.
  - Done when: all three slices are active, backward-compatible, proportional, and guarded by
    deterministic plugin validation.
  - Verify: focused tests and the plugin self-validator cover the implemented base.
  - Result: living artifacts, question rules, and the diagram lifecycle are implemented.

## Lightweight traceability

- [x] **W4 Trace active scenarios through workstreams and verification** — covers AC-15–AC-18
  - Changes: progressive traceability contract; `start`, `amend`, and `verify` guidance; deterministic
    AC coverage validation; focused docs and plugin guards.
  - Done when: every living active scenario has an ID, every workstream covers existing scenarios,
    uncovered/unknown references fail, and no mandatory machine DAG is introduced.
  - Verify: positive, missing, unknown, range, compatibility, and plugin self-validation tests pass.
  - Result: living packages now validate active scenario IDs, workstream references, compact ranges,
    complete coverage, and focused verification without a mandatory machine graph.
