---
name: backend-test-create
description: Create backend tests through Kapelle.
---

# Skill: backend-test-create

> Native project capability for backend testing.

## Purpose

Author the layered tests for a backend feature — domain tested **without the framework**, adapters/services at
their boundaries, integration where a real owned dependency is involved. The last entry in the dependency order.

## Owner

The `implement` stage's dispatcher invokes it per task. The skill never invokes a stage (one-way control).

## Inputs (gate)

- The task intent + the code under test + `docs/features/<slug>/test-plan.md` (the AC→test map, if present).
- Provider-neutral project guidance supplied by the invoking project capability, when available.

## Protocol

1. **Read project guidance.** Use the evidence supplied by the invoking capability; do not select or invoke a provider here.
2. **Inspect existing patterns.** Read the repo's test layout, fixtures, and integration-dependency strategy. Match it.
3. **Author tests.** Write tests at the right level per the test plan: the domain in isolation (no framework), adapters/services at their seams, integration against a real owned dependency where required. Each test asserts an AC.
4. **Run.** Execute the suite; every test must pass against the implemented code (and each must have been able to fail — no asserts-nothing tests).
5. **VALIDATE.** Run the project's applicable lint, typecheck, and test suite. They must pass.
6. **Report.** Emit the typed status line; mark done only on green.

## Output

- The test file(s), placed per the repo's convention.
- `Status: IMPLEMENTED-and-validated` · `Tests: <n passed>`; or `Status: BLOCKED-guidance` / `Status: STUCK-red`.

## Validation / Definition of Done

- Project guidance was applied when supplied; the domain is tested without the framework; each test maps to an AC and project validation passes.

## Anti-patterns

- **Testing the domain through the framework** (couples the test to wiring).
- **Asserts-nothing tests** that pass vacuously. **Ignoring supplied project guidance.** **Reaching up into a stage.**
