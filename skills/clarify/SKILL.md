---
name: clarify
model: opus
effort: high
agents: [devils-advocate]
description: >
  Tighten `spec.md` by finding ambiguities, gaps, and unresolved decisions. Invoke as /kapelle:clarify <slug> for feature-scoped work.
---

# Skill: clarify

Tighten `spec.md` by finding ambiguities, gaps, and unresolved decisions.

## Inputs

- `<slug>` for feature-scoped work.
- Reads: `docs/features/<slug>/spec.md`.
- Shared contract: [`../_shared/stage-contract.md`](../_shared/stage-contract.md).

## Protocol

1. Validate required inputs. If missing, refuse with the named producing stage.
2. Read artifacts directly from disk.
3. Perform this stage's work without re-running prior stages.
4. Use native project capabilities when project-specific behavior is needed: [`../_shared/project-capabilities.md`](../_shared/project-capabilities.md).
5. For any code-writing path, request provider-neutral project guidance: [`../_shared/guidance.md`](../_shared/guidance.md).
6. Write outputs: `updated spec.md`.
7. Emit the stage-handoff block per [`../_shared/handoff.md`](../_shared/handoff.md).

## Output

- `updated spec.md`.
- `Status: DONE | stage: clarify | produced: <paths>`.

## Definition of Done

- Inputs were read from disk.
- Outputs exist and link to upstream artifacts instead of duplicating them.
- Skips are explicit.
- Handoff points to `design`.

## Anti-patterns

- Guessing missing prior-stage output.
- Baking project-specific conventions or provider assumptions into the core skill.
- Running git operations.
