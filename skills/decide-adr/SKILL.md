---
name: decide-adr
description: >
  Write or update an ADR for an architectural decision within a feature.
---

# Skill: decide-adr

Write or update an ADR for an architectural decision.

## Inputs

- `<slug>` for feature-scoped work.
- Reads: `decision context`.
- Utility contract: [`../../references/utility-contract.md`](../../references/utility-contract.md).

## Protocol

1. Require a concrete decision, alternatives, and the affected feature slug. Refuse rather than
   inventing missing decision context.
2. Read artifacts directly from disk.
3. Read the current `design.md` and relevant scoped architecture guidance when they exist.
4. Use native project capabilities when project-specific behavior is needed: [`../../references/project-capabilities.md`](../../references/project-capabilities.md).
5. Write one concise `adr/*.md` containing context, decision, rejected alternatives, consequences,
   and revisit trigger. Update `design.md` only when it would otherwise contradict the decision.
6. Rebuild and validate feature status when feature artifacts changed.
7. Emit the handoff block per [`../../references/handoff.md`](../../references/handoff.md). A
   changed design returns to `/kapelle:start <slug> --approve`; otherwise return to status.

## Output

- `adr/*.md`.
- `Status: DONE | utility: decide-adr | produced: <paths>`.

## Definition of Done

- Inputs were read from disk.
- Outputs exist and link to upstream artifacts instead of duplicating them.
- Skips are explicit.
- Handoff points to current-slice approval or status, never to deprecated `design` or `plan`.

## Anti-patterns

- Guessing missing prior-stage output.
- Baking project-specific conventions or provider assumptions into the core skill.
- Running git operations.
