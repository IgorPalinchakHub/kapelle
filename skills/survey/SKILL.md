---
name: survey
model: inherit
effort: medium
description: >
  Map the repository once and write `docs/architecture-map.md`. Invoke as /kapelle:survey <slug> for feature-scoped work.
---

# Skill: survey

Map the repository once and write `docs/architecture-map.md`.

## Inputs

- `<slug>` for feature-scoped work.
- Reads: `repo`.
- Shared contract: [`../../references/stage-contract.md`](../../references/stage-contract.md).
- Agent contract: [`../../references/agent-orchestration.md`](../../references/agent-orchestration.md).
- Architecture-guidance contract:
  [`../../references/architecture-guidance.md`](../../references/architecture-guidance.md).

## Protocol

1. Validate required inputs. If missing, refuse with the named producing stage.
2. Dispatch `kapelle:explorer` with the repository root and request stack, module boundaries,
   wiring, data stores, test commands, project skills, project subagents, rules, and representative
   precedents.
3. Merge only cited findings into the architecture map; record unknowns instead of guessing.
4. Semantically discover the project's architecture-rules subagent. Record its native name and
   description evidence, or record a readiness gap; do not create a Kapelle alias or mapping.
5. Use native project capabilities when project-specific behavior is needed:
   [`../../references/project-capabilities.md`](../../references/project-capabilities.md).
6. Write outputs: `docs/architecture-map.md`.
7. Emit the stage-handoff block per [`../../references/handoff.md`](../../references/handoff.md).

## Output

- `docs/architecture-map.md`.
- `Status: DONE | stage: survey | produced: <paths>`.

## Definition of Done

- Inputs were read from disk.
- Outputs exist and link to upstream artifacts instead of duplicating them.
- The architecture map records project skill/subagent discovery and architecture-rules capability
  readiness.
- Skips are explicit.
- Handoff points to `specify`.

## Anti-patterns

- Guessing missing prior-stage output.
- Baking project-specific conventions or provider assumptions into the core skill.
- Running git operations.
