---
name: roadmap
description: >
  Maintain feature roadmap state across Now, Next, Later, and Shipped.
---

# Skill: roadmap

Maintain roadmap state across Now/Next/Later/Shipped.

## Inputs

- `<slug>` for feature-scoped work.
- Reads: `user request or feature artifacts`.
- Utility contract: [`../../references/utility-contract.md`](../../references/utility-contract.md).
- This is a project utility, not a feature backbone stage.

## Protocol

1. Require an explicit roadmap change or a feature whose current placement must be reconciled.
2. Read `docs/roadmap.md` and only the named feature artifacts.
3. Move or add the minimum roadmap entry requested by the developer. Do not infer commitments,
   dates, priority, or shipped status.
4. Write `docs/roadmap.md` and summarize the exact placement change.
5. Do not modify feature workflow state and do not emit a feature next-stage command.

## Output

- `docs/roadmap.md`.
- `Status: DONE | utility: roadmap | produced: docs/roadmap.md`.

## Definition of Done

- Inputs were read from disk.
- Outputs exist and link to upstream artifacts instead of duplicating them.
- Skips are explicit.
- No hidden feature-stage handoff is introduced.

## Anti-patterns

- Guessing missing prior-stage output.
- Baking project-specific conventions or provider assumptions into the core skill.
- Running git operations.
