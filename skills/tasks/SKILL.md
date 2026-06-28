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
- Read `data-model.md`, `contracts/*`, sequences, ADRs, and test plan when present.

## Protocol

1. Refuse if `spec.md` or `sad.md` is missing.
2. Split work into atomic tasks with one testable intent each.
3. Add dependency ids, covered acceptance criteria, Definition of Done, and file/module/surface hints when
   useful.
4. Do not add routing labels, skill names, agent names, provider names, rule queries, or gate names.
5. Validate every task against `dispatcher/task-context.schema.json`.
6. Ensure the dependency graph is acyclic and every acceptance criterion is covered.
7. Write `docs/features/<slug>/tasks.json` and optional human-readable `tasks/*.md`.
8. Emit handoff to `/kapelle:plan-tests <slug>`.

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
      "surface_hint": "backend",
      "entrypoint_hint": "http",
      "files_hint": ["src/..."],
      "status": "pending"
    }
  ]
}
```

Hints describe the work; they never select a capability.

## Definition of Done

- Every acceptance criterion is covered.
- Tasks are dependency ordered and independently verifiable.
- No runtime routing metadata is present.
