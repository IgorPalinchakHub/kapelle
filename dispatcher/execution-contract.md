# Implementation execution contract

The implementation engine is provider-neutral and uses this fixed lifecycle per task:

```text
SELECT-CAPABILITY -> GUIDANCE -> RED -> GREEN -> REFACTOR -> VERIFY -> GATE
```

## Sequential mode

For each dependency-ready task:

1. Select the applicable native project skill or agent by its description.
2. Obtain provider-neutral guidance evidence when configured.
3. Dispatch `kapelle:test-author`; require a classified RED result.
4. Dispatch `kapelle:implementer` with the task, selected capability, guidance evidence, and RED
   result.
5. Dispatch `kapelle:reviewer` in fresh read-only context.
6. Run the project capability's validation commands.
7. Mark the task completed only when implementation, review, and validation all pass.

## RED classification

- `GOOD_RED`: the behavior required by an acceptance criterion is absent.
- `BAD_RED`: the test cannot run because the test itself is invalid; repair the test and rerun.
- `FALSE_PASS`: the test passes before implementation; strengthen it or prove existing coverage.
- `NON_RED`: the required environment is unavailable; block unless project policy explicitly
  permits that tier to remain unverified.

Production code must not be written until a `GOOD_RED` result exists, unless the task is explicitly
non-code or the project capability documents why test-first is inapplicable.

## Agent-team mode

Build dependency-ready batches from the task DAG. A batch may run in parallel only when every task
has explicit, pairwise-disjoint `files_hint`. Keep tasks with shared or unknown files in a
serialization lane. Each task still executes the full lifecycle above.

Agent-team mode requires runtime availability and explicit user approval. Fall back to sequential
mode without failing the feature when unavailable.

## Structured results

Every role returns an object matching `execution-verdict.schema.json`. Store results in
`docs/features/<slug>/_audit/implementation.jsonl`. Prose may accompany a result, but the dispatcher
branches only on structured fields.

## Ownership boundary

Kapelle does not create commits, branches, worktrees, pull requests, or provider queries. Project
capabilities own framework-specific implementation and validation. The user or another explicitly
installed capability owns version-control operations.
