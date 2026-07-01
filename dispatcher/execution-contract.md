# Adaptive implementation contract

Kapelle uses a plan-first lifecycle. Testing is selected from task risk and evidence; strict TDD is
one strategy, not a global requirement.

```text
UNDERSTAND -> CLASSIFY -> SELECT-CAPABILITY -> GUIDANCE
-> TEST-STRATEGY -> PLAN -> APPROVE
-> IMPLEMENT -> REVIEW -> VALIDATE
```

## 1. Understand and classify

Read the task, acceptance criteria, feature artifacts, project instructions, applicable guidance,
and repository precedents. Extract business invariants and unresolved assumptions before choosing a
test strategy.

Read `surface-plan.json` and the task's aspect ids. Semantically discover project skills and
subagents for those aspects, then dispatch the project's architecture-rules subagent for the
specific modules, entrypoints, and candidate paths. Architecture evidence is mandatory and must
match `architecture-guidance.schema.json`.

Select execution depth using `references/execution-depth.md`. Depth controls role dispatch cost, not
artifact or validation requirements.

Classify the task:

| Task class | Default strategy |
|---|---|
| `bugfix` or `isolated-behavior` | `strict-tdd` |
| `legacy-change` or behavior-preserving `refactor` | `characterization` |
| `complex-domain` | `scenario-first` |
| `contract-boundary` | `contract-first` |
| `migration-config` | `validation-first` |
| `non-code` | `validation-only` |

The selected project capability may override the default with evidence. Validate the result against
`test-strategy.schema.json`.

## 2. Plan and approve

Run the implementation-planner role after capability and guidance selection. At `lean` depth for a
low-risk task, the coordinator may execute this role inline and record
`execution: inline-lean`; otherwise dispatch `kapelle:implementation-planner`. The plan must contain:

- task scope and non-goals;
- business invariants and scenario matrix;
- selected project capability and applicable guidance;
- scoped architecture rules and aspect/contract dependencies;
- files expected to change;
- ordered implementation slices;
- test strategy and validation commands;
- risks, rollback or recovery notes, and unresolved questions.

Write the plan to `docs/features/<slug>/_audit/plans/<task-id>.md`.

Apply `implementation.approval_policy`:

- `always`: require explicit approval for every task;
- `risk-based`: require approval for `complex-domain`, public contract, authorization/security,
  destructive migration, ambiguous invariant, or cross-module changes;
- `never`: print and record the plan, then continue without waiting.

On requested changes, revise the plan. On rejection, block the task. Never interpret silence as
approval when approval is required.

## 3. Execute the selected strategy

- `strict-tdd`: write and classify RED, then implement GREEN and refactor.
- `characterization`: first capture current behavior with passing tests; add a failing expectation
  only for the intended behavior change, then implement.
- `scenario-first`: validate the invariant/scenario matrix, implement one scenario slice at a time,
  and test observable behavior at the most stable boundary.
- `contract-first`: establish the contract or consumer-facing assertion first, then implement both
  sides and validate compatibility.
- `validation-first`: define deterministic pre/post checks before editing; implement and run them.
- `validation-only`: make no production-code claim; verify the requested artifact or operation.

Do not require `GOOD_RED` outside `strict-tdd`. Every strategy still requires executable or
inspectable evidence tied to acceptance criteria.

## 4. Review, validate, and retry

Dispatch `kapelle:reviewer` in fresh read-only context for every risk-triggered task. For a
low-risk `lean` task, record `review: deferred-to-feature-review` and run focused project
validation; `/kapelle:review` remains mandatory before ship. Then run project validation commands.

An attempt is one implementation or corrective edit cycle followed by focused validation.
`implementation.max_task_attempts` is a hard cap. Do not count read-only planning or review as edit
attempts. When the cap is reached:

1. stop editing;
2. preserve the latest evidence;
3. mark the task `BLOCKED`;
4. ask the user to revise the plan, acceptance criteria, or constraints.

Never weaken tests, invariants, security, or acceptance criteria to fit the attempt limit.

## 5. Execution modes

Sequential mode is the default. Agent-team mode may parallelize only already-approved,
dependency-ready tasks with explicit, pairwise-disjoint `files_hint`. Each task still follows this
full contract. Agent Teams require runtime availability and explicit user approval.

Kapelle does not create worktrees, branches, commits, pull requests, or unofficial `Workflow`
scripts.

## 6. Evidence and telemetry

Validate role results against `execution-verdict.schema.json`. Append execution events matching
`execution-telemetry.schema.json` to
`docs/features/<slug>/_audit/implementation-telemetry.jsonl`.

Record actual host-provided token usage when available. Never estimate token usage or monetary cost.
Enforce `max_agent_runs_per_task` as a cost guard regardless of whether usage metadata is available.
