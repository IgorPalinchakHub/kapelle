---
name: contracts
description: >
  Generate interface contracts through native project capabilities for a feature slug.
---

# Skill: contracts

Follow [`../../references/script-execution.md`](../../references/script-execution.md) for every
bundled Python helper.

Follow [`../../references/utility-contract.md`](../../references/utility-contract.md).
Use the trigger and boundary rules in
[`../../references/progressive-artifacts.md`](../../references/progressive-artifacts.md).

## Inputs

- Gate: `docs/features/<slug>/design.md`.
- `spec.md`, `design.md`, and optional `sequences.md` or coordination graphs when they already
  exist.
- Native project capabilities and project instructions.

## Protocol

1. Refuse if `design.md` or required interface declarations are missing. Data/schema impact must be
   explicit in `design.md`, including a confirmed no-schema-change result.
2. Describe the smallest durable contract artifact needed to make a public or cross-component
   boundary unambiguous. Do not require `_kapelle/surface-plan.json` for a normal lightweight slice.
3. When an optional coordination graph exists, validate and use it as supporting evidence rather
   than as a gate.
4. Let Claude Code select the applicable native project capability semantically.
5. Ask that capability to obtain project guidance through any available project mechanism.
6. Write human contracts under `docs/features/<slug>/contracts/`. Generate project code only during
   `/kapelle:implement`; this utility documents the boundary.
7. Check the contract against `spec.md`, the shared data model, runtime flows, and named
   provider/consumer boundaries. Report unknown consumers instead of inventing them.
8. Validate the package, rebuild status, and validate state as three separate commands:

```text
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate_progressive_docs.py" "${CLAUDE_PROJECT_DIR}/docs/features/<slug>"
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/build_feature_status.py" "${CLAUDE_PROJECT_DIR}/docs/features/<slug>"
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate_feature_state.py" "${CLAUDE_PROJECT_DIR}/docs/features/<slug>"
```

10. A changed contract or design requires `/kapelle:start <slug> --approve`; otherwise return to
   `/kapelle:status <slug>`.

## Anti-patterns

- Hardcoding contract kinds, skill names, agent names, providers, or commands in Kapelle core.
- Finalizing a contract that contradicts the shared data model.
