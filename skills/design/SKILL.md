---
name: design
model: opus
effort: high
agents: [explorer, critic]
description: >
  Write `sad.md`, ADRs, target surfaces, and entrypoints. Invoke as /kapelle:design <slug> for feature-scoped work.
---

# Skill: design

Write `sad.md`, ADRs, target surfaces, and entrypoints.

## Inputs

- `<slug>` for feature-scoped work.
- Reads: `spec.md + CONTEXT.md optional + architecture-map.md`.
- Shared contract: [`../_shared/stage-contract.md`](../_shared/stage-contract.md).

## Protocol

1. Validate required inputs. If missing, refuse with the named producing stage.
2. Read artifacts directly from disk.
3. Perform this stage's work without re-running prior stages.
4. Use native project capabilities when project-specific behavior is needed: [`../_shared/project-capabilities.md`](../_shared/project-capabilities.md).
5. For any code-writing path, request provider-neutral project guidance: [`../_shared/guidance.md`](../_shared/guidance.md).
6. Write outputs: `sad.md and adr/*.md`.
7. Emit the stage-handoff block per [`../_shared/handoff.md`](../_shared/handoff.md).

## Output

- `sad.md and adr/*.md`.
- `Status: DONE | stage: design | produced: <paths>`.

## Definition of Done

- Inputs were read from disk.
- Outputs exist and link to upstream artifacts instead of duplicating them.
- Skips are explicit.
- Handoff points to `sequences`.

## Anti-patterns

- Guessing missing prior-stage output.
- Baking project-specific conventions or provider assumptions into the core skill.
- Running git operations.
