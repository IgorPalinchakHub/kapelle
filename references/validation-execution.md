# Development validation execution

Kapelle separates planning validation from permission to execute project commands. Tests, static
analysis, linters, builds, and other project-defined checks are never silently treated as passed.

## Policy

Read `validation.development_policy` from project config. A command-line override on
`/kapelle:implement` applies only to that invocation:

```text
--validation=ask | --validation=allow | --validation=skip
```

The effective policy is:

- `ask` (default): show one validation batch and require an explicit decision;
- `allow`: execute the planned batch without another validation prompt;
- `skip`: execute no project validation commands and record deferred validation.

The validation decision is independent of implementation-plan approval.

## Validation batch

Before execution, show:

- task id and validation purpose;
- exact commands;
- command kind: `tests`, `static-analysis`, `lint`, `build`, or `other`;
- scope, such as focused files, module, or full project;
- whether each check is required by the task Definition of Done.

Under `ask`, accept:

- `run-all`;
- `run-selected`, naming the approved commands;
- `developer-verified`, with an explicit statement of what passed;
- `skip-all`.

Silence is not permission. Do not replace a skipped command with a different command unless the
replacement is shown and approved.

## Cancellation and evidence

If the user cancels a running command, stop it when the host supports cancellation. Do not
automatically retry it. Record every command as `passed`, `failed`, `skipped`, or `cancelled` using
`dispatcher/validation-decision.schema.json`.

Evidence includes exact current input fingerprints for the human package and coordination graphs,
plus fingerprints of the implementation files actually validated. Task-plan status fields are
excluded from its structural fingerprint so recording a validation result does not invalidate
itself. `files_hint` must enumerate the task's complete actual implementation inventory; a broad
directory is acceptable only when the recorded fingerprints enumerate every changed descendant.
Documentation convergence must equal the union of all completed-task implementation inventories.
Any changed input or implementation file makes the result stale.

Any required `skipped` or `cancelled` command makes the task `validation-deferred`. This state:

- permits continued development of dependency-ready tasks after explicit user choice;
- is not equivalent to `completed` or `PASS`;
- is selected first by a later `/kapelle:implement <slug> --validation=allow` run, which executes
  outstanding validation without repeating implementation;
- blocks final `/kapelle:verify --approve` until all required checks pass.

## Developer-attested verification

Kapelle accepts a developer's explicit report that verification was completed outside the current
agent session. The report does not need copied terminal output. It must state a passing result and
either cover the complete applicable batch or identify the selected checks that passed.

Use the `developer-attested` evidence source when Kapelle observed no output, `agent-observed` when
it did, and `mixed` when both sources contribute. Preserve the developer's statement in
`developer_confirmation`. A complete developer attestation may replace earlier deferred checks and
produce current `PASS`; a partial attestation leaves uncovered required checks deferred.

This is evidence, not final feature approval. Status and the verify summary must say when PASS is
developer-confirmed and command output was not captured by Kapelle.

For development readiness, a dependent task may consume code from a `validation-deferred`
dependency, but its plan and audit record must list that inherited validation risk. It may not
produce final contract, integration, verification, or completion evidence until the dependency
passes.

Optional checks may be skipped only when the task plan marks them optional and records why.
An omitted task-validation `required` field means `true`.

## Final gate

`/kapelle:verify` reports deferred required validation as `validation-deferred`.
`/kapelle:verify <slug> --approve` refuses with `Status: REFUSED-validation-incomplete` while
feature verification has a required check in `skipped`, `cancelled`, `failed`, or missing state
that is not covered by a later complete developer attestation.

Final readiness is deliberately not configurable: development may defer checks, but Kapelle never
claims the feature is validated or complete without current passing evidence. That evidence may be
agent-observed or explicitly developer-attested; its source always remains visible.
