# Adaptive execution depth

Kapelle scales work inside the single human-controlled pipeline. Execution depth reduces duplicate
analysis; interview depth controls clarification/adversarial work; lane controls artifact/stage
shape. None weakens architecture guidance, acceptance-criteria coverage, or validation.

## Selection

Read `docs/features/<slug>/_kapelle/size.json` when present:

| Evidence | Depth |
|---|---|
| `XS` or `S`, one aspect, established pattern, no risk trigger | `lean` |
| `M`, or uncertainty that does not trigger full depth | `standard` |
| `L` or `XL`, or any risk trigger | `full` |

Risk triggers always escalate to `full`: public contract changes, authorization/security, destructive
data changes, ambiguous business invariants, a new architectural pattern, or cross-aspect work with
an unestablished shared contract or unclear ownership. A routine backend/frontend change over an
existing contract may remain `standard`.

Record the selected depth and reason under `_kapelle/`. A later stage may escalate depth from new
evidence, but must not silently reduce it.

Feature size controls stage and decomposition depth. It does not automatically control every
implementation task. After decomposition, task execution depth is selected independently:

| Task evidence | Execution depth |
|---|---|
| Low risk, established pattern, bounded files, no public contract | `lean` |
| Medium risk, contract consumer/provider, or moderate coordination | `standard` |
| High risk, security, destructive data, ambiguous invariant, or new public contract | `full` |

## Dispatch budget

- `lean`: reuse cited upstream analysis; perform routine checks inline; dispatch a subagent only for
  a required project capability or a material ambiguity.
- `standard`: dispatch one focused specialist or critic where it adds independent evidence.
- `full`: use the complete adversarial, architecture, planning, test, and review roles required by
  the stage.

Specific rules:

- `start` performs bounded discovery, writes size/lane/depth, and follows
  `interview-depth.md`.
- `spec` uses the same recorded interview depth and never repeats an already accepted adversarial
  pass.
- `design` always dispatches the project's architecture-rules capability. It dispatches
  `kapelle:critic` only at `standard`/`full` or when a risk trigger is present.
- `data-model` dispatches `kapelle:explorer` only when persistence is affected and cited precedents
  are missing.
- `implement` always persists a plan. At `lean`, a low-risk task may execute the planner role
  inline. Risk-triggered tasks use a fresh planner and reviewer.
- Test-author runs only for the base-functional or post-implementation unit-test phases.

## Explicit skips

An inapplicable optional stage records `Status: SKIPPED-confirmed` and evidence in
`_kapelle/state.json`. Downstream stages never infer a skip from silence.
