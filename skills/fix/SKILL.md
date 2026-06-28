---
name: fix
model: opus
effort: high
description: >
  Investigate a bug or review finding and route a minimal fix through tests. Invoke as /kapelle:fix <slug> for feature-scoped work.
---

# Skill: fix

Investigate a bug or review finding and route a minimal fix through tests.

## Inputs

- `<slug>` for feature-scoped work.
- Reads: `bug report or review finding`.
- Shared contract: [`../../references/stage-contract.md`](../../references/stage-contract.md).
- Agent contract: [`../../references/agent-orchestration.md`](../../references/agent-orchestration.md).

## Protocol

1. Validate required inputs. If missing, refuse with the named producing stage.
2. Dispatch `kapelle:explorer` to trace the symptom, affected acceptance criteria, and closest
   working precedent.
3. Reproduce the defect before changing production code.
4. Use native project capabilities when project-specific behavior is needed: [`../../references/project-capabilities.md`](../../references/project-capabilities.md).
5. Request provider-neutral project guidance: [`../../references/guidance.md`](../../references/guidance.md).
6. Execute the same RED → GREEN → REFACTOR → VERIFY → GATE lifecycle as
   [`../../dispatcher/execution-contract.md`](../../dispatcher/execution-contract.md).
7. Write outputs: `_fixes/*.md + code/tests`.
8. Emit the stage-handoff block per [`../../references/handoff.md`](../../references/handoff.md).

## Output

- `_fixes/*.md + code/tests`.
- `Status: DONE | stage: fix | produced: <paths>`.

## Definition of Done

- Inputs were read from disk.
- Outputs exist and link to upstream artifacts instead of duplicating them.
- Skips are explicit.
- Handoff points to `review`.

## Anti-patterns

- Guessing missing prior-stage output.
- Baking project-specific conventions or provider assumptions into the core skill.
- Running git operations.
