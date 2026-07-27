---
name: migrate
description: >
  Adopt an existing feature into the lightweight start-implement-verify workflow while preserving
  human documents and never fabricating historical evidence.
---

# Skill: migrate

Invoke:

```text
/kapelle:migrate <slug>
/kapelle:migrate <slug> --apply
```

## Protocol

1. Dry-run first:

```text
scripts/migrate_workflow.py docs/features/<slug>
```

   Report preserved documents, missing `spec.md`/`design.md`/`tasks.md`, evidence that cannot be
   reconstructed, and the next command.
2. `spec.md` is the only migration prerequisite because it carries the durable lightweight marker.
   If it is missing, use `/kapelle:start <slug> "<raw task or current feature intent>"`.
3. On explicit `--apply`, run:

```text
scripts/migrate_workflow.py docs/features/<slug> --apply
```

   This adds the marker, writes workflow version 2, and rebuilds status. It preserves existing
   `proposal.md`, detailed specs/designs, contracts, ADRs, task evidence, and history.
4. Migration never creates plan/final approvals, validation results, agent reviews, command output,
   or telemetry. `/kapelle:start` compacts/revises the human package only when the developer asks.
5. Perform no production-code, validation, or git changes.

Handoff to the exact command returned by the migration helper.
