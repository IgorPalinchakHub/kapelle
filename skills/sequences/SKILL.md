---
name: sequences
description: >
  Enrich `design.md` with runtime and cross-aspect flows; create `sequences.md` only for genuinely
  complex feature flows.
---

# Skill: sequences

Enrich the technical specification with runtime flows and failure branches.

## Inputs

- `<slug>` for feature-scoped work.
- Reads: `design.md + _kapelle/surface-plan.json`.
- Shared contract: [`../../references/stage-contract.md`](../../references/stage-contract.md).

## Protocol

1. Validate required inputs. If missing, refuse with the named producing stage.
2. Read artifacts directly from disk.
3. Validate `_kapelle/surface-plan.json` and cover every declared cross-aspect handoff and failure branch.
4. Use native project capabilities when project-specific behavior is needed: [`../../references/project-capabilities.md`](../../references/project-capabilities.md).
5. For any code-writing path, request provider-neutral project guidance: [`../../references/guidance.md`](../../references/guidance.md).
6. Update the runtime-flow section of `design.md`. Create `sequences.md` only when the flow cannot
   remain readable in the design; record the skip/selection in `_kapelle/state.json`.
7. Refresh `STATUS.md` and emit the chat handoff.

## Output

- Updated `design.md`; optional `sequences.md`.
- `Status: DONE | stage: sequences | produced: <paths>`.

## Definition of Done

- Inputs were read from disk.
- Outputs exist and link to upstream artifacts instead of duplicating them.
- Skips are explicit.
- Handoff points to `data-model`.

## Anti-patterns

- Guessing missing prior-stage output.
- Baking project-specific conventions or provider assumptions into the core skill.
- Running git operations.
