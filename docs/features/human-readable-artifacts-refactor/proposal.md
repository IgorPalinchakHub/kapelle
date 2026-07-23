# Human-readable Kapelle feature artifacts

## Summary

Refactor Kapelle so a user can understand and control a feature through a small OpenSpec-like set
of Markdown documents, while machine-only execution state lives under `_kapelle/`.

## Problem

The current feature directory mixes product documentation with task graphs, audit logs, revision
sidecars, review output, and runtime evidence. Medium and large features become difficult to scan,
and the user must understand Kapelle internals to know the actual status.

## Goal

Make the normal feature package:

```text
STATUS.md
proposal.md
spec.md
design.md
tasks.md
test-plan.md
contracts/
adr/
```

All LLM-only, JSON, JSONL, fingerprints, reviews, telemetry, and execution state live under
`_kapelle/`.

## Observable outcome

- `STATUS.md` answers what is happening, what is blocked, and what command is next.
- Product and QA can use `proposal.md` and `spec.md`.
- Developers can use `design.md`, contracts, ADRs, tasks, and test plan.
- Removing `_kapelle/` does not prevent later continuation.
- Recovery never fabricates approvals, reviews, command output, or validation evidence.

## Scope

- Feature layout and artifact presentation contracts.
- New `/kapelle:status` utility.
- Deterministic status building, recovery, feature-state validation, and legacy migration.
- Stage protocols updated to write the new layout.
- Review/ship freshness and documentation-convergence gates.
- Updated examples and user documentation.

## Non-goals

- One-click autonomous orchestration.
- Replacing project-native skills or architecture-rules capabilities.
- Reconstructing deleted historical evidence.
- Automatically changing product requirements to match accidental code behavior.
- Performing git operations.

## Risks

- A hard cut-over could strand existing feature directories.
- Markdown parsing can become ambiguous if generated fields are not constrained.
- Treating recovered checkboxes as proof could create false ship readiness.
- Duplicating human and machine task state could drift without deterministic validation.

## Decisions

- Layout version 2 uses human Markdown as durable state and `_kapelle/` as derived state/evidence.
- Existing layouts are supported through explicit migration and read-only recovery, not silent
  destructive moves.
- `STATUS.md` is generated and must not be edited as an independent source of truth.

