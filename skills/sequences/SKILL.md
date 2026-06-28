---
name: sequences
model: inherit
effort: medium
description: >
  Write runtime flows and failure branches into the architecture artifact. Invoke as /kapelle:sequences <slug> for feature-scoped work.
---

# Skill: sequences

Write runtime flows and failure branches into the architecture artifact.

## Inputs

- `<slug>` for feature-scoped work.
- Reads: `sad.md`.
- Shared contract: [`../../references/stage-contract.md`](../../references/stage-contract.md).

## Protocol

1. Validate required inputs. If missing, refuse with the named producing stage.
2. Read artifacts directly from disk.
3. Perform this stage's work without re-running prior stages.
4. Use native project capabilities when project-specific behavior is needed: [`../../references/project-capabilities.md`](../../references/project-capabilities.md).
5. For any code-writing path, request provider-neutral project guidance: [`../../references/guidance.md`](../../references/guidance.md).
6. Write outputs: `sad.md flow section`.
7. Emit the stage-handoff block per [`../../references/handoff.md`](../../references/handoff.md).

## Output

- `sad.md flow section`.
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
