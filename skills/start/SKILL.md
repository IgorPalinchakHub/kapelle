---
name: start
description: >
  Start a feature from a raw developer task, discover current behavior, select fast or standard
  planning and interview depth, and produce the smallest complete human-reviewable draft.
---

# Skill: start

Invoke:

```text
/kapelle:start <slug> "<raw task>" [--lane=auto|fast|standard] [--interview=auto|lean|standard|deep]
/kapelle:start <slug> --approve
/kapelle:start <slug> --revise "<developer feedback>"
```

Read [`../../references/fast-lane.md`](../../references/fast-lane.md),
[`../../references/interview-depth.md`](../../references/interview-depth.md), and
[`../../references/design-template.md`](../../references/design-template.md).

## Protocol

1. Require a stable slug and raw task for a new feature. Ask only one consolidated question when
   intended behavior or plausible project ownership cannot be established.
2. Dispatch `kapelle:explorer` read-only to discover current behavior, actors, entrypoints,
   business flows, data, integrations, tests, precedents, and the project boundary.
3. Separate observed behavior, requested behavior, assumptions, and unresolved decisions.
4. Classify `XS|S|M|L|XL`, risk triggers, interview depth, and lane. `auto` is default. A requested
   fast lane never overrides a risk trigger.
5. Apply interview depth:
   - lean: inline challenge, no critic/devil subagent;
   - standard: business analysis plus one combined critic pass;
   - deep: business analyst, one fresh critic, one fresh devil's advocate.
   Allow at most one correction pass.
6. Write `proposal.md` beginning with:

```text
<!-- kapelle-workflow: human-controlled-v1; lane: fast|standard -->
```

   Also write `spec.md`, `_context/architecture.md`, `_kapelle/workflow.json`, and
   `_kapelle/size.json`.
7. In `standard`, stop after the concise outline and hand off to `/kapelle:spec <slug>`.
8. In `fast`, complete the bounded planning package in this invocation:
   - complete the small specification inside `spec.md`;
   - obtain scoped project architecture rules;
   - write `design.md` using every required design-template heading;
   - write vertical `tasks.md` with an inline Test strategy section;
   - write `_kapelle/surface-plan.json` and `_kapelle/task-plan.json`, then run
     `scripts/validate_task_plan.py`;
   - create at most three production tasks and no unit-test-writing task;
   - do not require `specs/`, `design/`, `contracts/`, or `test-plan.md` unless evidence makes one
     necessary, in which case escalate to standard.
9. Present the complete fast package and require one explicit approval. On `--approve`, validate
   the existing package and run `scripts/review_gate.py approve docs/features/<slug> feature-plan
   --confirmation "Developer explicitly approved the fast feature plan."`. Never construct gate
   JSON manually. The helper owns canonical
   `_kapelle/approvals/feature-plan.json`. `--approve` may not generate missing artifacts.
10. On `--revise`, update the current lane's draft and invalidate downstream evidence.
11. Refresh `STATUS.md` once when the review-gate helper has not already refreshed it. Never
    hand-edit manifest, state, status, or approval JSON. A standard handoff is `spec`; an approved
    fast handoff is `base-functional-tests`.

## Review packet

Return observed current behavior, selected size/lane/depth with reason, proposed outcome, at most
three decisions, files to review, and the exact revise/approve/next command. Hide agent chatter.

Use the standard backbone handoff block from `references/handoff.md`. Never run git operations.
