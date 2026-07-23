---
name: data-model
description: >
  Determine data/schema impact and stage migrations or an explicit no-schema-change result.
---

# Skill: data-model

Determine data/schema impact and stage migrations or explicit no-schema-change skip.

## Inputs

- `<slug>` for feature-scoped work.
- Reads: `spec.md + design.md + _kapelle/surface-plan.json + optional sequences.md`.
- Shared contract: [`../../references/stage-contract.md`](../../references/stage-contract.md).
- Agent contract: [`../../references/agent-orchestration.md`](../../references/agent-orchestration.md).

## Protocol

1. Validate required inputs. If missing, refuse with the named producing stage.
2. Read artifacts directly from disk.
3. Read the selected execution depth. Dispatch `kapelle:explorer` only when persistence is affected
   and the architecture map or scoped rules evidence does not cite a sufficient persistence
   precedent.
4. Use native project capabilities when project-specific behavior is needed: [`../../references/project-capabilities.md`](../../references/project-capabilities.md).
5. Before staging migrations, request provider-neutral project guidance: [`../../references/guidance.md`](../../references/guidance.md).
6. Keep one shared logical model across all producer and consumer aspects. Update the data/schema
   section of `design.md`, stage project migrations when required, and write deterministic evidence
   to `_kapelle/data-model.json`. A no-schema-change result is explicit in both places.
7. Refresh `STATUS.md` and emit the chat handoff.

## Output

- Updated `design.md`, `_kapelle/data-model.json`, and staged migrations when applicable.
- `Status: DONE | stage: data-model | produced: <paths>`.

## Definition of Done

- Inputs were read from disk.
- Outputs exist and link to upstream artifacts instead of duplicating them.
- Skips are explicit.
- Handoff points to `contracts`.

## Anti-patterns

- Guessing missing prior-stage output.
- Baking project-specific conventions or provider assumptions into the core skill.
- Running git operations.
