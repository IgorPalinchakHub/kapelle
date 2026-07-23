---
name: decompose
description: >
  Decompose a feature into architecture-aligned workstreams and bounded, dependency-ordered tasks.
---

# Skill: decompose

`decompose` bridges design artifacts to implementation without choosing project skills or agents.

## Inputs

- Gate: `docs/features/<slug>/spec.md` and `docs/features/<slug>/design.md`.
- Require `docs/features/<slug>/_kapelle/surface-plan.json`.
- Read `contracts/*`, optional `sequences.md`, ADRs, and test plan when present.
- Require current design architecture-guidance evidence, or refresh it for the decomposition scope.
- Contract: [`../../references/task-decomposition.md`](../../references/task-decomposition.md).
- With `--change=<change-id>`, read its approved impact matrix and create only delta tasks.

## Protocol

1. Refuse if `spec.md` or `design.md` is missing.
2. Validate `_kapelle/surface-plan.json` against `dispatcher/surface-plan.schema.json` and reject unknown
   aspect dependencies, contract participants, or integration-check participants.
3. Require architecture-guidance evidence covering all planned aspects/modules and write
   `_kapelle/architecture-guidance/tasks.json`. Reuse current design evidence without another agent
   run when its scope is sufficient. If it is missing or narrower than the decomposition scope,
   semantically dispatch the project's architecture-rules subagent. Refuse on blocking gaps.
4. Select decomposition depth:
   - `compact` for a cohesive XS/S outcome;
   - `standard` for M;
   - `hierarchical` for L/XL.
   Feature size selects decomposition depth, not the later execution depth of every task.
5. If an XL request contains independently shippable outcomes, stop with
   `Status: BLOCKED-split-required` and propose feature slugs instead of creating a monolithic plan.
6. Define architecture-aligned workstreams with outcomes, aspect ownership, dependencies, one
   completion task, and observable completion signals. Even `compact` uses one workstream for a
   stable output shape. For an M feature, prefer 3–7 workstreams and 7–15 tasks; exceeding this is a
   review signal, not permission to weaken AC or architecture coverage.
7. Within each workstream, create bounded tasks following
   `references/task-decomposition.md`. For a change request, preserve unaffected canonical tasks
   and their evidence without replanning them; add or modify only the approved delta.
8. Assign one primary aspect to every task. Keep contract provider, provider implementation,
   consumer implementation, and cross-aspect integration independently verifiable. Provider tasks
   must precede consumers, and each integration check must have exactly one owner task.
9. Add dependency ids, covered acceptance criteria, Definition of Done, validation procedure and
   expected result, risk, contract references, aspect ids, and file/module/entrypoint hints.
   Parallel candidates require known, pairwise-disjoint file ownership.
10. Do not add routing labels, skill names, agent names, provider names, rule queries, or gate names.
11. Write the draft `_kapelle/task-plan.json`, validate it against `dispatcher/task-plan.schema.json` and each
    task against `dispatcher/task-context.schema.json`, then run:

    ```text
    scripts/validate_task_plan.py \
      --tasks docs/features/<slug>/_kapelle/task-plan.json \
      --surface-plan docs/features/<slug>/_kapelle/surface-plan.json \
      --spec docs/features/<slug>/spec.md
    ```

12. At `standard` or `hierarchical` depth, dispatch exactly one fresh `kapelle:critic` decomposition
    review and validate its result against `dispatcher/decomposition-review.schema.json`. Apply at
    most one correction pass and rerun semantic validation. Stop if blocking findings remain.
13. Ensure the workstream and task graphs are acyclic, respect architecture and contract
    dependencies, and cover every acceptance criterion and integration check.
   During revision reconciliation, preserve existing task ids and evidence; apply `keep`,
   `revalidate`, `rework`, and `supersede` dispositions instead of silently replacing tasks.
14. Write:
    - compact `docs/features/<slug>/tasks.md`;
    - final `docs/features/<slug>/_kapelle/task-plan.json`;
    - semantic evidence to `_kapelle/task-plan-validation.txt`;
    - M/L/XL review to `_kapelle/reviews/decomposition.json`.
15. Refresh `STATUS.md` and emit handoff to `/kapelle:plan-tests <slug>`.

## Output Contract

```json
{
  "slug": "<slug>",
  "decomposition_depth": "standard",
  "architecture_guidance_path": "_kapelle/architecture-guidance/tasks.json",
  "workstreams": [
    {
      "id": "WS-PROVIDER",
      "title": "Establish invoice provider behavior",
      "intent": "Deliver a stable provider contract and behavior",
      "aspects": ["backend"],
      "depends_on": [],
      "completion_task_id": "T1",
      "completion_signal": "Provider contract validation passes"
    }
  ],
  "tasks": [
    {
      "id": "T1",
      "title": "Implement invoice provider behavior",
      "intent": "Expose invoice creation through the declared provider contract",
      "workstream_id": "WS-PROVIDER",
      "deps": [],
      "acs": ["AC-01"],
      "dod": "Provider behavior and contract validation pass",
      "module_hint": null,
      "primary_aspect": "backend",
      "aspects": ["backend"],
      "entrypoint_hint": "http",
      "provides_contracts": ["invoice-api"],
      "consumes_contracts": [],
      "integration_checks": [],
      "validation": [
        {
          "kind": "automated",
          "procedure": "Run the project-defined provider contract check",
          "expected": "The provider matches the declared contract"
        }
      ],
      "risk": "medium",
      "parallel_candidate": false,
      "ownership_status": "known",
      "files_hint": ["src/..."],
      "status": "pending"
    }
  ],
  "split_recommendations": []
}
```

Hints describe the work; they never select a capability.

## Definition of Done

- Every acceptance criterion is covered.
- Workstreams have coherent outcomes and an acyclic dependency graph.
- Every task references declared aspects and every cross-aspect integration check is covered.
- Tasks have one primary aspect, bounded intent, explicit validation, contract references, risk,
  and ownership evidence.
- Tasks are dependency ordered and independently verifiable.
- `scripts/validate_task_plan.py` passes.
- M/L/XL plans have one bounded independent decomposition review.
- No runtime routing metadata is present.
