---
name: amend
description: >
  Apply developer feedback or changed requirements during implementation, verification, or manual
  testing by versioning the change, updating affected artifacts, and invalidating downstream state.
---

# Skill: amend

Invoke:

```text
/kapelle:amend <slug> "<feedback or changed requirement>"
/kapelle:amend <slug> --change=<change-id> --revise "<additional feedback>"
```

Read [`../../references/developer-questions.md`](../../references/developer-questions.md) before
asking the developer to choose an impact route or behavior change.

## Protocol

1. Create or update the canonical runtime records:
   - `_kapelle/changes/<change-id>/request.json`;
   - `_kapelle/changes/<change-id>/state.json`;
   - `_kapelle/changes/<change-id>/revisions/rNNN/revision.json`;
   - `_kapelle/changes/<change-id>/artifacts/*.json` for affected artifact lineage;
   - `_kapelle/changes/<change-id>/reconciliation.json` once tasks are reconciled.
   Capture the current canonical documents, implementation inventory, test evidence, and active
   workflow state as immutable revision evidence beside `revision.json`.
2. Classify the feedback as:
   - business requirement;
   - architecture/design;
   - contract;
   - implementation defect;
   - test/documentation correction.
3. Dispatch `kapelle:change-reconciler` to compute affected spec, design, domain model, contracts,
   functional tests, tasks, production code, unit tests, verification, and diagrams.
4. Show the impact route and require explicit developer approval before edits.
   Explain the observable change and route alternatives in plain language with their trade-offs;
   do not ask the developer to interpret revision, artifact, blocker, or task identifiers.
5. Update canonical human documents; never create parallel versioned copies in the feature root.
6. Invalidate every downstream approval/evidence fingerprint transitively.
7. Preserve immutable history under `_kapelle/changes/` and `_kapelle/history/`.
8. After each runtime write, run `scripts/validate_json.py` against the corresponding
   `change-request`, `change-state`, `change-revision`, `artifact-state`, or `reconciliation`
   schema. A non-zero exit blocks the lifecycle transition; never compare the JSON and schema by
   eye.
9. Select the earliest necessary human-controlled stage and refresh `STATUS.md`.

Use the same mutation, retry, no-git, and safe-pause guarantees as `change`. The handoff is the
minimal stage needed to reconcile the amendment, not a full restart.
