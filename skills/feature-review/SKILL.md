---
name: feature-review
description: >
  Run clean-context feature review against spec, architecture, contracts, tests, and project guidance.
---

# Skill: feature-review

Run clean-context review against spec, architecture, contracts, tests, and available project guidance.

## Inputs

- `<slug>` for feature-scoped work.
- Reads: `implemented diff + feature artifacts`.
- Requires `_kapelle/surface-plan.json` and scoped architecture-guidance evidence for implemented tasks.
- With `--change=<change-id>`, also read its baseline, approved impact matrix, and progress log;
  review for unapproved behavioral or artifact drift.
- Shared contract: [`../../references/stage-contract.md`](../../references/stage-contract.md).
- Agent contract: [`../../references/agent-orchestration.md`](../../references/agent-orchestration.md).
- Validation execution:
  [`../../references/validation-execution.md`](../../references/validation-execution.md).

## Protocol

1. Validate required inputs. If missing, refuse with the named producing stage.
2. Collect feature artifacts, changed-file evidence supplied by the host, implementation
   records, scoped project architecture guidance, and applicable general project guidance.
3. Inspect validation-decision evidence. If any required command or integration check is missing,
   failed, skipped, or cancelled, continue the read-only review but require
   `Status: BLOCKED-validation-deferred`; do not issue `PASS`.
4. Before the final review, reconcile `proposal.md`, `spec.md`, `design.md`, contracts, ADRs,
   `tasks.md`, and `test-plan.md` against the current implementation. Do not rewrite requirements
   to match accidental code behavior; route observable changes through the change lifecycle.
5. Write `_kapelle/reviews/documentation-convergence.json` with complete current input
   fingerprints (including normalized coordination graphs), current implementation-file
   fingerprints, and `PASS | CHANGES_REQUIRED | BLOCKED`; validate it against
   `dispatcher/documentation-convergence.schema.json`. Refuse a final `PASS` while convergence is
   not current.
6. Dispatch `kapelle:reviewer` in fresh read-only context.
7. Require the reviewer to cover every affected aspect, provider/consumer contract, and
   cross-aspect integration check.
8. Require a structured `PASS`, `CHANGES_REQUESTED`, or `BLOCKED` feature verdict matching
   `dispatcher/feature-review.schema.json`; its validation files must cover every completed task.
9. Write `_kapelle/reviews/feature-review.json` with the same current input fingerprints and the
   validation evidence file for every completed task, refresh `STATUS.md`, and
   emit the chat handoff.

## Output

- `_kapelle/reviews/documentation-convergence.json`,
  `_kapelle/reviews/feature-review.json`, and refreshed `STATUS.md`.
- `Status: DONE | stage: feature-review | produced: <paths>`.

## Definition of Done

- Inputs were read from disk.
- Outputs exist and link to upstream artifacts instead of duplicating them.
- Skips are explicit.
- Handoff points to `ship`.
- A `PASS` verdict has no unresolved required validation.

## Anti-patterns

- Guessing missing prior-stage output.
- Baking project-specific conventions or provider assumptions into the core skill.
- Running git operations.
