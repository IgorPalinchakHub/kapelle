# Agent Orchestration

Kapelle agents are explicit execution roles, not frontmatter metadata. A skill that needs an
isolated role must dispatch it in its protocol.

## Dispatch contract

1. Use the plugin-namespaced agent type `kapelle:<agent>`.
2. Pass the feature slug, task id when applicable, required artifact paths, and the expected typed
   result. Let the agent read files directly; do not paste entire artifacts into its prompt.
3. Keep read-only analysis agents in fresh context.
4. If the named agent is unavailable, dispatch a general-purpose subagent with the same role,
   constraints, and output contract.
5. If subagents are unavailable, run the role inline and record `execution: inline-fallback`.
6. Never treat a custom `agents:` field in `SKILL.md` frontmatter as executable orchestration.

## Core roles

| Agent | Purpose | Side effects |
|---|---|---|
| `explorer` | Map repository structure and precedents | none |
| `critic` | Find specification or design inconsistencies | none |
| `devils-advocate` | Find ambiguity and failure modes | none |
| `implementation-planner` | Produce an approval-ready project-aware plan | plan artifact only |
| `change-reconciler` | Classify existing work against a new change revision | none |
| `test-author` | Select and execute the task's test strategy | tests and test fixtures |
| `implementer` | Execute the approved plan and validate each slice | project files and tests |
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

Sequential execution is the default. An Agent Team is allowed only for `implement` when all of
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
