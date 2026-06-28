---
name: rest-controller-create
description: Create a REST controller through Kapelle.
---

# Skill: rest-controller-create

> Native project capability for REST controller implementation.

## Purpose

Wire the `rest` entrypoint to the application service — a **thin** controller that validates the request at the
edge, delegates to the service, and maps results/exceptions to HTTP. No business logic. Depends on Service (order 3)
and the `rest` Contract.

## Owner

The `implement` stage's dispatcher invokes it per task. The skill never invokes a stage (one-way control).

## Inputs (gate)

- The task intent + the REST contract + the service it fronts.
- Provider-neutral project guidance supplied by the invoking project capability, when available.

## Protocol

1. **Read project guidance.** Use the evidence supplied by the invoking capability; do not select or invoke a provider here.
2. **Inspect existing patterns.** Read how controllers/routes/DI are wired in the repo. Match it.
3. **RED.** Write the failing test first: the route validates input at the edge, delegates to the service, maps the domain exception to the right HTTP status; no logic in the controller. Run it; classify aloud; quote the failing line.
4. **GREEN.** Minimal controller, route registration, and DI wiring to pass, applying supplied guidance.
5. **REFACTOR.** Tidy while staying green.
6. **VALIDATE.** Run the project's applicable quality commands. They must pass.
7. **Report.** Emit the typed status line; mark done only on green.

## Output

- The controller + route-registration/wiring file(s) + test(s).
- `Status: IMPLEMENTED-and-validated` · `Tests: <n passed>`; or `Status: BLOCKED-guidance` / `Status: STUCK-red`.

## Validation / Definition of Done

- Test failed **first**; the controller is thin; validation happens at the edge; project validation passes.

## Anti-patterns

- **Business logic in the controller.** **Skipping edge validation.**
- **Ignoring supplied project guidance.** **Weakening the test.** **Reaching up into a stage.**
