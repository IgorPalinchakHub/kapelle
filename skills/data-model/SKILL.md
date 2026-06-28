---
name: data-model
model: inherit
effort: medium
description: >
  Determine data/schema impact and stage migrations or explicit no-schema-change skip. Invoke as /kapelle:data-model <slug> for feature-scoped work.
---

# Skill: data-model

Determine data/schema impact and stage migrations or explicit no-schema-change skip.

## Inputs

- `<slug>` for feature-scoped work.
- Reads: `spec.md + sad.md`.
- Shared contract: [`../../references/stage-contract.md`](../../references/stage-contract.md).
- Agent contract: [`../../references/agent-orchestration.md`](../../references/agent-orchestration.md).

## Protocol

1. Validate required inputs. If missing, refuse with the named producing stage.
2. Read artifacts directly from disk.
3. Dispatch `kapelle:explorer` for existing persistence conventions, migration layout, and closest
   domain/schema precedents.
4. Use native project capabilities when project-specific behavior is needed: [`../../references/project-capabilities.md`](../../references/project-capabilities.md).
5. Before staging migrations, request provider-neutral project guidance: [`../../references/guidance.md`](../../references/guidance.md).
6. Write outputs: `data-model.md and staged migrations or skip note`.
7. Emit the stage-handoff block per [`../../references/handoff.md`](../../references/handoff.md).

## Output

- `data-model.md and staged migrations or skip note`.
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
