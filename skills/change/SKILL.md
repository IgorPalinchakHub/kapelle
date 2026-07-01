---
name: change
model: opus
effort: high
description: >
  Safely modify an existing feature as a bugfix, enhancement, or behavior-preserving refactor.
  Capture immutable revisions, pause active implementation for amendments, invalidate dependent
  artifacts, reconcile existing work, obtain route approval, and execute only necessary Kapelle
  stages. Invoke as /kapelle:change <slug> [--mode=bugfix|enhancement|refactor] "<description>" or
  /kapelle:change <slug> --change=<id> --revise "<amendment>".
---

# Skill: change

Coordinate a traceable change to an existing feature without rerunning the full SDLC blindly.

## Inputs

- Existing feature slug and change description.
- Optional `--mode=bugfix|enhancement|refactor`.
- Optional `--change=<change-id>` for a caller-controlled id.
- Optional `--revise "<amendment>"` for an active change.
- Contract: [`../../references/change-lifecycle.md`](../../references/change-lifecycle.md).
- Agent orchestration: [`../../references/agent-orchestration.md`](../../references/agent-orchestration.md).

## Protocol

1. Require a feature slug and description/amendment.
2. If `--revise` is present:
   - require an existing change and state `running`, `paused`, or `blocked`;
   - stop all implementation dispatch and write a safe checkpoint to `active-state.json`;
   - increment the revision and create immutable `revisions/rNNN/`;
   - continue at step 4 with the amendment as the delta.
3. Otherwise infer mode, initialize revision `r001`, and permit an imported baseline only when
   repository evidence identifies existing behavior.
4. Dispatch `kapelle:explorer` for behavior, artifacts, source/tests, contracts, schema, and
   precedents. Compute fingerprints with `scripts/artifact_fingerprint.py`.
5. Build acceptance-criteria impact, artifact impact, and transitive invalidation.
6. Dispatch `kapelle:critic` against classification, amendment, stale set, and minimal route.
7. For revision 2+, dispatch `kapelle:change-reconciler`; validate
   `reconciliation.json` against `dispatcher/reconciliation.schema.json`.
8. Write or update `change.json`, `change.md`, `active-state.json`, revision data, artifact
   sidecars, and snapshots. Validate the root request against
   `dispatcher/change-request.schema.json` and all revision artifacts against their matching
   schemas.
9. Show amendment, stale artifacts, task dispositions, risks, and route. Require `approve`,
   `request changes`, or `abort`.
10. On approval, execute only route stages through their existing contracts. Pass
    `--change=<change-id>` and current revision; append outcomes to `progress.jsonl`.
11. When all stale upstream artifacts are resolved, set state `resumable` and hand off to
    `/kapelle:resume <slug> --change=<change-id>`.
12. Emit the stage-handoff block with the current revision, artifacts to review, and exact resume
    command.

## Definition of Done

- Mode is explicit and semantically correct.
- Baseline and code evidence identify pre-change behavior.
- Every approved revision is immutable and linked to its parent.
- Artifact fingerprints and dependency invalidation are current.
- Existing tasks are reconciled for revision 2+.
- Impact matrix and route were approved before canonical edits.
- Only approved artifacts and stages were changed.
- Progress is durable and the final implementation passed adaptive review and validation.

## Anti-patterns

- Treating a behavior change as a refactor.
- Fixing a missing or incorrect requirement without reclassifying to enhancement.
- Overwriting canonical artifacts before baseline capture and approval.
- Editing code while revision state is `paused`, `reconciling`, or `waiting-approval`.
- Mutating an approved revision.
- Resuming from a stale implementation plan.
- Running every SDLC stage regardless of impact.
- Copying project source into change artifacts.
- Running git operations.
