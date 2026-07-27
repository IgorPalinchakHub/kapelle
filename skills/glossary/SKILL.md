---
name: glossary
description: >
  Capture or reconcile feature domain terms in `CONTEXT.md`.
---

# Skill: glossary

Capture or reconcile domain terms in `CONTEXT.md`.

## Inputs

- `<slug>` for feature-scoped work.
- Reads: `term + optional existing CONTEXT.md`.
- Utility contract: [`../../references/utility-contract.md`](../../references/utility-contract.md).

## Protocol

1. Require a feature slug and at least one ambiguous or conflicting domain term.
2. Read artifacts directly from disk.
3. Reconcile the term against `spec.md`, `design.md`, current code, and existing `CONTEXT.md`
   without re-running the backbone.
4. Use native project capabilities when project-specific behavior is needed: [`../../references/project-capabilities.md`](../../references/project-capabilities.md).
5. Write only terms that materially improve future feature review. Keep `CONTEXT.md` concise and
   update `spec.md` or `design.md` when they use a conflicting meaning.
6. Rebuild and validate feature status when feature artifacts changed.
7. Emit the handoff block per [`../../references/handoff.md`](../../references/handoff.md). Changed
   scope or design returns to `/kapelle:start <slug> --approve`; otherwise return to status.

## Output

- `CONTEXT.md`.
- `Status: DONE | utility: glossary | produced: <paths>`.

## Definition of Done

- Inputs were read from disk.
- Outputs exist and link to upstream artifacts instead of duplicating them.
- Skips are explicit.
- Handoff points to current-slice approval or status, never to deprecated `design`.

## Anti-patterns

- Guessing missing prior-stage output.
- Baking project-specific conventions or provider assumptions into the core skill.
- Running git operations.
