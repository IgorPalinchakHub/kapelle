# Kapelle Runtime Instructions

When a Kapelle skill runs, behave as a gated SDLC stage or utility.

## Invariants

1. Artifact is state. Read stage inputs from disk; write durable state under `docs/features/<slug>/`.
2. Missing inputs cause refusal, not guessing. Emit `Status: REFUSED-missing-input` and name the prior stage.
3. Stage -> native project capability -> guidance/tools/code is one-way. Project skills never invoke stages.
4. Code-writing goes through the dispatcher and native project skill/subagent discovery. Selected
   project subagents are encouraged to discover narrower native capabilities.
5. Agent roles are dispatched explicitly by skill protocols; custom `agents:` frontmatter is never
   treated as executable configuration.
6. Sequential plan-first execution is the default. Select test strategy from task evidence; strict
   TDD is not universal. Agent Teams require configuration, runtime support, safe file partitioning,
   and explicit user approval.
7. Required approval is explicit. Silence is not approval.
8. Edit attempts and agent runs are bounded by project configuration.
9. Project guidance is provider-neutral. A semantically discovered project subagent must return
   scoped architecture rules for design and implementation; Kapelle never prescribes its name,
   storage, rule codes, tools, or provider.
10. Existing-feature changes capture a baseline and approved impact route before canonical artifact
    edits. Refactors preserve observable behavior; behavior changes are enhancements.
11. Requirement or architecture amendments pause all active implementation, create an immutable
    revision, invalidate downstream artifacts, reconcile tasks, and require approval before resume.
12. Implementation plans are executable only when their revision and `based_on` fingerprints match.
13. Skips are explicit and confirmed.
14. No git operations are performed by the harness.
15. Project-specific behavior belongs in native project capabilities, not in core stages.
16. Multi-aspect features use `surface-plan.json` for dependencies, shared contracts, and integration
    checks; it contains no skill or agent routing.
17. Execution depth reduces duplicate subagent runs but never weakens artifacts, architecture rules,
    acceptance-criteria coverage, or validation.

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
