---
name: domain-model-create
description: Create a framework-independent backend domain model through Kapelle.
---

# Skill: domain-model-create

> Native project capability for domain-model implementation.

## Purpose

Create one domain model (entity / aggregate / value object) as **pure domain code** — no framework or
SDK types — for a single `Domain`-tagged task. It is the first layer in the dependency order
(Domain → Adapter → Service → Wiring), so it has no dependencies on other layers.

## Owner

The `implement` stage's dispatcher invokes it per task. The skill never invokes a stage (one-way control, tenet #7).

## Inputs (gate)

- The task object from `tasks.json` (id, intent, acceptance criteria, and file hints).
- `docs/features/<slug>/data-model.md` — the entity's fields, types, constraints.
- Provider-neutral project guidance supplied by the invoking project capability, when available.

## Protocol

1. **Read project guidance.** Use the evidence supplied by the invoking capability; do not select or
   invoke a provider here.
2. **Inspect existing patterns.** Read where the repo already keeps domain models (placement, naming, base types). Do not reinvent placement — match it.
3. **RED.** Write the failing test first that encodes the task's acceptance criteria (invariants, value-object equality, factory rejection of invalid input). Run it; classify the first run aloud (`GOOD red` / `BAD red` / `false-pass` / `NON-red`); quote the failing line.
4. **GREEN.** Write the minimal domain code to pass, applying supplied guidance and keeping framework or SDK types out of the domain.
5. **REFACTOR.** Tidy while staying green.
6. **VALIDATE.** Run the project's applicable lint, typecheck, and domain unit tests. They must pass.
7. **Report.** Emit the typed status line (see Output). Mark the task `[x]` only on a passing gate.

## Output

- The domain code file(s) + their test(s), placed per the repo's convention.
- A typed status line the dispatcher parses:
  - `Status: IMPLEMENTED-and-validated` · `Tests: <n passed>`
  - or `Status: BLOCKED-guidance` / `Status: STUCK-red`.

## Validation / Definition of Done

- The test was written and failed **first** (load-bearing RED).
- No framework/SDK import appears in the domain file.
- Project validation passes; the status line is emitted.

## Anti-patterns

- **Ignoring project guidance supplied by the invoking capability.**
- **Leaking framework types into the domain model.**
- **Weakening the test to force green.** Forbidden — escalate instead (retry → stronger model → split → ask human → rollback).
- **Reaching up into a stage** if more work appears — stop and name the next stage (one-way control).
