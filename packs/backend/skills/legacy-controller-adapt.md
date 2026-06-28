---
name: legacy-controller-adapt
description: Adapt a legacy controller to a Kapelle-managed service.
---

# Skill: legacy-controller-adapt

> Native project capability for adapting a legacy controller.

## Purpose

Bridge an existing **legacy** controller to the new application service — a strangler-fig boundary that routes
legacy calls into the new service **without adding new logic in the legacy layer**. Depends on Service (order 3).

## Owner

The `implement` stage's dispatcher invokes it per task. The skill never invokes a stage (one-way control).

## Inputs (gate)

- The task intent + the legacy controller to bridge + the service it should delegate to.
- Provider-neutral project guidance supplied by the invoking project capability, when available.

## Protocol

1. **Read project guidance.** Use the evidence supplied by the invoking capability; do not select or invoke a provider here.
2. **Inspect existing patterns.** Read the legacy controller and the strangler boundary already in the repo. Match it; change as little of the legacy layer as possible.
3. **RED.** Write the failing test first: the legacy entrypoint now delegates to the new service and behaviour is preserved; no new business logic added in the legacy layer. Run it; classify aloud; quote the failing line.
4. **GREEN.** Minimal bridge code to pass, applying supplied guidance and preserving the strangler boundary.
5. **REFACTOR.** Tidy while staying green.
6. **VALIDATE.** Run the project's applicable quality commands. They must pass.
7. **Report.** Emit the typed status line; mark done only on green.

## Output

- The bridge/adapter file(s) + test(s).
- `Status: IMPLEMENTED-and-validated` · `Tests: <n passed>`; or `Status: BLOCKED-guidance` / `Status: STUCK-red`.

## Validation / Definition of Done

- Test failed **first**; the legacy layer gains no new business logic; behaviour is preserved; project validation passes.

## Anti-patterns

- **Adding new business logic in the legacy layer** instead of delegating to the service.
- **Ignoring supplied project guidance.** **Weakening the test.** **Reaching up into a stage.**
