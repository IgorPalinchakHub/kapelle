---
name: plan
description: >
  Build the human-approved delivery package for a Kapelle feature: functional-test strategy,
  vertical implementation tasks, dependency graph, file ownership, and implementation checkpoints.
---

# Skill: plan

Invoke:

```text
/kapelle:plan <slug>
/kapelle:plan <slug> --revise "<developer feedback>"
/kapelle:plan <slug> --approve
```

## Protocol

1. Require the complete business/design/contracts package and run
   `scripts/review_gate.py check docs/features/<slug> architecture`. Refuse on non-zero exit.
2. Discover scoped project architecture rules and native delivery/test capabilities.
3. Write `test-plan.md` for:
   - base endpoint functional tests;
   - public use-case method functional tests;
   - critical contract tests;
   - later unit-test phase;
   - final functional/integration/static/lint/build verification.
4. Write `tasks.md` and `_kapelle/task-plan.json`.
5. Decompose by low coupling and high cohesion into vertical business outcomes. Do not create
   layer-only tasks such as endpoint/service/repository when one coherent slice can own them.
6. Every task states outcome, ACs, dependencies, contracts, primary aspect, exact file ownership,
   and short Definition of Done. Production tasks do not include writing unit tests.
7. Run `scripts/validate_task_plan.py`. For M/L/XL, dispatch exactly one fresh critic and allow one
   correction pass.
8. Select or record the recommended implementation checkpoint: `task`, `workstream`, or `none`.
9. On `--revise`, update the delivery package and invalidate delivery approval and downstream
   test/implementation evidence.
10. On `--approve`, require current `tasks.md`, `test-plan.md`, a successfully validated task plan,
    and explicit developer confirmation. Never generate missing planning artifacts on an approval
    invocation. Run `scripts/review_gate.py approve docs/features/<slug> delivery-plan
    --confirmation "Developer explicitly approved the delivery plan."`; never construct approval
    JSON manually. Hand off to `/kapelle:base-functional-tests <slug>`.

Do not write production code, base functional tests, or unit tests in this stage. Never hand-edit
manifest, state, status, or approval JSON.

Use the standard backbone handoff block from `references/handoff.md`.
