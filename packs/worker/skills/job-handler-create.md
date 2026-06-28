---
name: job-handler-create
description: Create an asynchronous job handler through Kapelle.
---

# Skill: job-handler-create

> Native project capability for asynchronous job-handler implementation.

## Purpose

Create one **handler** that orchestrates the domain + ports to process a message — owning the transactional
boundary (transactional outbox where effects must be exactly-once), holding **no business logic itself**. Depends
on the Consumer (order 1) and the domain.

## Owner

The `implement` stage's dispatcher invokes it per task. The skill never invokes a stage (one-way control).

## Inputs (gate)

- The task intent + `docs/features/<slug>/data-model.md` + the relevant sequence.
- Provider-neutral project guidance supplied by the invoking project capability, when available.

## Protocol

1. **Read project guidance.** Use the evidence supplied by the invoking capability; do not select or invoke a provider here.
2. **Inspect existing patterns.** Read how handlers/outbox/retry are done in the repo. Match it.
3. **RED.** Write the failing test first: the handler orchestrates the use case within a transaction, emits effects via the outbox, retries with backoff, and pushes decisions to the domain. Run it; classify aloud; quote the failing line.
4. **GREEN.** Minimal handler to pass, applying supplied guidance and keeping business decisions in the domain.
5. **REFACTOR.** Tidy while staying green.
6. **VALIDATE.** Run the project's applicable quality commands. They must pass.
7. **Report.** Emit the typed status line; mark done only on green.

## Output

- The handler file(s) + test(s).
- `Status: IMPLEMENTED-and-validated` · `Tests: <n passed>`; or `Status: BLOCKED-guidance` / `Status: STUCK-red`.

## Validation / Definition of Done

- Test failed **first**; transaction/outbox boundaries are correct; project validation passes.

## Anti-patterns

- **Business logic in the handler** instead of the domain. **External effects outside the outbox** (lost on rollback).
- **Ignoring supplied project guidance.** **Weakening the test.** **Reaching up into a stage.**
