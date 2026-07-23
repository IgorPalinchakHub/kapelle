# Test plan

## Strategy

Use deterministic unit tests for state derivation and migration, schema/plugin validation for
contract drift, and existing semantic task-plan tests for unchanged decomposition guarantees.

## Required checks

| Coverage | Command | Expected |
|---|---|---|
| Status/recovery/migration | `python3 -m unittest discover -s scripts -p 'test_*.py'` | All tests pass |
| Plugin contracts | `python3 scripts/validate_plugin.py` | No contract drift |
| Task graph | `python3 scripts/validate_task_plan.py ...` | Self-hosted task plan passes |
| Patch hygiene | `git diff --check` | No whitespace errors |

## Acceptance coverage

- AC-01, AC-08, AC-09, AC-12: plugin validator and documentation assertions.
- AC-02–AC-07: feature-state unit tests.
- AC-10: migration dry-run/apply/idempotency fixture.
- AC-11: full test suite and plugin validation.

## Recovery integration scenario

1. Build separate layout-v2 fixtures with checked and unchecked tasks.
2. Remove its `_kapelle/` in a temporary fixture.
3. Run state recovery.
4. Verify checked work becomes `implemented-unverified`.
5. Verify missing evidence is explicit and ship readiness is false.
6. Verify checked work routes to validation-only, while pending work routes to architecture-aware
   decomposition before any code-writing; neither restarts at specification.

## Validation policy

All checks are local and safe. No project runtime, network, git mutation, or external service is
required.
