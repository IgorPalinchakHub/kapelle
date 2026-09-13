# Human-controlled amendment lifecycle

Use `/kapelle:amend <slug> "<feedback>"` for requirement, architecture, contract, implementation,
test, or documentation changes discovered after planning begins.
Bundled helpers follow [`script-execution.md`](./script-execution.md).

## Protocol

1. Pause new implementation dispatch after the current atomic operation.
2. Only when amend's explicit audit trigger applies, use this machine layout; ordinary amendments
   update affected human documents without creating an audit graph:

```text
_kapelle/changes/<change-id>/
  request.json
  state.json
  reconciliation.json
  artifacts/<artifact-id>.json
  revisions/rNNN/revision.json
```

   Capture immutable revision evidence beside each `revision.json`.
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

- behavior, architecture, contracts and task changes: amend, then start --approve;
- production code and basic/critical early tests: implement;
- remaining tests, complete checks and as-built documents/diagrams: verify.

8. Update canonical human documents in place. Keep history internal.
9. Recompute approvals/evidence only from actual current results. Never fabricate lost evidence or
   automatically revert code.
10. Before any record affects routing, use validate_json.py via the invoking amend skill's
    command and resolved paths.
    Use its exact dispatcher schema: `change-request`, `change-state`, `change-revision`,
    `artifact-state`, or `reconciliation`. Structural validity does not imply route approval;
    semantic freshness, fingerprints, and explicit human approval remain separate gates.

Kapelle performs no git operations. Rejection or unexplained drift leaves the amendment blocked.
