# Task decomposition contract

Kapelle decomposes a feature into a small number of architecture-aligned workstreams and bounded,
independently verifiable tasks. The result must be executable by the implementation dispatcher
without another global planning pass.

## Inputs

Read only the canonical feature artifacts, current scoped architecture guidance, and cited
repository precedents:

```text
spec.md
sad.md
surface-plan.json
sequences.md
data-model.md
contracts/
adr/
_audit/architecture-guidance/design.json
```

Do not rescan the repository broadly. Refresh architecture guidance only when the design evidence
does not cover the task-decomposition scope.

## Decomposition depth

| Feature evidence | Decomposition |
|---|---|
| XS/S, one cohesive outcome | `compact` |
| M, several coordinated changes | `standard` |
| L/XL, multiple aspects or dependency chains | `hierarchical` |

Every output uses workstreams. `compact` normally has one workstream; `hierarchical` uses multiple
workstreams to keep the task graph readable.

If an XL request contains independently shippable outcomes, stop with
`Status: BLOCKED-split-required` and propose feature slugs. Do not hide multiple features inside one
large task plan.

## Workstream rules

A workstream is an architecture-aligned delivery slice, not merely a directory or technical layer.
It has:

- one coherent outcome;
- declared aspects and dependencies;
- one completion task that depends on all other tasks in the workstream;
- a completion signal observable at the workstream boundary.

Prefer dependency order such as data/model → provider contract → provider behavior → consumers →
integration, while following the project's actual architecture rules.

## Atomic task rules

Every task must:

- have one testable intent and one primary aspect;
- fit one focused implementation/review cycle;
- be independently validatable after its dependencies complete;
- cite covered acceptance criteria;
- have an explicit Definition of Done;
- declare validation procedure and expected result;
- declare contract provider/consumer references;
- own at most the integration checks it actually validates;
- declare file ownership as `known` or `unknown`;
- avoid combining contract definition, provider implementation, consumer implementation, and
  cross-aspect integration in one task.

`provides_contracts` means that the task establishes the stable contract boundary; exactly one task
owns that responsibility per declared contract. Provider implementation tasks may depend on it
without claiming the same contract.

Split a task when its clauses can fail, be reviewed, or ship independently. Do not split mechanical
files that have no independently useful completion signal.

## Architecture gate

Task boundaries and dependency direction must be checked against scoped project architecture rules.
Write the evidence to:

```text
docs/features/<slug>/_audit/architecture-guidance/tasks.json
```

When current design evidence already covers every planned aspect/module/path, reuse it and write a
task-scoped evidence record without another subagent run. Dispatch the project architecture-rules
subagent only for uncovered scope or blocking uncertainty.

Kapelle does not put rule codes, skill names, agent names, or routing labels in `tasks.json`.

## Efficient review protocol

1. Draft the complete workstream/task graph once.
2. Run `scripts/validate_task_plan.py`.
3. For `standard` and `hierarchical`, dispatch one fresh `kapelle:critic` pass against the graph,
   feature artifacts, and architecture evidence.
4. Apply at most one correction pass and rerun semantic validation.
5. If blocking findings remain, stop. Do not enter an open-ended decomposition loop.

The critic checks missing outcomes, oversized tasks, architecture violations, contract ordering,
acceptance-criteria coverage, integration ownership, unsafe parallel claims, and unnecessary task
fragmentation.

For an existing-feature change, `tasks.json` remains the complete canonical plan. Preserve
unaffected tasks and evidence; only the approved delta is decomposed or changed. This keeps global
acceptance-criteria, contract, and integration validation meaningful.

When a preserved legacy task predates this contract, add the missing structural fields from existing
evidence without changing its intent, status, acceptance criteria, or completion evidence. Mark
unknown file ownership honestly; do not invent precision to make validation pass.

## Feature size versus task execution depth

Feature size controls decomposition depth only. During implementation, each task receives its own
execution depth from local risk and complexity. A large feature may contain many `lean` mechanical
tasks; it must not force every task through full-cost execution.
