---
name: feature-review
description: >
  Run clean-context review against spec, architecture, contracts, tests, and available project guidance. Invoke as /kapelle:feature-review <slug> for feature-scoped work.
---

# Skill: feature-review

Run clean-context review against spec, architecture, contracts, tests, and available project guidance.

## Inputs

- `<slug>` for feature-scoped work.
- Reads: `implemented diff + feature artifacts`.
- Requires `surface-plan.json` and scoped architecture-guidance evidence for implemented tasks.
- With `--change=<change-id>`, also read its baseline, approved impact matrix, and progress log;
  review for unapproved behavioral or artifact drift.
- Shared contract: [`../../references/stage-contract.md`](../../references/stage-contract.md).
- Agent contract: [`../../references/agent-orchestration.md`](../../references/agent-orchestration.md).
- Validation execution:
  [`../../references/validation-execution.md`](../../references/validation-execution.md).

## Protocol

1. Validate required inputs. If missing, refuse with the named producing stage.
2. Collect feature artifacts, changed-file evidence supplied by the host, implementation audit
   records, scoped project architecture guidance, and applicable general project guidance.
3. Inspect validation-decision evidence. If any required command or integration check is missing,
   failed, skipped, or cancelled, continue the read-only review but require
   `Status: BLOCKED-validation-deferred`; do not issue `PASS`.
4. Dispatch `kapelle:reviewer` in fresh read-only context.
5. Require the reviewer to cover every affected aspect, provider/consumer contract, and
   cross-aspect integration check.
6. Require a structured `PASS`, `CHANGES_REQUESTED`, or `BLOCKED` verdict matching
   `dispatcher/execution-verdict.schema.json`.
7. Write outputs: `_review/review-<date>.md`.
8. Emit the stage-handoff block per [`../../references/handoff.md`](../../references/handoff.md).

## Output

- `_review/review-<date>.md`.
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
