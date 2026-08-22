---
name: amend
description: >
  Add the next business or technical requirement as one new vertical slice, or revise the active
  slice, while preserving already working implementation.
---

# Skill: amend

Read [`../../references/developer-questions.md`](../../references/developer-questions.md) before
asking for input and
[`../../references/progressive-artifacts.md`](../../references/progressive-artifacts.md) before
promoting or detailing a use case.
Follow [`../../references/script-execution.md`](../../references/script-execution.md) for every
bundled Python helper and shell inspection command.

## Mandatory command shape

- One Kapelle helper or inspection tool call is one direct executable invocation.
- Use absolute paths from the project-root session. Never add `cd`, shell operators, redirection,
  substitutions, loops, conditionals, background execution, polling, or scratchpads.
- Read stdout, stderr, and exit status from the tool result. Never append `echo`, `wc`, or another
  diagnostic command.
- Never run Git, including through `rtk proxy`, another wrapper, or a subagent. Use native
  Read/Glob/Search on the current worktree.

Invoke:

```text
/kapelle:amend <slug> "<feedback or changed requirement>"
```

## Protocol

1. Read the current `spec.md`, `design.md`, `tasks.md`, relevant implementation, and verification
   result if present. Classify the request as a next feature increment, active-slice revision,
   implementation defect, or documentation-only correction.
2. Explain the observable impact and at most three real options with trade-offs. Ask one concise
   question only when the developer's choice materially changes behavior.
3. For a next increment, first inspect how the existing walking skeleton behaves in code. Promote
   only the developer-requested capability from the high-level use-case map into committed behavior.
   Detail just that use case in `specs/` when the trigger applies, update the high-level system
   design, and add one smallest coherent vertical slice to `tasks.md`. Do not detail, redesign, or
   decompose the remaining candidate map.
4. Update `design/domain-model.md` when the slice adds or changes aggregate behavior, invariants,
   lifecycle/status transitions, events, ownership, or persistence mapping. Update contracts,
   aspect design, sequences, or ADRs only when their explicit trigger applies. If new detail
   contradicts the high-level specification or system design, propose the smallest corresponding
   correction rather than hiding the conflict.
5. For an active-slice revision, update only affected sections and work. Fingerprints make the
   `plan`, verification, and final approvals stale; do not build a separate revision graph.
6. Use immutable `_kapelle/changes/` history only when the amendment follows PASS verification,
   changes authorization/money/destructive data/public contracts/migrations, or the developer asks
   for an audit trail. When used, validate every machine record against the applicable
   `change-request`, `change-revision`, `change-state`, `artifact-state`, or `reconciliation`
   schema before it affects routing:

```text
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate_json.py" "<absolute-record-path>" "${CLAUDE_PLUGIN_ROOT}/dispatcher/<schema>.schema.json"
```
7. Refresh architecture guidance only when affected modules, entrypoints, paths, or architectural
   decisions changed. Reuse it for implementation-only corrections.
8. Use at most one bounded read-only subagent burst when a promoted slice crosses unfamiliar
   backend/frontend/worker/integration boundaries. Use one critic correction pass only for high
   risk or a material contradiction. The main agent integrates and writes the documents.
9. Preserve already correct implementation. Add or reopen only the smallest workstream needed. Do
   not restart the feature, rewrite the base slice, or regenerate unrelated documents.
10. Validate the progressive package:

```text
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate_progressive_docs.py" "${CLAUDE_PROJECT_DIR}/docs/features/<slug>"
```

    Documentation-only corrections that do not change plan meaning may return directly to status.
    Implementation defects return to `/kapelle:implement`. Behavior/design changes require:

```text
/kapelle:start <slug> --approve
```

11. Rebuild and validate `STATUS.md`. Never fabricate prior approval/validation evidence and never
   run git operations.

Use the standard handoff block and standalone developer-question contract.
