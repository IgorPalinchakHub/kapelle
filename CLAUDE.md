# Kapelle Runtime Instructions

When a Kapelle skill runs, behave as a gated SDLC stage or utility.

## Invariants

1. Artifact is state. Read stage inputs from disk; write durable state under `docs/features/<slug>/`.
2. Missing inputs cause refusal, not guessing. Emit `Status: REFUSED-missing-input` and name the prior stage.
3. Stage -> native project capability -> guidance/tools/code is one-way. Project skills never invoke stages.
4. Code-writing goes through the dispatcher and native project capability discovery.
5. Project guidance is provider-neutral. Kapelle records evidence but never prescribes storage, search,
   rule codes, tools, agents, or commands.
6. Skips are explicit and confirmed.
7. No git operations are performed by the harness.
8. Project-specific behavior belongs in native project capabilities, not in core stages.

## Handoff

Every backbone stage ends with:

```md
## <stage> — <slug>

**What I did**
- ...

**Review before continuing**
- ...

**Run next**
1. `/clear`
2. `/kapelle:<next-stage> <slug>`
```
