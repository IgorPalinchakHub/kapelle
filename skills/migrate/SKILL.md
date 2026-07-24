---
name: migrate
description: >
  Migrate a legacy Kapelle feature directory into the single human-controlled workflow without
  fabricating approvals, validation, review, or historical evidence.
---

# Skill: migrate

Invoke:

```text
/kapelle:migrate <slug>
/kapelle:migrate <slug> --apply [--lane=standard|fast]
```

## Protocol

1. Read the current human documents, `_kapelle/` state, current implementation, and available
   evidence. Do not run a legacy stage.
2. Default to standard lane. Recommend fast only when the complete eligibility contract in
   `references/fast-lane.md` is demonstrably satisfied and the developer explicitly confirms it.
3. Dry-run first: report preserved files, missing target artifacts, evidence gaps, collisions,
   selected lane, and the minimal post-migration command.
4. On `--apply`, run `scripts/migrate_workflow.py <feature-dir> --apply --lane=<lane>`.
5. Preserve canonical human documents in place. Add the durable workflow marker and
   `_kapelle/workflow.json`; rebuild derived state.
6. Never recreate lost approvals, agent verdicts, command output, validation evidence, or
   telemetry. The migrated route asks for the earliest missing approval or artifact.
7. Refresh `STATUS.md` and return the exact next human-controlled command.

Migration performs no production-code or git changes. Use the standard handoff block.
