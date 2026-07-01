---
name: resume
model: opus
effort: high
description: >
  Resume a paused Kapelle existing-feature change after requirement or architecture revision.
  Verify fingerprints, stale-artifact resolution, task reconciliation, and current implementation
  plans before continuing. Invoke as /kapelle:resume <slug> --change=<change-id>.
---

# Skill: resume

Resume implementation only from a reconciled and approved immutable change revision.

## Inputs

- Feature slug and required `--change=<change-id>`.
- `change.json`, `active-state.json`, current revision, artifact sidecars, reconciliation, tasks,
  implementation plans, and audit evidence.
- Contract: [`../../references/change-lifecycle.md`](../../references/change-lifecycle.md).

## Protocol

1. Refuse unless active state is `resumable`.
2. Validate change, state, current revision, artifact-state, reconciliation, and task files against
   their schemas.
3. Recompute every recorded artifact fingerprint with `scripts/artifact_fingerprint.py`.
4. On unexplained mismatch, set state `paused` and require another revision; do not implement.
5. Refuse while any upstream artifact is `stale` or `review-required`.
6. Verify every pre-revision task has a reconciliation disposition:
   - retain `keep`;
   - run validation for `revalidate`;
   - regenerate plan and strategy for `rework`;
   - skip `superseded`;
   - require an approved corrective task for `revert-required`.
7. Before each runnable task, verify its plan uses the current revision and current `based_on`
   fingerprints.
8. Set state `running` and continue `/kapelle:implement <slug> --change=<change-id>` from the first
   pending or `needs-rework` task.
9. Preserve previous revision evidence and append resume status to `progress.jsonl`.
10. Emit the stage-handoff block with the resumed implementation command and current revision.

## Definition of Done

- No unexplained fingerprint drift exists.
- No unresolved stale upstream artifact exists.
- Reconciliation covers every existing task.
- Every runnable task has a current plan and strategy.
- Implementation resumed under the current revision.

## Anti-patterns

- Resuming because files “look close enough”.
- Treating stale plans as current.
- Deleting superseded task evidence.
- Automatically reverting code.
- Running git operations.
