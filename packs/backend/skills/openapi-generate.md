---
name: openapi-generate
description: Generate an OpenAPI contract through Kapelle.
---

# Skill: openapi-generate

> Native project capability for OpenAPI contract generation.

## Purpose

Generate the **REST** interface contract (OpenAPI) for the `rest` entrypoint **from the shared data model** —
the capability selected natively for compatible REST contract work. The contract is checked against the
data model before finalization.

## Owner

The `contracts` stage invokes it (one generator per entrypoint kind, injected — the stage never branches on kind). The skill never invokes a stage.

## Inputs (gate)

- The declared `rest` entrypoint + `docs/features/<slug>/data-model.md` (the shared model).
- Provider-neutral project guidance supplied by the invoking project capability, when available.

## Protocol

1. **Read project guidance.** Use the evidence supplied by the invoking capability; do not select or invoke a provider here.
2. **Inspect existing patterns.** Read the repo's existing OpenAPI docs/conventions (envelope, error shape, pagination). Match them.
3. **Generate.** Produce the OpenAPI document, deriving paths and schemas from the data model and applying supplied guidance.
4. **GATE (drift).** Run the `openapi-drift` gate (T16): the contract must not contradict a model field type or omit a model-required field (optional extensions allowed). On drift → block, name the invariant.
5. **Report.** Emit the typed status line; finalize only on a clean drift gate.

## Output

- `docs/features/<slug>/contracts/openapi.yaml` (the candidate, finalized only after the drift gate).
- `Status: CONTRACT-GENERATED` · `entrypoint: rest` · `drift: clean`; or `Status: CONTRACT-DRIFT-BLOCKED`.

## Validation / Definition of Done

- Project guidance was applied when supplied; the contract is derived from the shared model; project validation is clean.

## Anti-patterns

- **Hand-authoring the contract** independent of the data model (it must be *derived*, gated by drift).
- **Branching on kind inside the stage** — this skill *is* the per-kind generator; the stage stays generic.
- **Ignoring supplied project guidance.** **Reaching up into a stage.**
