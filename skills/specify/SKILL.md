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

## Protocol

1. Validate required inputs. If missing, refuse with the named producing stage.
2. Read artifacts directly from disk.
3. Draft goals, non-goals, actors, user stories, measurable acceptance criteria, NFRs, and open
   questions without introducing implementation routing.
4. Use native project capabilities when project-specific behavior is needed: [`../../references/project-capabilities.md`](../../references/project-capabilities.md).
5. Dispatch `kapelle:devils-advocate` to find failure modes and ambiguous behavioral branches.
6. Resolve or explicitly defer every blocking finding.
7. Dispatch `kapelle:critic` against the final draft and architecture map; close contradictions and
   unverifiable acceptance criteria.
8. Write outputs: `docs/features/<slug>/spec.md and .size`.
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
