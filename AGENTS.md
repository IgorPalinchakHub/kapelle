# Kapelle Runtime Instructions

When a Kapelle skill runs, behave as a gated SDLC stage or utility.

## Invariants

1. Human-readable feature artifacts are durable state. Derived execution state and evidence live
   under `docs/features/<slug>/_kapelle/` and may be rebuilt without fabricating lost evidence.
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
16. Multi-aspect features use `_kapelle/surface-plan.json` for dependencies, shared contracts, and integration
    checks; it contains no skill or agent routing.
17. Execution depth reduces duplicate subagent runs but never weakens artifacts, architecture rules,
    acceptance-criteria coverage, or validation.
18. `docs/architecture-map.md` is a shared baseline. Feature worktree drift is recorded under the
    feature `_context/` directory and never triggers an automatic shared-map rewrite.
19. Development validation commands use an explicit `ask | allow | skip` policy. Skipped or
    cancelled required checks become `validation-deferred`; they are never reported as `PASS` and
    block ship readiness.
20. `STATUS.md` is the generated human entry point. Every backbone stage refreshes it; missing or
    invalid `_kapelle/` state triggers recovery and the minimal safe next route.
21. Product `spec.md` and technical `design.md` must converge with the as-built implementation
    before feature review and ship.
22. Existing-code reconstruction is documentation-only. It classifies material claims as
    `observed | inferred | declared | unknown`, fingerprints cited sources, distinguishes as-built
    architecture from rules and deviations, and never routes to planning, implementation, test, or
    release stages. `documented` never means ship-ready.
23. Only deterministic Kapelle scripts write review-gate JSON, `_kapelle/manifest.json`,
    `_kapelle/state.json`, and `STATUS.md`. Skills and subagents never hand-maintain those files.
24. Every machine JSON/JSONL artifact is structurally checked by Kapelle's fail-closed schema
    validator before it affects routing or stage completion. Stage validators add only semantic,
    cross-file, graph, filesystem, freshness, and readiness checks.
25. Developer questions are standalone and concise: explain the intended change, why the decision
    matters, and the real options with trade-offs. Never forward raw subagent output or require the
    developer to decode task, blocker, DoD, gate, acceptance-criterion, or artifact identifiers.

## Handoff

Every backbone stage refreshes `STATUS.md` and ends its chat response with:

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
