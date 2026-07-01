---
name: fix
model: opus
effort: high
description: >
  Backward-compatible bugfix shorthand for the existing-feature change lifecycle. Capture baseline,
  reproduce the defect, assess impact, and run the minimal approved route. Invoke as
  /kapelle:fix <slug> "<bug description>".
---

# Skill: fix

Run the universal change lifecycle with `mode: bugfix`.

## Inputs

- `<slug>` for feature-scoped work.
- Reads: bug report or review finding plus existing feature artifacts.
- Change contract: [`../../references/change-lifecycle.md`](../../references/change-lifecycle.md).
- Shared contract: [`../../references/stage-contract.md`](../../references/stage-contract.md).
- Agent contract: [`../../references/agent-orchestration.md`](../../references/agent-orchestration.md).

## Protocol

1. Require a bug description or review finding.
2. Apply the `change` skill protocol with forced `mode: bugfix`.
3. Reproduce the defect and link it to an existing acceptance criterion.
4. If expected behavior is missing or wrong in the requirement, stop and request reclassification
   to `enhancement`.
5. Execute only the approved bugfix route through the adaptive implementation contract.
6. Emit the stage-handoff block per [`../../references/handoff.md`](../../references/handoff.md).

## Output

- `changes/<change-id>/change.json`, baseline, progress, code and tests.
- `Status: DONE | stage: fix | produced: <paths>`.

## Definition of Done

- Inputs were read from disk.
- Outputs exist and link to upstream artifacts instead of duplicating them.
- Skips are explicit.
- Handoff points to `review`.
- `/kapelle:fix` and `/kapelle:change --mode=bugfix` produce the same artifact model.

## Anti-patterns

- Guessing missing prior-stage output.
- Baking project-specific conventions or provider assumptions into the core skill.
- Running git operations.
