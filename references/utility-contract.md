# Optional utility contract

Kapelle utilities enrich durable human documentation without creating another workflow.
Bundled helpers follow [`script-execution.md`](./script-execution.md).

1. Read only the named feature or project artifacts and refuse missing inputs instead of guessing.
2. Write the smallest independently useful human artifact. Utilities never hand-edit
   `_kapelle/manifest.json`, `_kapelle/state.json`, review gates, or `STATUS.md`.
3. After a feature artifact changes, run as separate commands:

```text
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/build_feature_status.py" "${CLAUDE_PROJECT_DIR}/docs/features/<slug>"
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate_feature_state.py" "${CLAUDE_PROJECT_DIR}/docs/features/<slug>"
```
4. A change to `spec.md`, `specs/`, `design.md`, `design/`, `tasks.md`, `sequences.md`, an ADR, or a
   durable contract invalidates the current-slice approval. The next command is
   `/kapelle:start <slug> --approve`.
5. When no approved artifact changed, return to `/kapelle:status <slug>`.
6. Utilities never chain into each other and never run git operations.

Output uses `Status: DONE | utility: <name> | produced: <paths>` and the readable handoff format in
[`handoff.md`](./handoff.md).
