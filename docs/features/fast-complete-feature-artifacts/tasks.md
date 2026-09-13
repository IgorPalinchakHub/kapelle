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

## Compact completeness and understandable decisions

- [x] **W5 Strengthen specifications and dialogue without lengthening simple work** — covers AC-19–AC-25
  - Changes: shared requirement/design/use-case guidance, current/proposal explanations, narrow
    early-test exception, final evidence mapping, stage consumers, docs, and behavior-eval fixtures.
  - Done when: a simple improvement keeps one workstream and the current route, risky concerns are
    explicit, dialogue stands alone, and all nonessential tests remain at final verification.
  - Verify: existing plugin validation and focused skill validation; scenario-based review for simple
    improvement, risky integration, and refactoring. No new test suite for wording alone.
  - Result: proportional completeness, standalone dialogue, and narrow early tests are implemented; plugin and four skill checks pass; independent A/B/C planning drafts cover AC-19–AC-22/AC-24, shared/detail contract review covers AC-23, and evidence mapping plus eval provenance covers AC-25 (see evals/compact-quality.md).
