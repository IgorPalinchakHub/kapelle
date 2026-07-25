# Agent Orchestration

Kapelle agents are explicit execution roles, not frontmatter metadata. A skill that needs an
isolated role must dispatch it in its protocol.

## Dispatch contract

1. Use the plugin-namespaced agent type `kapelle:<agent>`.
2. Resolve the role's provider-neutral execution profile from `dispatcher/role-profiles.json`.
   Apply a concrete model or effort only when the project config binds it
   (`providers.<provider>.roles.<agent>` / `providers.<provider>.stages.<stage>`); otherwise
   inherit the session default. Core definitions never pin a provider model.
3. Pass the feature slug, task id when applicable, required artifact paths, and the expected typed
   result. Let the agent read files directly; do not paste entire artifacts into its prompt.
4. Keep read-only analysis agents in fresh context.
5. If the named agent is unavailable, dispatch a general-purpose subagent with the same role,
   constraints, and output contract.
6. If subagents are unavailable, run the role inline and record `execution: inline-fallback`.
7. Never treat a custom `agents:` field in `SKILL.md` frontmatter as executable orchestration.
8. A bounded role gets one run and one terminal collection. Do not repeatedly status-ping it. If
   its budget is exhausted, stop/cancel that run before inline fallback; never execute both
   concurrently. A required project architecture-rules capability has no inline substitute.

## Core roles

| Agent | Purpose | Side effects |
|---|---|---|
| `business-analyst` | Separate current behavior, requested outcomes, rules, and scenarios | none |
| `explorer` | Map repository structure and precedents | none |
| `critic` | Find specification or design inconsistencies | none |
| `devils-advocate` | Find ambiguity and failure modes | none |
| `implementation-planner` | Produce an approval-ready project-aware plan | plan artifact only |
| `change-reconciler` | Classify existing work against a new change revision | none |
| `test-author` | Author base functional tests before implementation or unit tests after it | tests and test fixtures |
| `implementer` | Execute approved production-code plans | project files, excluding unit tests |
| `reviewer` | Return an independent structured verdict | none |

Project-specific skills and agents remain native project capabilities. Kapelle agents coordinate
generic SDLC roles and must apply the selected project capability and guidance rather than replace
them.

For each feature aspect or implementation task, the host semantically discovers applicable project
skills and subagents from their native descriptions. A selected project subagent may discover and
delegate to narrower project skills/subagents. Kapelle records these selections but never turns
them into a routing registry.

Every project must also provide a semantically discoverable subagent that can return scoped
architecture rules according to [`architecture-guidance.md`](./architecture-guidance.md). This is a
project capability, not a bundled Kapelle role, and its name is not fixed.

## Agent Teams

Sequential execution is the default. An Agent Team is allowed only for production tasks in
`implement` when all of
these are true:

- `.claude/kapelle.config.json` sets `implementation.mode` to `agent-team`;
- Claude Code Agent Teams are available at runtime;
- the user explicitly approves creating the team;
- at least two dependency-ready tasks have non-overlapping `files_hint`;
- `implementation.max_parallel_agents` is greater than one.

The team lead owns dependency ordering, task assignment, and result collection. Teammates use the
same typed contracts as sequential execution. Agent Teams do not imply worktree isolation; Kapelle
does not create branches or worktrees. Tasks with missing or overlapping file ownership remain
sequential.

If any precondition fails, report the reason and fall back to sequential execution. Do not invoke or
generate an unofficial `Workflow` tool.
