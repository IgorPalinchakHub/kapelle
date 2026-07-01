---
name: contracts
model: inherit
effort: medium
description: >
  Generate interface contracts through native project capabilities. Invoke as /kapelle:contracts <slug>.
---

# Skill: contracts

## Inputs

- Gate: `docs/features/<slug>/data-model.md`.
- `docs/features/<slug>/sad.md`, `surface-plan.json`, and `sequences.md` with declared interfaces,
  aspect providers/consumers, or entrypoints.
- Native project capabilities and project instructions.

## Protocol

1. Refuse if `data-model.md` or interface declarations are missing.
2. Validate `surface-plan.json`, then read `stages/contracts/contracts.stage.md` and
   `stages/contracts/drift-gate.md`.
3. Describe the required contract artifact and its design context.
4. Let Claude Code select the applicable native project capability semantically.
5. Ask that capability to obtain project guidance through any available project mechanism.
6. Generate the contract and run its project-defined validation.
7. Run the generic drift check against the shared data model and sequences. Require each shared
   contract to identify its provider aspect and all consumer aspects from `surface-plan.json`.
8. Write artifacts under `docs/features/<slug>/contracts/`.
9. Emit the stage handoff.

## Anti-patterns

- Hardcoding contract kinds, skill names, agent names, providers, or commands in Kapelle core.
- Finalizing a contract that contradicts the shared data model.
