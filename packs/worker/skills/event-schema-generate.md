---
name: event-schema-generate
description: Generate an event schema through Kapelle.
---

# Skill: event-schema-generate

> Native project capability for event-schema generation.

## Purpose

Generate an event interface contract from the shared data model and validate it against the project's
compatibility expectations.

## Owner

The native project capability may select it for a compatible contract task. The skill never invokes a stage.

## Inputs (gate)

- The declared `event` entrypoint + `docs/features/<slug>/data-model.md`.
- Provider-neutral project guidance supplied by the invoking project capability, when available.

## Protocol

1. **Read project guidance.** Use the evidence supplied by the invoking capability; do not select or invoke a provider here.
2. **Inspect existing patterns.** Read the repo's existing event schemas / envelope / versioning convention. Match them.
3. **Generate.** Produce the event schema, deriving fields from the data model and applying supplied guidance.
4. **GATE (drift).** Run the `event-drift` gate (T16): no contradiction of a model field type, no omission of a model-required field (optional extensions allowed). On drift → block, name the invariant.
5. **Report.** Emit the typed status line; finalize only on a clean drift gate.

## Output

- `docs/features/<slug>/contracts/<event>.schema.json` (candidate, finalized after the drift gate).
- `Status: CONTRACT-GENERATED` · `entrypoint: event` · `drift: clean`; or `Status: CONTRACT-DRIFT-BLOCKED`.

## Validation / Definition of Done

- Project guidance was applied when supplied; the schema is derived from the shared model; project validation is clean.

## Anti-patterns

- **Hand-authoring the schema** independent of the model. **Branching on kind in the stage.**
- **Breaking backward compatibility** without a version bump. **Ignoring supplied project guidance.**
