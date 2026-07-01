---
name: implement
model: inherit
effort: high
description: >
  Plan and implement a feature's dependency-ordered tasks using adaptive test strategies,
  risk-based approval, bounded retries, native project capabilities, provider-neutral guidance,
  independent review, and project validation. Invoke as /kapelle:implement <slug>.
---

# Skill: implement

`implement` is the generic plan-first implementation engine. Sequential execution is the default.
Strict TDD is selected only when it fits the task.

## Inputs

- Gate: `docs/features/<slug>/tasks.json`.
- Required coordination input: `docs/features/<slug>/surface-plan.json`.
- Optional change context: `docs/features/<slug>/changes/<change-id>/change.json` when invoked with
  `--change=<change-id>`.
- Feature artifacts under `docs/features/<slug>/`.
- Project instructions and native `.claude/skills`, `.claude/agents`, `.claude/rules`.
- Any user/project plugins, MCP tools, or provider capabilities already available to Claude Code.
- Execution contract: [`../../dispatcher/execution-contract.md`](../../dispatcher/execution-contract.md).
- Agent dispatch contract: [`../../references/agent-orchestration.md`](../../references/agent-orchestration.md).
- Execution depth: [`../../references/execution-depth.md`](../../references/execution-depth.md).
- Architecture guidance:
  [`../../references/architecture-guidance.md`](../../references/architecture-guidance.md).

## Protocol

1. Refuse if `tasks.json` is missing; run `tasks` first.
2. Validate `surface-plan.json` against `dispatcher/surface-plan.schema.json` and tasks against
   `dispatcher/task-context.schema.json`.
   For a change request, also validate that `implement` is in its approved route and restrict tasks
   to the approved change delta.
3. For a change request, refuse unless `active-state.state` is `running`. Before every task,
   recompute its plan's `based_on` fingerprints and require the current revision. A requirement or
   architecture amendment expressed during implementation triggers the safe-pause revision path;
   stop all further implementation dispatch.
4. Validate that dependencies exist, the graph is acyclic, every task aspect exists, provider
   contract tasks precede consumers, and integration checks have owner tasks. Compute
   dependency-ready batches.
5. Read implementation mode, approval policy, attempt and agent-run limits, and telemetry setting
   from project config.
6. Select Agent Team mode only when every precondition in the orchestration contract passes.
   Otherwise report the failed precondition and use sequential mode.
7. For every task, execute:
   `UNDERSTAND -> CLASSIFY -> SELECT-CAPABILITY -> GUIDANCE -> TEST-STRATEGY -> PLAN -> APPROVE
   -> IMPLEMENT -> REVIEW -> VALIDATE`.
   - select execution depth from feature size and task risk;
   - select project skills and subagents semantically from native descriptions for every declared
     task aspect; encourage the selected project subagent to discover narrower project capabilities;
   - semantically discover and dispatch the project's architecture-rules subagent for the task's
     aspects, modules, entrypoints, and candidate paths; validate and persist its scoped evidence;
   - request applicable guidance without naming or assuming a provider;
   - select and validate the test strategy; at `lean`, routine strategy selection may execute
     inline, while risk-triggered tasks dispatch `kapelle:test-author` in `strategy` mode;
   - persist a plan for every task; a low-risk `lean` task may execute the planner role inline,
     while risk-triggered tasks dispatch `kapelle:implementation-planner`;
   - apply the configured approval policy; never infer required approval;
   - dispatch `kapelle:test-author` in `execute` mode when the strategy creates tests or fixtures;
     skip this dispatch for `validation-only`;
   - dispatch `kapelle:implementer` with the approved plan and strategy;
   - dispatch `kapelle:reviewer` in fresh read-only context for risk-triggered tasks. Low-risk
     `lean` tasks may defer independent review to the mandatory feature-level `review` stage;
   - run project validation and require `PASS`.
8. Validate each role result against `dispatcher/execution-verdict.schema.json`.
9. Stop edit retries at `implementation.max_task_attempts` and all agent dispatches at
   `implementation.max_agent_runs_per_task`.
10. Append capability, architecture guidance, general guidance, strategy, plan, approval,
    implementation, review policy, and validation to
   `docs/features/<slug>/_audit/implementation.jsonl`.
11. When telemetry is enabled, append actual execution events to
    `_audit/implementation-telemetry.jsonl`; never estimate unavailable token or cost data.
12. Update task status only after Definition of Done, review, and validation pass.
13. Emit handoff to `/kapelle:review <slug>`.

## Definition of Done

- Every completed task has capability-selection and validation evidence.
- Every task has scoped architecture-rule evidence, a validated strategy, a durable plan, approval
  evidence when required, and a recorded review policy. Risk-triggered tasks have a per-task
  independent review verdict; all tasks remain subject to the feature-level review.
- Every aspect contract dependency and integration check is validated.
- Required guidance evidence exists when the project enables that policy.
- Retry and agent-run limits were respected.
- Parallel tasks have explicit, pairwise-disjoint file ownership.
- No runtime pack manifest, rule storage convention, CLI, or provider name was assumed.

## Anti-patterns

- Selecting project capabilities from a Kapelle routing table.
- Requiring one specific rule provider or command.
- Encoding search topics or rule codes in Kapelle core.
- Requiring strict TDD for every task.
- Writing code before business invariants, strategy, and plan are known.
- Continuing after a requirement or architecture amendment without creating a revision.
- Running a task whose plan revision or fingerprints are stale.
- Treating silence as approval.
- Continuing edits after the configured attempt limit.
- Estimating tokens or monetary cost when the host did not report usage.
- Treating `agents:` frontmatter as orchestration.
- Using Agent Teams without runtime support and explicit user approval.
- Parallelizing tasks with missing or overlapping `files_hint`.
- Invoking or generating an unofficial `Workflow` tool.
- Running git operations.
