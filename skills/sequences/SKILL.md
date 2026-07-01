---
name: sequences
model: inherit
effort: medium
description: >
  Write runtime and cross-aspect flows to `sequences.md`. Invoke as /kapelle:sequences <slug> for
  feature-scoped work.
---

# Skill: sequences

Write runtime flows and failure branches to a dedicated artifact.

## Inputs

- `<slug>` for feature-scoped work.
- Reads: `sad.md + surface-plan.json`.
- Shared contract: [`../../references/stage-contract.md`](../../references/stage-contract.md).

## Protocol

1. Validate required inputs. If missing, refuse with the named producing stage.
2. Read artifacts directly from disk.
3. Validate `surface-plan.json` and cover every declared cross-aspect handoff and failure branch.
4. Use native project capabilities when project-specific behavior is needed: [`../../references/project-capabilities.md`](../../references/project-capabilities.md).
5. For any code-writing path, request provider-neutral project guidance: [`../../references/guidance.md`](../../references/guidance.md).
6. Write `sequences.md`. If no runtime flow exists, write an explicit
   `Status: SKIPPED-confirmed` artifact with the evidence.
7. Emit the stage-handoff block per [`../../references/handoff.md`](../../references/handoff.md).

## Output

- `sequences.md`.
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
