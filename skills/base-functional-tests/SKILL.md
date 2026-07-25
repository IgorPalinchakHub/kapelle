---
name: base-functional-tests
description: >
  Write the small pre-implementation functional safety net for approved endpoints, public
  use-case methods, and critical contracts without writing unit tests or production code.
---

# Skill: base-functional-tests

Invoke:

```text
/kapelle:base-functional-tests <slug> [--validation=ask|allow|skip]
```

## Protocol

1. Read the lane. Standard lane must pass
   `scripts/review_gate.py check docs/features/<slug> delivery-plan`; fast lane must pass the same
   check for `feature-plan`. Refuse before test writes on non-zero exit.
2. Read the current lane. Standard reads `spec.md`, `specs/`, contracts, `test-plan.md`, and the
   task plan. Fast reads `spec.md`, `design.md`, the Test strategy section in `tasks.md`, and the
   task plan; optional detailed artifacts are read when present.
3. Discover native project testing skills and test infrastructure.
4. Dispatch `kapelle:test-author` only for this bounded scope:
   - endpoint input/output/status and principal validation errors;
   - public use-case method happy path, principal business errors, and observable side effects;
   - directly affected critical contracts.
5. Prefer executable tests. When a production symbol does not yet exist, use the project's normal
   supported contract/test seam; do not create fake production implementations to make tests pass.
6. Explicitly exclude unit tests, exhaustive branch coverage, private methods, and implementation
   details.
7. If none of the permitted boundaries exists, require developer confirmation and record
   `SKIPPED-confirmed` with empty scope/test files instead of inventing a test seam.
8. Apply the `ask | allow | skip` validation policy. A developer-confirmed skip is recorded but
   does not become PASS.
9. Write `_kapelle/base-functional-tests.json` matching
   `base-functional-tests.schema.json`. Its `input_fingerprints` cover the approved business,
   design, contract, test-plan, `tasks.md#structural`, and
   `_kapelle/task-plan.json#structural` inputs; task checkbox/status changes do not invalidate this
   evidence.
10. Run `scripts/validate_json.py docs/features/<slug>/_kapelle/base-functional-tests.json
    dispatcher/base-functional-tests.schema.json`. On non-zero exit, refuse completion and correct
    the artifact once; never validate it by visual comparison with the schema.
11. Refresh status and hand off to:

```text
/kapelle:implement <slug> --checkpoint=task
```

The developer may replace `task` with `workstream` or `none`.

Use the standard backbone handoff block from `references/handoff.md`.
