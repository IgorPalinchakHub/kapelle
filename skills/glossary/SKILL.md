---
name: glossary
model: haiku
effort: low
description: >
  Capture or reconcile domain terms in `CONTEXT.md`. Invoke as /kapelle:glossary <slug> for feature-scoped work.
---

# Skill: glossary

Capture or reconcile domain terms in `CONTEXT.md`.

## Inputs

- `<slug>` for feature-scoped work.
- Reads: `term + optional existing CONTEXT.md`.
- Shared contract: [`../../references/stage-contract.md`](../../references/stage-contract.md).

## Protocol

1. Validate required inputs. If missing, refuse with the named producing stage.
2. Read artifacts directly from disk.
3. Perform this stage's work without re-running prior stages.
4. Use native project capabilities when project-specific behavior is needed: [`../../references/project-capabilities.md`](../../references/project-capabilities.md).
5. For any code-writing path, request provider-neutral project guidance: [`../../references/guidance.md`](../../references/guidance.md).
6. Write outputs: `CONTEXT.md`.
7. Emit the stage-handoff block per [`../../references/handoff.md`](../../references/handoff.md).

## Output

- `CONTEXT.md`.
- `Status: DONE | stage: glossary | produced: <paths>`.

## Definition of Done

- Inputs were read from disk.
- Outputs exist and link to upstream artifacts instead of duplicating them.
- Skips are explicit.
- Handoff points to `design`.

## Anti-patterns

- Guessing missing prior-stage output.
- Baking project-specific conventions or provider assumptions into the core skill.
- Running git operations.
