# Implementation dispatcher

The dispatcher executes dependency-ordered tasks without maintaining a second capability registry.
It uses explicit Kapelle execution roles while Claude Code selects project skills, agents, and tools
through native discovery and their descriptions.

## Protocol

For each pending task:

1. Validate it against `task-context.schema.json`.
2. Read the referenced feature artifacts and relevant repository context from disk.
3. Validate `surface-plan.json`, the complete dependency graph, aspect dependencies, shared
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
10. Execute `execution-contract.md`: classify the task, select execution depth and a test strategy,
   run planner/reviewer roles inline only when the lean-depth contract permits it, otherwise dispatch
   `kapelle:implementation-planner`, enforce the approval policy, then dispatch
   `kapelle:test-author`, `kapelle:implementer`, and `kapelle:reviewer`.
11. Use sequential mode by default. Use an Agent Team only when configured, available, explicitly
    approved, and safe for the ready task batch.
12. Enforce edit-attempt and agent-run caps. Stop and block rather than iterating without bound.
13. Run the project capability's validation commands.
14. Mark the task completed only when its Definition of Done, required review policy, and validation pass.
15. Append task, capability, architecture guidance, general guidance, strategy, plan, approval, implementation, review,
    validation, and actual available usage telemetry to feature audit files.
16. If requirements, architecture, contracts, or constraints change during implementation, stop
    all change-related dispatch, checkpoint state, and enter the revision lifecycle. Do not resume
    until `/kapelle:resume` passes fingerprint and reconciliation gates.

## Status lines

- `Status: CAPABILITY-SELECTED | skill: <name> | agent: <name-or-default>`
- `Status: EXECUTION-MODE | mode: sequential|agent-team | reason: <selection>`
- `Status: TEST-STRATEGY | task: <id> | class: <class> | strategy: <strategy>`
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
- `Status: IMPLEMENTED-and-validated | task: <id>`

## Invariants

- **No runtime pack registry** — distribution metadata is never read during implementation.
- **No provider coupling** — Kapelle does not invoke a named CLI or prescribe rule storage.
- **Native discovery** — project capability descriptions are the selection mechanism.
- **Scoped architecture law** — a project subagent supplies applicable rules for each design/task scope.
- **Explicit roles** — agent execution comes from protocol dispatch, never custom frontmatter.
- **Plan first** — code follows a validated strategy and durable plan.
- **Adaptive verification** — TDD, characterization, scenarios, contracts, and validation are
  chosen from task evidence.
- **Bounded execution** — retry and agent-run caps prevent runaway loops.
- **Revision safety** — changed requirements pause execution; fingerprints and reconciliation gate
  resume.
- **Safe concurrency** — unknown or overlapping file ownership remains sequential.
- **Official mechanisms only** — no generated or assumed `Workflow` tool.
- **Artifact is state** — tasks and handoffs remain durable on disk.
- **No git ownership** — Kapelle never runs git operations.
