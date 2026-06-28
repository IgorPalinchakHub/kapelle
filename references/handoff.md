# Stage Handoff Block

Use this at the end of each backbone stage:

```md
## <stage> — <slug>

**What I did**
- wrote/updated `<artifact>`

**Review before continuing**
- `<artifact>` — what to inspect

**Run next**
1. `/clear`
2. `/kapelle:<next-stage> <slug>`
```

For review -> implement loopbacks, say explicitly whether `/clear` should be skipped to keep fix context.
