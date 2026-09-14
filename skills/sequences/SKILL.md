---
name: sequences
description: >
  Enrich `design.md` with runtime and cross-aspect flows; create `sequences.md` only for genuinely
  complex feature flows.
---

# Skill: sequences

Follow [`../../references/script-execution.md`](../../references/script-execution.md) for every
bundled Python helper.

Enrich the technical specification with runtime flows and failure branches.


## Runtime paths

Plugin root: `${CLAUDE_PLUGIN_ROOT}`. Project root: `${CLAUDE_PROJECT_DIR}`.
Use these resolved absolute paths for commands below. Reference files receive no substitution.
On a host without skill substitution, derive plugin root from this skill's absolute path (two
parents above SKILL.md's directory) and project root from the host working directory. Verify both
exist; if unavailable, report the missing root. Never send unresolved variables to the shell.

## Inputs

- `<slug>` for feature-scoped work.
- Reads: `spec.md + design.md + optional contracts`.
- Utility contract: [`../../references/utility-contract.md`](../../references/utility-contract.md).
- Progressive artifacts: [`../../references/progressive-artifacts.md`](../../references/progressive-artifacts.md).

## Protocol

1. Refuse with `Status: REFUSED-missing-input` when `spec.md` or `design.md` is missing; point to
   `/kapelle:start <slug>`.
2. Read artifacts directly from disk.
3. Identify only runtime flows whose ordering, retries, failure paths, or cross-component handoffs
   are difficult to understand from the current design.
4. Use native project capabilities when project-specific behavior is needed: [`../../references/project-capabilities.md`](../../references/project-capabilities.md).
5. Request scoped project guidance when the flow crosses an architectural boundary:
   [`../../references/guidance.md`](../../references/guidance.md).
6. Prefer one focused Mermaid block in `End-to-end flow` in `design.md`. When three or more
   components, asynchronous ordering, retries, or failure branches would make that section hard to
   scan, create `design/runtime-flow.md` or another focused `design/<aspect>.md`. Follow every
   diagram with a short plain-language explanation. Do not create a new root `sequences.md`; read
   and read that path as historical context only; write new diagrams in the new feature package. Do not
   write `_kapelle/state.json` directly.
7. Validate the package, rebuild status, and validate state as three separate commands:

```text
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate_progressive_docs.py" "${CLAUDE_PROJECT_DIR}/docs/features/<slug>"
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/build_feature_status.py" "${CLAUDE_PROJECT_DIR}/docs/features/<slug>"
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate_feature_state.py" "${CLAUDE_PROJECT_DIR}/docs/features/<slug>"
```

9. End with the standard handoff. A changed design requires `/kapelle:start <slug> --approve`;
   otherwise return to `/kapelle:status <slug>`.

## Output

- Updated `design.md`; optional focused `design/<aspect>.md`.
- `Status: DONE | utility: sequences | produced: <paths>`.

## Definition of Done

- Inputs were read from disk.
- Outputs exist and link to upstream artifacts instead of duplicating them.
- Skips are explicit.
- Handoff points to current-slice approval or status, never to another hidden stage chain.

## Anti-patterns

- Guessing missing prior-stage output.
- Baking project-specific conventions or provider assumptions into the core skill.
- Running git operations.


## Feature status commands

After changing feature artifacts, run each separately; omit for a repository-only utility:

```text
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/build_feature_status.py" "${CLAUDE_PROJECT_DIR}/docs/features/<slug>"
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate_feature_state.py" "${CLAUDE_PROJECT_DIR}/docs/features/<slug>"
```
