---
name: implement
model: inherit
effort: high
description: >
  Execute a feature's dependency-ordered tasks through explicit test-author, implementer, and
  reviewer roles, native project capabilities, provider-neutral guidance, and project validation.
  Invoke as /kapelle:implement <slug>.
---

# Skill: implement

`implement` is the generic implementation engine. Sequential TDD is the default; an Agent Team is
an explicit, guarded optimization for independent tasks.

## Inputs

- Gate: `docs/features/<slug>/tasks.json`.
- Feature artifacts under `docs/features/<slug>/`.
- Project instructions and native `.claude/skills`, `.claude/agents`, `.claude/rules`.
- Any user/project plugins, MCP tools, or provider capabilities already available to Claude Code.
- Execution contract: [`../../dispatcher/execution-contract.md`](../../dispatcher/execution-contract.md).
- Agent dispatch contract: [`../../references/agent-orchestration.md`](../../references/agent-orchestration.md).

## Protocol

1. Refuse if `tasks.json` is missing; run `tasks` first.
2. Validate tasks against `dispatcher/task-context.schema.json`.
3. Validate that dependencies exist and the graph is acyclic; compute dependency-ready batches.
4. Read `implementation.mode` and `implementation.max_parallel_agents` from project config.
5. Select Agent Team mode only when every precondition in the orchestration contract passes.
   Otherwise report the failed precondition and use sequential mode.
6. For every task, execute:
   `SELECT-CAPABILITY -> GUIDANCE -> RED -> GREEN -> REFACTOR -> VERIFY -> GATE`.
   - select project capabilities semantically from native descriptions;
   - request applicable guidance without naming or assuming a provider;
   - dispatch `kapelle:test-author` and require `GOOD_RED` before production code;
   - dispatch `kapelle:implementer` with the selected capability, guidance, and RED evidence;
   - dispatch `kapelle:reviewer` in fresh read-only context;
   - run project validation and require `PASS`.
7. Validate each role result against `dispatcher/execution-verdict.schema.json`.
8. Append capability, guidance, RED, implementation, review, and validation evidence to
   `docs/features/<slug>/_audit/implementation.jsonl`.
9. Update task status only after Definition of Done, review, and validation pass.
10. Emit handoff to `/kapelle:review <slug>`.

## Definition of Done

- Every completed task has capability-selection and validation evidence.
- Every code task has a classified RED result and independent review verdict.
- Required guidance evidence exists when the project enables that policy.
- Parallel tasks have explicit, pairwise-disjoint file ownership.
- No runtime pack manifest, rule storage convention, CLI, or provider name was assumed.

## Anti-patterns

- Selecting project capabilities from a Kapelle routing table.
- Requiring one specific rule provider or command.
- Encoding search topics or rule codes in Kapelle core.
- Treating `agents:` frontmatter as orchestration.
- Using Agent Teams without runtime support and explicit user approval.
- Parallelizing tasks with missing or overlapping `files_hint`.
- Invoking or generating an unofficial `Workflow` tool.
- Running git operations.
