---
name: consumer-create
description: Create an idempotent queue consumer through Kapelle.
---

# Skill: consumer-create

> Native project capability for queue-consumer implementation.

## Purpose

Create one message **consumer** for the `queue` entrypoint — an **idempotent**, at-least-once consumer that
acks/offsets correctly and dead-letters poison messages, delegating the work to a handler. First in the worker
dependency order.

## Owner

The `implement` stage's dispatcher invokes it per task. The skill never invokes a stage (one-way control).

## Inputs (gate)

- The task intent + the event contract it consumes + the handler it delegates to.
- Provider-neutral project guidance supplied by the invoking project capability, when available.

## Protocol

1. **Read project guidance.** Use the evidence supplied by the invoking capability; do not select or invoke a provider here.
2. **Inspect existing patterns.** Read how consumers/ack/dead-letter are wired in the repo. Match it.
3. **RED.** Write the failing test first: a re-delivered message is processed **once** (idempotent), a poison message is dead-lettered, the offset/ack is correct. Run it; classify aloud; quote the failing line.
4. **GREEN.** Minimal consumer to pass, applying supplied guidance and preventing duplicate effects.
5. **REFACTOR.** Tidy while staying green.
6. **VALIDATE.** Run the project's applicable quality commands. They must pass.
7. **Report.** Emit the typed status line; mark done only on green.

## Output

- The consumer file(s) + test(s).
- `Status: IMPLEMENTED-and-validated` · `Tests: <n passed>`; or `Status: BLOCKED-guidance` / `Status: STUCK-red`.

## Validation / Definition of Done

- Test failed **first**; duplicate delivery causes no duplicate effect; poison messages are handled; project validation passes.

## Anti-patterns

- **A non-idempotent consumer** (duplicate effects on re-delivery) — the `IDEMPOTENCY-001` violation.
- **Business logic in the consumer** instead of the handler. **Ignoring supplied project guidance.** **Reaching up into a stage.**
