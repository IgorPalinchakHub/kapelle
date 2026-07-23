---
name: ship
description: >
  Verify feature readiness and write ship notes without running git actions.
---

# Skill: ship

Verify readiness and write ship notes; do not run git actions.

## Inputs

- `<slug>` for feature-scoped work.
- Reads: current `PASS` documentation convergence, current `PASS` feature review, state, and
  validation evidence.
- Shared contract: [`../../references/stage-contract.md`](../../references/stage-contract.md).
- Validation execution:
  [`../../references/validation-execution.md`](../../references/validation-execution.md).

## Protocol

1. Validate required inputs. If missing, refuse with the named producing stage.
2. Read artifacts directly from disk.
3. Refuse with `Status: REFUSED-validation-incomplete` if any task is `validation-deferred` or any
   required test, static-analysis, lint, build, other validation command, or integration check is
   missing, failed, skipped, or cancelled. Development policy cannot override this final gate.
4. Refuse when documentation convergence or feature review fingerprints do not match the current
   proposal, spec, design, contracts, tasks, and test plan.
5. Perform this stage's work without re-running prior stages.
6. Use native project capabilities when project-specific behavior is needed:
   [`../../references/project-capabilities.md`](../../references/project-capabilities.md).
7. Set ship readiness in `_kapelle/state.json`, refresh `STATUS.md`, and write an optional human
   `release.md` only when release notes are useful. Do not create a competing `ship.md`.
8. Emit the chat handoff per [`../../references/handoff.md`](../../references/handoff.md).

## Output

- Updated `_kapelle/state.json` and `STATUS.md`; optional `release.md`.
- `Status: DONE | stage: ship | produced: <paths>`.

## Definition of Done

- Inputs were read from disk.
- Outputs exist and link to upstream artifacts instead of duplicating them.
- Skips are explicit.
- Handoff points to `done`.

## Anti-patterns

- Guessing missing prior-stage output.
- Baking project-specific conventions or provider assumptions into the core skill.
- Running git operations.
