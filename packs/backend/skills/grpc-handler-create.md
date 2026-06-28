---
name: grpc-handler-create
description: Create a gRPC handler through Kapelle.
---

# Skill: grpc-handler-create

> Native project capability for gRPC handler implementation.

## Purpose

Wire the `grpc` entrypoint to the application service — a **thin** handler that delegates to the service and maps
domain exceptions to gRPC status codes. No business logic. Depends on Service (order 3) and the `grpc` Contract.

## Owner

The `implement` stage's dispatcher invokes it per task. The skill never invokes a stage (one-way control).

## Inputs (gate)

- The task intent + the gRPC contract + the service it fronts.
- Provider-neutral project guidance supplied by the invoking project capability, when available.

## Protocol

1. **Read project guidance.** Use the evidence supplied by the invoking capability; do not select or invoke a provider here.
2. **Inspect existing patterns.** Read how gRPC handlers/DI/status-mapping are done in the repo. Match it.
3. **RED.** Write the failing test first: the handler delegates to the service and maps a domain exception to the correct gRPC status; no logic in the handler. Run it; classify aloud; quote the failing line.
4. **GREEN.** Minimal handler, DI wiring, and status mapping to pass, applying supplied guidance.
5. **REFACTOR.** Tidy while staying green.
6. **VALIDATE.** Run the project's applicable quality commands. They must pass.
7. **Report.** Emit the typed status line; mark done only on green.

## Output

- The handler + wiring file(s) + test(s).
- `Status: IMPLEMENTED-and-validated` · `Tests: <n passed>`; or `Status: BLOCKED-guidance` / `Status: STUCK-red`.

## Validation / Definition of Done

- Test failed **first**; handler is thin; domain exceptions map correctly; project validation passes.

## Anti-patterns

- **Business logic in the handler.** **Leaking a domain exception unmapped.**
- **Ignoring supplied project guidance.** **Weakening the test.** **Reaching up into a stage.**
