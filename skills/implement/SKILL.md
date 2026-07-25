---
name: implement
description: >
  Implement approved production tasks without writing unit tests, using project capabilities,
  scoped architecture rules, bounded retries, explicit human checkpoints, and amendment safety.
---

# Skill: implement

Implement production behavior only. Basic functional tests already exist; all unit tests are
written later by `/kapelle:unit-tests`.

Invoke:

```text
/kapelle:implement <slug> [--checkpoint=task|workstream|none] [--validation=ask|allow|skip]
```

## Inputs

- `_kapelle/task-plan.json` and `_kapelle/surface-plan.json`.
- Human feature artifacts, architecture approval, delivery-plan approval, and
  `_kapelle/base-functional-tests.json` for `human-controlled` features.
- Optional approved change context under `_kapelle/changes/`.
- Project instructions and native skills/subagents.
- [`../../dispatcher/execution-contract.md`](../../dispatcher/execution-contract.md).
- [`../../references/agent-orchestration.md`](../../references/agent-orchestration.md).
- [`../../references/architecture-guidance.md`](../../references/architecture-guidance.md).
- [`../../references/human-control.md`](../../references/human-control.md).

## Protocol

1. Validate the plans and rerun `scripts/validate_task_plan.py`. Refuse code-writing for a
   provisional recovery graph or stale approval/fingerprint.
2. For a human-controlled feature, check `feature-plan` in fast lane or both `architecture` and
   `delivery-plan` in standard lane with `scripts/review_gate.py check`. Also require current
   base-functional-test evidence. A confirmed pre-implementation test skip is visible risk, never
   PASS.
3. Compute dependency-ready production tasks. Sequential execution is the default. Agent Teams
   still require runtime support, safe disjoint ownership, configuration, and explicit approval.
4. Resolve `--checkpoint` from the invocation or `implementation.checkpoint`; default to `task`.
   - `task`: stop after every completed task for developer review;
   - `workstream`: stop after each coherent workstream;
   - `none`: continue through all ready work and return one concise summary.
5. For every task execute:
   `UNDERSTAND -> SELECT-CAPABILITY -> GUIDANCE -> PLAN -> APPROVE -> IMPLEMENT -> REVIEW -> SUMMARIZE`.
   - discover project skills/subagents semantically for each aspect;
   - dispatch the project's architecture-rules subagent for scoped rules;
   - dispatch `kapelle:implementation-planner` and persist its plan with current revision and
     fingerprints;
   - apply risk-based approval and bounded retries;
   - dispatch `kapelle:implementer` and fresh `kapelle:reviewer` when risk requires it;
   - write production code and production configuration only.
6. Do not create unit tests, unit-test fixtures, or strict-TDD loops. Do not ask `test-author` to
   generate unit tests during this stage.
7. Existing base functional tests may be run as a focused development check under
   `ask | allow | skip`. Do not run full static analysis or lint batches here unless the developer
   explicitly requests them. Skipped required checks remain `validation-deferred`.
8. After each checkpoint return: implemented business outcome, changed files, observable behavior,
   deviations/risks, and the next task or command. Keep internal agent chatter out of the packet.
9. Developer feedback that changes approved behavior, design, contract, or task ownership triggers
   `/kapelle:amend`; pause remaining dispatch.
10. Mark implemented tasks `implemented-unverified`, not `completed`. Synchronize `tasks.md`,
    `_kapelle/task-plan.json`, task-run evidence, and `STATUS.md`.
11. When every production task is implemented, hand off to `/kapelle:unit-tests <slug>
    --validation=ask`.
12. Stop edit retries at `implementation.max_task_attempts` and role dispatches at
    `implementation.max_agent_runs_per_task`.

## Definition of Done

- All selected production tasks have current plans, scoped architecture guidance, implementation
  evidence, and required reviews.
- No unit tests were authored in this stage.
- Human checkpoint policy and validation decisions are recorded.
- Requirements/design changes were routed through amendment.
- Retry limits, file ownership, and no-git policy were respected.
