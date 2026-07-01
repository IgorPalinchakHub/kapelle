---
name: design
model: opus
effort: high
description: >
  Write `sad.md`, `surface-plan.json`, and ADRs using scoped project architecture rules. Invoke as
  /kapelle:design <slug> for feature-scoped work.
---

# Skill: design

Write `sad.md`, `surface-plan.json`, and ADRs.

## Inputs

- `<slug>` for feature-scoped work.
- Reads: `spec.md + CONTEXT.md optional + architecture-map.md`.
- Shared contract: [`../../references/stage-contract.md`](../../references/stage-contract.md).
- Agent contract: [`../../references/agent-orchestration.md`](../../references/agent-orchestration.md).
- Execution depth: [`../../references/execution-depth.md`](../../references/execution-depth.md).
- Architecture guidance:
  [`../../references/architecture-guidance.md`](../../references/architecture-guidance.md).

## Protocol

1. Validate required inputs. If missing, refuse with the named producing stage.
2. Read artifacts directly from disk.
3. Select and record execution depth. Use the architecture map when present; dispatch
   `kapelle:explorer` only for missing affected-scope precedents.
4. Identify the tentative aspects, modules, entrypoints, and paths. Semantically discover and
   dispatch the project's architecture-rules subagent for exactly that scope. Validate its output
   against `dispatcher/architecture-guidance.schema.json`; refuse on a missing capability or
   blocking gaps.
5. Let the selected project subagent discover any narrower project skills/subagents needed to
   evaluate the design. Record selections as evidence, not routing configuration.
6. Draft `sad.md` from the specification, cited precedents, and scoped architecture rules.
7. Write `surface-plan.json` with aspect dependencies, shared contracts, and cross-aspect
   integration checks. Validate it against `dispatcher/surface-plan.schema.json`. A single-aspect
   feature still has one small aspect entry.
8. At `standard` or `full` depth, or for a risk trigger, dispatch `kapelle:critic` in fresh context
   against `spec.md`, `sad.md`, `surface-plan.json`, rules evidence, and ADRs. At `lean`, perform a
   focused inline consistency check. Resolve or explicitly defer every blocking finding.
9. Write outputs: `sad.md`, `surface-plan.json`, `adr/*.md`, and
   `_audit/architecture-guidance/design.json`.
10. Emit the stage-handoff block per [`../../references/handoff.md`](../../references/handoff.md).

## Output

- `sad.md`, `surface-plan.json`, `adr/*.md`, and architecture-guidance evidence.
- `Status: DONE | stage: design | produced: <paths>`.

## Definition of Done

- Inputs were read from disk.
- Outputs exist and link to upstream artifacts instead of duplicating them.
- Every aspect and cross-aspect dependency is explicit and validated.
- Design decisions cite scoped project architecture rules.
- Skips are explicit.
- Handoff points to `sequences`.

## Anti-patterns

- Guessing missing prior-stage output.
- Baking project-specific conventions or provider assumptions into the core skill.
- Running git operations.
