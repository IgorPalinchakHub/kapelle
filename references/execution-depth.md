# Adaptive execution depth

Kapelle keeps every SDLC stage independently invocable, but scales the work inside a stage to the
feature's size and risk. Execution depth reduces duplicate analysis; it never weakens required
artifacts, architecture guidance, acceptance-criteria coverage, or validation.

## Selection

Read `docs/features/<slug>/.size` when present:

| Evidence | Depth |
|---|---|
| `XS` or `S`, one aspect, established pattern, no risk trigger | `lean` |
| `M`, or uncertainty that does not trigger full depth | `standard` |
| `L` or `XL`, or any risk trigger | `full` |

Risk triggers always escalate to `full`: public contract changes, authorization/security, destructive
data changes, ambiguous business invariants, a new architectural pattern, or cross-aspect work with
an unestablished shared contract or unclear ownership. A routine backend/frontend change over an
existing contract may remain `standard`.

Record the selected depth and reason in the stage output or feature audit. A later stage may escalate
depth from new evidence, but must not silently reduce it.

## Dispatch budget

- `lean`: reuse cited upstream analysis; perform routine checks inline; dispatch a subagent only for
  a required project capability or a material ambiguity.
- `standard`: dispatch one focused specialist or critic where it adds independent evidence.
- `full`: use the complete adversarial, architecture, planning, test, and review roles required by
  the stage.

Specific rules:

- `specify` and `clarify` must not repeat the same adversarial review. At `lean`, `specify` performs
  one inline acceptance-criteria check and `clarify` runs only a delta ambiguity sweep.
- `design` always dispatches the project's architecture-rules capability. It dispatches
  `kapelle:critic` only at `standard`/`full` or when a risk trigger is present.
- `data-model` dispatches `kapelle:explorer` only when persistence is affected and cited precedents
  are missing.
- `implement` always persists a plan. At `lean`, a low-risk task may execute the planner role inline
  and defer independent review to the feature-level `review` stage. Risk-triggered tasks always use
  a fresh `kapelle:implementation-planner` and per-task `kapelle:reviewer`.
- `test-author` execute mode is skipped for `validation-only` work that creates no test artifact.

## Explicit skips

An inapplicable stage writes its normal artifact containing a short `Status: SKIPPED-confirmed`
record with the evidence for the skip. Downstream stages therefore retain a stable file contract and
never infer a skip from a missing file.
