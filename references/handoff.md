# Backbone and Utility Handoff

Use this at the end of each backbone stage:

```md
## <stage> — <slug>

**What I did**
- wrote/updated `<artifact>`

**Review before continuing**
- `<artifact>` — what to inspect

**Run next**
`/kapelle:<next-stage> <slug>`
```

Recommend `/clear` only when the current context is noisy or an independent final review matters.
Do not require it between normal workstream checkpoints.

Optional utilities use the same readable sections but label the heading `utility`. They never
invent a second pipeline. When they change `spec.md`, `design.md`, `tasks.md`, an ADR, or a durable
contract, their next command is `/kapelle:start <slug> --approve`; otherwise it is
`/kapelle:status <slug>`.
