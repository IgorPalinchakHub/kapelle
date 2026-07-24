# Human-controlled amendment lifecycle

Use `/kapelle:amend <slug> "<feedback>"` for requirement, architecture, contract, implementation,
test, or documentation changes discovered after planning begins.

## Protocol

1. Pause new implementation dispatch after the current atomic operation.
2. Capture immutable revision evidence under `_kapelle/changes/<change-id>/revisions/rNNN/`.
3. Classify impact across specification, design, contracts, functional tests, tasks, production
   code, unit tests, verification, diagrams, and release evidence.
4. Fingerprint affected artifacts and propagate stale state through
   `dispatcher/artifact-dependencies.json`.
5. Reconcile each existing task as:

```text
keep | revalidate | rework | supersede | revert-required
```

6. Show the minimal route and require explicit approval before canonical edits.
7. Use only current pipeline stages:

- business behavior: `spec`;
- architecture/contracts: `design`;
- task/test planning: `plan`;
- production code: `implement`;
- unit coverage: `unit-tests`;
- complete checks: `verify`;
- as-built documents/diagrams: `finalize`.

8. Update canonical human documents in place. Keep history internal.
9. Recompute approvals/evidence only from actual current results. Never fabricate lost evidence or
   automatically revert code.

Kapelle performs no git operations. Rejection or unexplained drift leaves the amendment blocked.
