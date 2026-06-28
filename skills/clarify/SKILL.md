---
name: clarify
model: opus
effort: high
description: >
  Tighten `spec.md` by finding ambiguities, gaps, and unresolved decisions. Invoke as /kapelle:clarify <slug> for feature-scoped work.
---

# Skill: clarify

Tighten `spec.md` by finding ambiguities, gaps, and unresolved decisions.

## Inputs

- `<slug>` for feature-scoped work.
- Reads: `docs/features/<slug>/spec.md`.
- Shared contract: [`../../references/stage-contract.md`](../../references/stage-contract.md).
- Agent contract: [`../../references/agent-orchestration.md`](../../references/agent-orchestration.md).

## Protocol

1. Validate required inputs. If missing, refuse with the named producing stage.
2. Read artifacts directly from disk.
3. Run an inline ambiguity sweep over vague terms, missing actors, unmeasured NFRs, conflicting
   requirements, and underspecified acceptance criteria.
4. Dispatch `kapelle:devils-advocate` in fresh context with only the slug and artifact paths.
5. Merge and deduplicate findings. Resolve each in the spec or defer it with owner and reason.
6. Write outputs: `updated spec.md`.
7. Emit the stage-handoff block per [`../../references/handoff.md`](../../references/handoff.md).

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
