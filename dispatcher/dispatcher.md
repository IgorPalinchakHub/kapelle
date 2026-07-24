# Implementation dispatcher

The dispatcher executes dependency-ordered tasks without maintaining a second capability registry.
It uses explicit Kapelle execution roles while Claude Code selects project skills, agents, and tools
through native discovery and their descriptions.

## Protocol

For each pending task:

1. Validate the enclosing plan against `task-plan.schema.json`, rerun
   `scripts/validate_task_plan.py`, and validate the task against `task-context.schema.json`.
2. Read the referenced feature artifacts and relevant repository context from disk.
3. Validate `_kapelle/surface-plan.json`, the complete dependency graph, aspect dependencies, shared
   contract ordering, and integration-check ownership; compute dependency-ready batches.
4. Present the task intent, acceptance criteria, hints, and artifact paths to native project capabilities.
5. Let Claude Code select applicable project skills and subagents semantically for the task's
   declared aspects. Encourage selected project subagents to discover narrower native capabilities.
   Do not resolve names from a Kapelle manifest and do not parse a routing label.
6. Discover and dispatch the project's architecture-rules subagent for the actual task scope.
   Validate its result against `architecture-guidance.schema.json`; missing capability or blocking
   gaps stop planning and code-writing.
7. Before code, instruct the selected project capability to obtain applicable project guidance using any
   provider available in the project or user environment.
8. Accept provider-neutral guidance evidence:
   `{ status, guidance[], sources[], gaps[] }`. Kapelle does not know whether it came from CLI, MCP,
   files, APIs, project instructions, or another agent.
9. When `guidance_evidence` is `required`, stop if evidence is absent or reports unresolved blocking gaps.
   `optional` records available evidence without requiring a provider; `disabled` skips this check.
10. Execute `execution-contract.md`: plan the production task, enforce approval, dispatch
   `kapelle:implementer`, and dispatch `kapelle:reviewer` when risk requires it. Unit-test authoring
   is forbidden here; `kapelle:test-author` runs only in the separate base-functional-test and
   post-implementation unit-test stages.
11. Use sequential mode by default. Use an Agent Team only when configured, available, explicitly
    approved, and safe for the ready task batch.
12. Enforce edit-attempt and agent-run caps. Stop and block rather than iterating without bound.
13. Optionally run the existing focused base functional tests under
    `references/validation-execution.md`. Full unit, static-analysis, lint, and build batches are
    deferred to their explicit later stages.
14. Mark production work `implemented-unverified`; final completion comes only after unit tests and
    complete verification. A skipped/cancelled focused check remains visible deferred evidence.
15. A dependent task may become development-ready from a `validation-deferred` dependency only
    after the explicit skip/cancel decision is recorded. Propagate that risk into its plan; do not
    accept final contract or integration evidence until the dependency passes.
16. Persist task, capability, architecture guidance, strategy, plan, approval, implementation,
    review, and validation in `_kapelle/task-runs/<task-id>.json`; append only actual available usage
    telemetry to `_kapelle/telemetry/execution.jsonl`.
17. If requirements, architecture, contracts, or constraints change during implementation, stop
    all change-related dispatch, checkpoint state, and enter `/kapelle:amend`. Resume only after
    the amended route has current fingerprints, reconciled tasks, and explicit developer approval.

## Status lines

- `Status: CAPABILITY-SELECTED | skill: <name> | agent: <name-or-default>`
- `Status: EXECUTION-MODE | mode: sequential|agent-team | reason: <selection>`
- `Status: PLAN-READY | task: <id> | approval: required|not-required`
- `Status: PLAN-APPROVED | task: <id> | by: user|policy`
- `Status: ATTEMPT | task: <id> | edit: <n>/<max> | agent-runs: <n>/<max>`
- `Status: PAUSED-REVISION | change: <id> | task: <id> | reason: <amendment>`
- `Status: RECONCILING | change: <id> | revision: <n>`
- `Status: RESUMABLE | change: <id> | revision: <n>`
- `Status: GUIDANCE-READY | sources: <n> | gaps: <n>`
- `Status: ARCHITECTURE-GUIDANCE-READY | capability: <project-subagent> | rules: <n> | gaps: 0`
- `Status: REFUSED-missing-project-capability | capability: project architecture-rules subagent`
- `Status: BLOCKED-guidance | gaps: <descriptions>`
- `Status: IMPLEMENTED-unverified | task: <id>`

## Invariants

- **No runtime pack registry** — distribution metadata is never read during implementation.
- **No provider coupling** — Kapelle does not invoke a named CLI or prescribe rule storage.
- **Native discovery** — project capability descriptions are the selection mechanism.
- **Scoped architecture law** — a project subagent supplies applicable rules for each design/task scope.
- **Explicit roles** — agent execution comes from protocol dispatch, never custom frontmatter.
- **Plan first** — code follows a validated strategy and durable plan.
- **Explicit test timing** — base functional tests precede production code; unit tests follow all
  production implementation; complete verification follows unit tests.
- **Bounded execution** — retry and agent-run caps prevent runaway loops.
- **Revision safety** — changed requirements pause execution; fingerprints and reconciliation gate
  resume.
- **Safe concurrency** — unknown or overlapping file ownership remains sequential.
- **Official mechanisms only** — no generated or assumed `Workflow` tool.
- **Readable artifact state** — human documents remain durable; execution evidence stays under
  `_kapelle/`.
- **No git ownership** — Kapelle never runs git operations.
