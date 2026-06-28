---
name: scheduled-job-create
description: Create a scheduled job through Kapelle.
---

# Skill: scheduled-job-create

> Native project capability for scheduled-job implementation.

## Purpose

Create one **scheduled job** for the `schedule` entrypoint — a cron-triggered task that prevents overlapping runs
(leader election / lock), is idempotent across runs, and delegates the work to a handler. Depends on the Handler (order 2).

## Owner

The `implement` stage's dispatcher invokes it per task. The skill never invokes a stage (one-way control).

## Inputs (gate)

- The task intent + the schedule definition + the handler it delegates to.
- Provider-neutral project guidance supplied by the invoking project capability, when available.

## Protocol

1. **Read project guidance.** Use the evidence supplied by the invoking capability; do not select or invoke a provider here.
2. **Inspect existing patterns.** Read how scheduled jobs/locks are wired in the repo. Match it.
3. **RED.** Write the failing test first: two concurrent triggers run the job **once** (overlap prevented), a re-run is idempotent, the cron schedule is honored. Run it; classify aloud; quote the failing line.
4. **GREEN.** Minimal scheduled-job code to pass, applying supplied guidance.
5. **REFACTOR.** Tidy while staying green.
6. **VALIDATE.** Run the project's applicable quality commands. They must pass.
7. **Report.** Emit the typed status line; mark done only on green.

## Output

- The scheduled-job file(s) + test(s).
- `Status: IMPLEMENTED-and-validated` · `Tests: <n passed>`; or `Status: BLOCKED-guidance` / `Status: STUCK-red`.

## Validation / Definition of Done

- Test failed **first**; concurrent triggers do not double-run; re-runs are idempotent; project validation passes.

## Anti-patterns

- **Overlapping runs** (no lock/leader election). **A non-idempotent job.**
- **Business logic in the job** instead of the handler. **Ignoring supplied project guidance.** **Reaching up into a stage.**
