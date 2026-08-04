# Kapelle Runtime Instructions

When a Kapelle skill runs, behave as a gated SDLC stage or utility.

## Invariants

1. Human-readable feature artifacts are durable state. Derived execution state and evidence live
   under `docs/features/<slug>/_kapelle/` and may be rebuilt without fabricating lost evidence.
2. Missing inputs cause refusal, not guessing. Emit `Status: REFUSED-missing-input` and name the prior stage.
3. Stage -> native project capability -> guidance/tools/code is one-way. Project skills never invoke stages.
4. Before code-writing, discover relevant native project skills, instructions, and architecture
   guidance once per workstream. Reuse them until scope changes; a project subagent is optional.
5. Agent roles are dispatched explicitly by skill protocols; custom `agents:` frontmatter is never
   treated as executable configuration.
6. Sequential plan-first execution is the default. Select test strategy from task evidence; strict
   TDD is not universal. Agent Teams require configuration, runtime support, safe file partitioning,
   stable approved contracts, and explicit user approval. Do not use a team for the first tightly
   coupled walking skeleton.
7. Required approval is explicit. Silence is not approval.
8. Retry loops and optional agent runs are bounded. The main agent owns normal planning and
   implementation; explorer, critic, reviewer, and Agent Teams are triggered by uncertainty or risk.
9. Project guidance is provider-neutral. Read the narrowest relevant rules for the affected scope,
   persist their evidence, and refresh only when the scope changes.
10. New development starts with a bounded high-level feature/specification and system-design map,
    then the smallest production-shaped end-to-end walking skeleton. Candidate capabilities remain
    hypotheses until the developer explicitly promotes one.
11. Each promoted business or technical requirement becomes one smallest coherent vertical slice.
    It updates only affected artifacts, invalidates downstream evidence, and requires renewed slice
    approval before code resumes.
12. Implementation starts only from a current approved slice whose fingerprints match `spec.md`,
    `design.md`, `tasks.md`, and architecture guidance.
13. Skips are explicit and confirmed.
14. No git operations are performed by the harness.
15. Project-specific behavior belongs in native project capabilities, not in core stages.
16. Create machine coordination graphs only when they add safety for genuine parallel ownership,
    shared contracts, migrations, or complex dependencies. They are not routine stage outputs.
17. Human documents evolve with working code: `spec.md` and `design.md` map the known feature at
    high level while clearly separating committed behavior from candidates; `tasks.md` contains
    only the implemented base and active approved slice. Detail a use case, domain model, contract,
    aspect, ADR, or diagram only when its explicit trigger makes it independently useful.
18. `docs/architecture-map.md` is a shared baseline. Feature worktree drift is recorded under the
    feature `_context/` directory and never triggers an automatic shared-map rewrite.
19. Development validation commands use an explicit `ask | allow | skip` policy. Skipped or
    cancelled required checks become `validation-deferred` unless the developer later explicitly
    confirms that the complete applicable verification passed outside Kapelle. Developer-attested
    PASS is accepted for ship readiness but is always labeled as attested, never agent-observed.
20. `STATUS.md` is the generated human entry point. Every backbone stage refreshes it; missing or
    invalid `_kapelle/` state triggers recovery and the minimal safe next route.
21. Product `spec.md` and technical `design.md` converge with the as-built implementation during
    `/kapelle:verify`, before final approval.
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
26. Bundled Python helpers and allowlisted project-native read-only CLIs run as one direct command
    per tool call. The executable is the first token; consume the tool result directly. Never add
    `cd`, environment assignments, redirection, scratchpads, exit-code `echo`, subshells, shell
    wrappers, `;`, `&&`, `||`, pipes, background execution, or shell polling loops.
27. Shell inspection uses the tool's working directory and one native command, never `cd` plus a
    `for`/`while`/`if` shell program. Prefer Read, Glob, and Search for current-worktree evidence.
    Kapelle does not inspect branches, commits, or repository objects with Git.

## Handoff

Every backbone stage refreshes `STATUS.md` and ends its chat response with:

```md
## <stage> — <slug>

**What I did**
- ...

**Review before continuing**
- ...

**Run next**
`/kapelle:<next-stage> <slug>`
```
