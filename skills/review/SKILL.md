---
name: review
model: opus
effort: high
agents: [reviewer]
description: >
  Run clean-context review against spec, architecture, contracts, tests, and available project guidance. Invoke as /kapelle:review <slug> for feature-scoped work.
---

# Skill: review

Run clean-context review against spec, architecture, contracts, tests, and available project guidance.

## Inputs

- `<slug>` for feature-scoped work.
- Reads: `implemented diff + feature artifacts`.
- Shared contract: [`../_shared/stage-contract.md`](../_shared/stage-contract.md).

## Protocol

1. Validate required inputs. If missing, refuse with the named producing stage.
2. Read artifacts directly from disk.
3. Perform this stage's work without re-running prior stages.
4. Use native project capabilities when project-specific behavior is needed: [`../_shared/project-capabilities.md`](../_shared/project-capabilities.md).
5. For any code-writing path, request provider-neutral project guidance: [`../_shared/guidance.md`](../_shared/guidance.md).
6. Write outputs: `_review/review-<date>.md`.
7. Emit the stage-handoff block per [`../_shared/handoff.md`](../_shared/handoff.md).

## Output

- `_review/review-<date>.md`.
- `Status: DONE | stage: review | produced: <paths>`.

## Definition of Done

- Inputs were read from disk.
- Outputs exist and link to upstream artifacts instead of duplicating them.
- Skips are explicit.
- Handoff points to `ship`.

## Anti-patterns

- Guessing missing prior-stage output.
- Baking project-specific conventions or provider assumptions into the core skill.
- Running git operations.
