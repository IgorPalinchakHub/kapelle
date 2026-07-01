---
name: specify
model: opus
effort: high
description: >
  Turn a raw feature idea into `spec.md` with acceptance criteria. Invoke as /kapelle:specify <slug> for feature-scoped work.
---

# Skill: specify

Turn a raw feature idea into `spec.md` with acceptance criteria.

## Inputs

- `<slug>` for feature-scoped work.
- Reads: `idea + optional architecture-map.md`.
- Shared contract: [`../../references/stage-contract.md`](../../references/stage-contract.md).
- Agent contract: [`../../references/agent-orchestration.md`](../../references/agent-orchestration.md).
- Execution depth: [`../../references/execution-depth.md`](../../references/execution-depth.md).

## Protocol

1. Validate required inputs. If missing, refuse with the named producing stage.
2. Read artifacts directly from disk.
3. Draft goals, non-goals, actors, user stories, measurable acceptance criteria, NFRs, and open
   questions without introducing implementation routing.
4. Use native project capabilities when project-specific behavior is needed: [`../../references/project-capabilities.md`](../../references/project-capabilities.md).
5. Classify size and execution depth. At `lean`, perform one inline acceptance-criteria and failure
   branch check. At `standard`/`full`, dispatch `kapelle:devils-advocate`.
6. Resolve or explicitly defer every blocking finding.
7. Dispatch `kapelle:critic` only at `full` depth or when requirements conflict with repository
   constraints. Otherwise leave the independent ambiguity delta pass to `clarify`.
8. Write outputs: `docs/features/<slug>/spec.md and .size`, including the execution-depth reason.
9. Emit the stage-handoff block per [`../../references/handoff.md`](../../references/handoff.md).

## Output

- `docs/features/<slug>/spec.md and .size`.
- `Status: DONE | stage: specify | produced: <paths>`.

## Definition of Done

- Inputs were read from disk.
- Outputs exist and link to upstream artifacts instead of duplicating them.
- Skips are explicit.
- Handoff points to `clarify`.

## Anti-patterns

- Guessing missing prior-stage output.
- Baking project-specific conventions or provider assumptions into the core skill.
- Running git operations.
