---
name: adapter-create
description: Create a backend adapter through Kapelle.
---

# Skill: adapter-create

> Native project capability for backend-adapter implementation.

## Purpose

Create one adapter (a port implementation: repository, gateway, external-SDK client) that translates between
the domain and an external dependency — **keeping SDK types and SDK errors out of the domain**. It depends on
the Domain layer (order 1) and is consumed by Services (order 3).

## Owner

The `implement` stage's dispatcher invokes it per task. The skill never invokes a stage (one-way control).

## Inputs (gate)

- The task object from `tasks.json` (id, intent, acceptance criteria, and file hints).
- `docs/features/<slug>/data-model.md` (the port's domain types) + the relevant `contracts/` if the adapter fronts one.
- Provider-neutral project guidance supplied by the invoking project capability, when available.

## Protocol

1. **Read project guidance.** Use the evidence supplied by the invoking capability; do not select or invoke a provider here.
2. **Inspect existing patterns.** Read where the repo keeps adapters/ports (placement, naming, the port interface the domain declares). Match it; do not reinvent the port.
3. **RED.** Write the failing test first encoding the AC — the adapter satisfies its port, and an SDK error is translated to a domain exception (never leaked). Run it; classify the first run aloud; quote the failing line.
4. **GREEN.** Write the minimal adapter to pass, applying supplied guidance and translating SDK errors at the boundary.
5. **REFACTOR.** Tidy while staying green.
6. **VALIDATE.** Run the project's applicable lint, typecheck, and tests. They must pass.
7. **Report.** Emit the typed status line. Mark the task done only on a passing gate.

## Output

- The adapter file(s) + their test(s), placed per the repo's convention.
- A typed status line: `Status: IMPLEMENTED-and-validated` · `Tests: <n passed>`; or `Status: BLOCKED-guidance` / `Status: STUCK-red`.

## Validation / Definition of Done

- The test was written and failed **first**.
- No SDK error or SDK type leaks into the domain.
- Project validation passes; the status line is emitted.

## Anti-patterns

- **Leaking an SDK exception/type into the domain** — the precise violation `ADAPTER-ERR-001` exists to prevent.
- **Ignoring supplied project guidance.** **Weakening the test to force green** — escalate instead.
- **Reaching up into a stage** if more work appears — stop and name the next stage (one-way control).
