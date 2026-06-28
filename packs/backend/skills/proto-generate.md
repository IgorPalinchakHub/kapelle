---
name: proto-generate
description: Generate a protobuf contract through Kapelle.
---

# Skill: proto-generate

> Native project capability for protobuf contract generation.

## Purpose

Generate the **gRPC** interface contract (protobuf) for the `grpc` entrypoint **from the shared data model** —
the capability selected natively for compatible gRPC contract work.

## Owner

The `contracts` stage invokes it (injected per entrypoint kind; the stage never branches on kind). The skill never invokes a stage.

## Inputs (gate)

- The declared `grpc` entrypoint + `docs/features/<slug>/data-model.md`.
- Provider-neutral project guidance supplied by the invoking project capability, when available.

## Protocol

1. **Read project guidance.** Use the evidence supplied by the invoking capability; do not select or invoke a provider here.
2. **Inspect existing patterns.** Read the repo's existing `.proto` conventions (package layout, error model, naming). Match them.
3. **Generate.** Produce the `.proto`, mapping the data model to messages and services and applying supplied guidance.
4. **GATE (drift).** Run the `proto-drift` gate (T16): no contradiction of a model field type, no omission of a model-required field (optional extensions allowed). On drift → block, name the invariant.
5. **Report.** Emit the typed status line; finalize only on a clean drift gate.

## Output

- `docs/features/<slug>/contracts/<service>.proto` (candidate, finalized after the drift gate).
- `Status: CONTRACT-GENERATED` · `entrypoint: grpc` · `drift: clean`; or `Status: CONTRACT-DRIFT-BLOCKED`.

## Validation / Definition of Done

- Project guidance was applied when supplied; the contract is derived from the shared model; project validation is clean.

## Anti-patterns

- **Hand-authoring the proto** independent of the model. **Branching on kind in the stage.**
- **Ignoring supplied project guidance.** **Reaching up into a stage.**
