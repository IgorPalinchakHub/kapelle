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

## Protocol

1. Capture the current canonical documents, implementation inventory, test evidence, and active
   workflow state as an immutable internal revision.
2. Classify the feedback as:
   - business requirement;
   - architecture/design;
   - contract;
   - implementation defect;
   - test/documentation correction.
3. Dispatch `kapelle:change-reconciler` to compute affected spec, design, domain model, contracts,
   functional tests, tasks, production code, unit tests, verification, and diagrams.
4. Show the impact route and require explicit developer approval before edits.
5. Update canonical human documents; never create parallel versioned copies in the feature root.
6. Invalidate every downstream approval/evidence fingerprint transitively.
7. Preserve immutable history under `_kapelle/changes/` and `_kapelle/history/`.
8. Select the earliest necessary human-controlled stage and refresh `STATUS.md`.

Use the same mutation, retry, no-git, and safe-pause guarantees as `change`. The handoff is the
minimal stage needed to reconcile the amendment, not a full restart.
