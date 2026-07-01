---
name: tasks
model: inherit
effort: medium
description: >
  Break a feature into atomic, dependency-ordered implementation tasks with descriptive context. Invoke as /kapelle:tasks <slug>.
---

# Skill: tasks

`tasks` bridges design artifacts to implementation without choosing project skills or agents.

## Inputs

- Gate: `docs/features/<slug>/spec.md` and `docs/features/<slug>/sad.md`.
- Require `docs/features/<slug>/surface-plan.json`.
- Read `data-model.md`, `contracts/*`, `sequences.md`, ADRs, and test plan when present.
- With `--change=<change-id>`, read its approved impact matrix and create only delta tasks.

## Protocol

1. Refuse if `spec.md` or `sad.md` is missing.
2. Validate `surface-plan.json` against `dispatcher/surface-plan.schema.json` and reject unknown
   aspect dependencies, contract participants, or integration-check participants.
3. Split work into atomic tasks with one testable intent each. For a change request, exclude
   unaffected existing-feature work.
4. Assign every task one or more aspect ids from `surface-plan.json`. Provider-side contract tasks
   must precede consumer implementation tasks, and every cross-aspect integration check must be
   owned by a final validation task.
5. Add dependency ids, covered acceptance criteria, Definition of Done, aspect ids, integration
   check ids, and file/module/entrypoint hints when useful.
6. Do not add routing labels, skill names, agent names, provider names, rule queries, or gate names.
7. Validate every task against `dispatcher/task-context.schema.json`.
8. Ensure the dependency graph is acyclic, respects aspect and contract dependencies, and covers
   every acceptance criterion and integration check.
   During revision reconciliation, preserve existing task ids and evidence; apply `keep`,
   `revalidate`, `needs-rework`, and `superseded` dispositions instead of silently replacing tasks.
9. Write `docs/features/<slug>/tasks.json` and optional human-readable `tasks/*.md`.
10. Emit handoff to `/kapelle:plan-tests <slug>`.

## Output Contract

```json
{
  "slug": "<slug>",
  "tasks": [
    {
      "id": "T1",
      "title": "Create invoice endpoint",
      "intent": "Expose invoice creation through the project's HTTP interface",
      "deps": [],
      "acs": ["AC-01"],
      "dod": "A testable completion statement",
      "module_hint": null,
      "aspects": ["backend"],
      "entrypoint_hint": "http",
      "integration_checks": [],
      "files_hint": ["src/..."],
      "status": "pending"
    }
  ]
}
```

Hints describe the work; they never select a capability.

## Definition of Done

- Every acceptance criterion is covered.
- Every task references declared aspects and every cross-aspect integration check is covered.
- Tasks are dependency ordered and independently verifiable.
- No runtime routing metadata is present.
