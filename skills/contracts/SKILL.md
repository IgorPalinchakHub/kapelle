---
name: contracts
description: >
  Generate interface contracts through native project capabilities for a feature slug.
---

# Skill: contracts

## Inputs

- Gate: `docs/features/<slug>/design.md`.
- `docs/features/<slug>/design.md`, `_kapelle/surface-plan.json`, and optional `sequences.md` with declared interfaces,
  aspect providers/consumers, or entrypoints.
- Native project capabilities and project instructions.

## Protocol

1. Refuse if `design.md` or required interface declarations are missing. Data/schema impact must be
   explicit in `design.md`, including a confirmed no-schema-change result.
2. Validate `_kapelle/surface-plan.json`, then read `stages/contracts/contracts.stage.md` and
   `stages/contracts/drift-gate.md`.
3. Describe the required contract artifact and its design context.
4. Let Claude Code select the applicable native project capability semantically.
5. Ask that capability to obtain project guidance through any available project mechanism.
6. Generate the contract and run its project-defined validation.
7. Run the generic drift check against the shared data model and sequences. Require each shared
   contract to identify its provider aspect and all consumer aspects from `_kapelle/surface-plan.json`.
8. Write human contracts under `docs/features/<slug>/contracts/` and internal validation metadata
   under `_kapelle/validation/contracts.json`.
9. Refresh `STATUS.md` and emit the chat handoff.

## Anti-patterns

- Hardcoding contract kinds, skill names, agent names, providers, or commands in Kapelle core.
- Finalizing a contract that contradicts the shared data model.
