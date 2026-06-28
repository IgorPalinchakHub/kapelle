---
name: design
model: opus
effort: high
description: >
  Write `sad.md`, ADRs, target surfaces, and entrypoints. Invoke as /kapelle:design <slug> for feature-scoped work.
---

# Skill: design

Write `sad.md`, ADRs, target surfaces, and entrypoints.

## Inputs

- `<slug>` for feature-scoped work.
- Reads: `spec.md + CONTEXT.md optional + architecture-map.md`.
- Shared contract: [`../../references/stage-contract.md`](../../references/stage-contract.md).
- Agent contract: [`../../references/agent-orchestration.md`](../../references/agent-orchestration.md).

## Protocol

1. Validate required inputs. If missing, refuse with the named producing stage.
2. Read artifacts directly from disk.
3. If `architecture-map.md` is absent or stale, dispatch `kapelle:explorer` for only the feature's
   affected scope and cite the resulting precedents.
4. Use native project capabilities when project-specific behavior is needed: [`../../references/project-capabilities.md`](../../references/project-capabilities.md).
5. Draft `sad.md`, target surfaces, entrypoints, interfaces, consequences, and ADRs.
6. Dispatch `kapelle:critic` in fresh context against `spec.md`, `sad.md`, and ADRs. Resolve or
   explicitly defer every blocking finding.
7. Write outputs: `sad.md and adr/*.md`.
8. Emit the stage-handoff block per [`../../references/handoff.md`](../../references/handoff.md).

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
