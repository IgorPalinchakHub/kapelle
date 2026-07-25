# Human-controlled implementation contract

Kapelle separates production implementation from test-authoring phases:

```text
APPROVED CONTRACTS
  -> BASE FUNCTIONAL TESTS
  -> PRODUCTION IMPLEMENTATION
  -> ALL UNIT TESTS
  -> COMPLETE VERIFICATION
```

The intentional timing rule is strict: `/kapelle:implement` never authors unit tests. Unit tests
are planned and written in one post-implementation `/kapelle:unit-tests` phase.

## Production task lifecycle

```text
UNDERSTAND -> SELECT-CAPABILITY -> GUIDANCE
-> PLAN -> APPROVE -> IMPLEMENT -> REVIEW -> SUMMARIZE
```

For every dependency-ready task:

1. Read approved business, design, contract, task, and base-functional-test artifacts.
   Read `_kapelle/surface-plan.json` so backend, frontend, data, worker, and integration aspects
   remain coordinated.
2. Discover native project skills/subagents semantically.
3. Obtain scoped architecture rules from the project-provided architecture-rules subagent.
4. Persist a fingerprinted implementation plan. Apply risk-based approval and bounded retries.
5. Dispatch the implementer for production code only.
6. Run fresh review where task risk requires it.
7. Optionally run existing focused base functional tests under `ask | allow | skip`.
8. Record `implemented-unverified`, changed files, observable behavior, deviations, and risks.

If planning or implementation needs developer input, the coordinator must translate the internal
finding using `references/developer-questions.md`. Never forward planner/reviewer prose, artifact
references, task/blocker ids, or DoD wording as the question.

`task`, `workstream`, and `none` checkpoints control how often control returns to the developer.
They do not weaken amendment, verification, or final approval gates.

## Deferred validation

During implementation, a skipped or cancelled focused check remains `validation-deferred`; it is
never PASS. Full unit, functional, integration, contract, static-analysis, lint, and build
verification belongs to `/kapelle:unit-tests` and `/kapelle:verify`.

## Amendments

Developer feedback that changes business behavior, architecture, contracts, or approved task
ownership pauses remaining work and routes through `/kapelle:amend`. The reconciler versions the
change, invalidates dependent evidence, and selects the earliest necessary stage.

## Execution modes and limits

Sequential mode is the default. Agent-team mode may parallelize only approved, dependency-ready
production tasks with explicit pairwise-disjoint ownership, runtime support, configuration, and
developer approval. Edit-attempt and agent-run caps always apply.

Kapelle never creates worktrees, branches, commits, pull requests, or unofficial workflow tools.
