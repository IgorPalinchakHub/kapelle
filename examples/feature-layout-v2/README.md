# Layout-v2 example

This directory illustrates the separation, not a runnable feature:

```text
STATUS.md
proposal.md
spec.md
design.md
tasks.md
test-plan.md
contracts/
adr/
_kapelle/
  manifest.json
  state.json
  surface-plan.json
  task-plan.json
  architecture-guidance/
  task-runs/
  validation/
  reviews/
  telemetry/
  history/
```

Human review starts with `STATUS.md`. The root Markdown remains useful after `_kapelle/` is removed;
the internal directory accelerates execution and preserves evidence that recovery must not invent.

