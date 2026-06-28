---
name: service-create
description: Create a backend application service through Kapelle.
---

# Skill: service-create

> Native project capability for application-service implementation.

## Purpose

Create one application service that **orchestrates** domain objects and ports to fulfil a use case — owning the
transaction boundary, holding **no business logic itself** (that lives in the domain). It depends on Domain
(order 1) and Adapters (order 2).

## Owner

The `implement` stage's dispatcher invokes it per task. The skill never invokes a stage (one-way control).

## Inputs (gate)

- The task intent from `tasks.json`.
- `docs/features/<slug>/data-model.md` + the relevant `sad.md` §6 sequence for the use case.
- Provider-neutral project guidance supplied by the invoking project capability, when available.

## Protocol

1. **Read project guidance.** Use the evidence supplied by the invoking capability; do not select or invoke a provider here.
2. **Inspect existing patterns.** Read where services live, how transactions are demarcated, how ports are injected. Match it.
3. **RED.** Write the failing test first: the service orchestrates the use case, commits/rolls back the transaction at its boundary, and pushes business decisions down to the domain. Run it; classify aloud; quote the failing line.
4. **GREEN.** Minimal service code to pass, applying supplied guidance and keeping invariants in the domain.
5. **REFACTOR.** Tidy while staying green.
6. **VALIDATE.** Run the project's applicable lint, typecheck, and tests. They must pass.
7. **Report.** Emit the typed status line; mark done only on green.

## Output

- The service file(s) + test(s), per the repo's convention.
- `Status: IMPLEMENTED-and-validated` · `Tests: <n passed>`; or `Status: BLOCKED-guidance` / `Status: STUCK-red`.

## Validation / Definition of Done

- The test failed **first**; the transaction boundary is owned by the service; project validation passes.

## Anti-patterns

- **Business logic in the service** instead of the domain.
- **Ignoring supplied project guidance.** **Weakening the test.** **Reaching up into a stage.**
