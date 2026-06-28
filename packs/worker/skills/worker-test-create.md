---
name: worker-test-create
description: Create worker tests through Kapelle.
---

# Skill: worker-test-create

> Native project capability for worker testing.

## Purpose

Author the layered tests for an event-driven worker — handlers tested **without the broker**, consumers via a
message-replay harness, idempotency under duplicate delivery, integration against a real owned dependency where
required. Last in the worker dependency order.

## Owner

The `implement` stage's dispatcher invokes it per task. The skill never invokes a stage (one-way control).

## Inputs (gate)

- The task intent + the code under test + `docs/features/<slug>/test-plan.md` (if present).
- Provider-neutral project guidance supplied by the invoking project capability, when available.

## Protocol

1. **Read project guidance.** Use the evidence supplied by the invoking capability; do not select or invoke a provider here.
2. **Inspect existing patterns.** Read the repo's worker test layout, replay harness, and integration-dependency strategy. Match it.
3. **Author tests.** Handlers in isolation (no broker), consumers via a replay harness, an **idempotency test** (re-deliver → single effect), integration against a real owned dependency where required. Each test asserts an AC.
4. **Run.** Execute the suite; every test passes against the implemented code and each could have failed.
5. **VALIDATE.** Run the project's applicable test and quality commands. They must pass.
6. **Report.** Emit the typed status line; mark done only on green.

## Output

- The test file(s), per the repo's convention.
- `Status: IMPLEMENTED-and-validated` · `Tests: <n passed>`; or `Status: BLOCKED-guidance` / `Status: STUCK-red`.

## Validation / Definition of Done

- Project guidance was applied when supplied; handlers are tested without the broker; replay coverage exists; project validation passes.

## Anti-patterns

- **Testing the handler through the broker** (couples the test to infra). **No idempotency test** for an at-least-once consumer.
- **Asserts-nothing tests.** **Ignoring supplied project guidance.** **Reaching up into a stage.**
