# Revision-based existing-feature change lifecycle

Use this contract for a bug fix, enhancement, or behavior-preserving refactor, including requirement
or architecture changes discovered during implementation.

## Storage

```text
docs/features/<slug>/changes/<change-id>/
  change.json
  change.md
  active-state.json
  artifact-state/
  revisions/
    r001/
      revision.json
      request.md
      impact.json
      baseline/
    r002/
      revision.json
      amendment.md
      impact.json
      baseline/
  reconciliation.json
  progress.jsonl
```

Revisions are immutable after approval. `change.json` points to `current_revision`;
`active-state.json` owns runtime state.

## New change

Accept:

```text
/kapelle:change <slug> [--mode=bugfix|enhancement|refactor] "<description>"
```

Generate a collision-safe change id when omitted. Dispatch `kapelle:explorer` for current behavior,
artifacts, source/tests, contracts, schema, and precedents. Dispatch `kapelle:critic` against mode,
hidden behavior changes, impacted acceptance criteria, and route.

Capture revision `r001`, fingerprints, impacted artifact snapshots, and code evidence. Never copy
project source into the baseline. Show mode, impacts, risks, and minimal route; require approval
before canonical artifact edits.

## Mid-implementation revision

Accept either an explicit command or a requirement/architecture amendment expressed while
`implement` is running:

```text
/kapelle:change <slug> --change=<id> --revise "<amendment>"
```

### 1. Safe pause

Stop all new implementation edits for the change. Finish only the currently running atomic tool
operation, then:

1. set `active-state.state` to `paused`;
2. record active task, changed-file evidence, completed validations, and unresolved work;
3. set current in-progress task to `blocked` with reason `revision-pending`;
4. do not dispatch more implementation agents, including Agent Team lanes.

Transition:

```text
running -> paused -> reconciling
```

Kapelle performs no git stash, reset, checkout, or revert.

### 2. Create immutable revision

Increment the integer revision and create `rNNN/`. Record requirement, architecture, and constraint
deltas separately. Snapshot only impacted existing Kapelle artifacts and compute raw-byte SHA-256
fingerprints with:

```text
scripts/artifact_fingerprint.py --root <project> <artifact>...
```

Write `revision.json` matching `dispatcher/change-revision.schema.json`. Do not mutate an approved
older revision.

### 3. Invalidate transitively

Read the canonical graph from `dispatcher/artifact-dependencies.json`. Its effective structure is:

```text
spec.md -> sad.md -> surface-plan.json -> sequences.md
spec.md + sad.md + surface-plan.json + sequences.md -> data-model.md
spec.md + sad.md + surface-plan.json + sequences.md + data-model.md -> contracts
all design artifacts -> tasks.json
spec.md + surface-plan.json + data-model.md + contracts + tasks.json -> test-plan.md
all upstream artifacts -> implementation-plans -> validation
```

For each artifact, store a sidecar matching `dispatcher/artifact-state.schema.json` with its
fingerprint, revision, direct `based_on` fingerprints, and one status:

```text
current | review-required | stale | superseded
```

A changed upstream fingerprint marks direct dependants `stale`; propagate until a stage
regenerates the artifact against the new revision. Manual edits detected by fingerprint mismatch
follow the same revision path.

### 4. Reconcile existing work

Dispatch `kapelle:change-reconciler` and write `reconciliation.json`. Every task receives exactly
one disposition:

```text
keep | revalidate | rework | supersede | revert-required
```

Map dispositions into task state:

- `keep`: retain `completed`;
- `revalidate`: set `stale` until validation passes;
- `rework`: set `needs-rework` and replace its implementation plan/test strategy;
- `supersede`: set `superseded`;
- `revert-required`: set `blocked` and create an explicit corrective task after approval.

Never delete completed evidence or automatically revert code.

### 5. Rebuild the minimal route

- Requirement delta starts at `specify` or `clarify`.
- Architecture delta starts at `design` or `decide-adr`.
- Contract/data/flow delta starts at the corresponding stage.
- Validation-only delta starts at `plan-tests`.

Then regenerate only transitively stale downstream artifacts. Never silently expand the route.

### 6. Re-approval

Show amendment, changed acceptance criteria, stale artifacts, reconciliation dispositions, new
route, risks, and existing code requiring rework/revert. Transition:

```text
reconciling -> waiting-approval -> approved -> resumable
```

Silence is not approval. Rejection sets state to `blocked`.

## Resume

`/kapelle:resume <slug> --change=<id>` must:

1. require state `resumable`;
2. recompute fingerprints and block on unexplained drift;
3. require no unresolved `stale` upstream artifacts;
4. verify reconciliation covers every existing task;
5. regenerate plans/test strategies for `needs-rework` tasks;
6. run validation for `revalidate` tasks;
7. resume from the first pending or rework task under the current revision;
8. set state to `running` and continue through the adaptive execution contract.

Before every task, verify that its plan records the current revision and current `based_on`
fingerprints. Otherwise mark it stale and return to reconciliation.

On successful ship readiness, set state to `completed`.
