---
name: data-model
description: >
  Document data/schema impact and, when triggered, the behavioral domain model for the current
  lightweight slice before implementation.
---

# Skill: data-model

Follow [`../../references/script-execution.md`](../../references/script-execution.md) for every
bundled Python helper.

Document data/schema impact or an explicit no-schema-change result, plus domain ownership and
behavior when the domain-model trigger applies. This is an optional planning utility, not a
backbone stage and not a migration executor.

## Inputs

- `<slug>` for feature-scoped work.
- Reads: `spec.md + design.md + optional sequences.md`.
- Utility contract: [`../../references/utility-contract.md`](../../references/utility-contract.md).
- Agent contract: [`../../references/agent-orchestration.md`](../../references/agent-orchestration.md).
- Progressive artifacts: [`../../references/progressive-artifacts.md`](../../references/progressive-artifacts.md).

## Protocol

1. Refuse with `Status: REFUSED-missing-input` when `spec.md` or `design.md` is missing; point to
   `/kapelle:start <slug>`.
2. Read artifacts directly from disk.
3. Dispatch `kapelle:explorer` only when persistence is affected
   and the architecture map or scoped rules evidence does not cite a sufficient persistence
   precedent.
4. Use native project capabilities when project-specific behavior is needed: [`../../references/project-capabilities.md`](../../references/project-capabilities.md).
5. Obtain the narrowest relevant persistence guidance before recommending schema or migration work:
   [`../../references/guidance.md`](../../references/guidance.md).
6. Keep one shared logical model across all producer and consumer aspects. Update `Domain and data`
   in `design.md` with ownership, compatibility strategy, migration order, and rollback constraint.
   When an aggregate, lifecycle/status transition, invariant, event, ownership boundary, or
   non-trivial relation changes, create or update `design/domain-model.md` using the progressive
   template. Describe behavior and ownership, not only fields. Record an explicit no-schema-change
   result when applicable. Do not create migrations or production code; `/kapelle:implement` owns
   those changes.
7. Validate the package, rebuild status, and validate state as three separate commands:

```text
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate_progressive_docs.py" "${CLAUDE_PROJECT_DIR}/docs/features/<slug>"
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/build_feature_status.py" "${CLAUDE_PROJECT_DIR}/docs/features/<slug>"
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate_feature_state.py" "${CLAUDE_PROJECT_DIR}/docs/features/<slug>"
```

9. End with the standard handoff. A changed design requires `/kapelle:start <slug> --approve`;
   otherwise return to `/kapelle:status <slug>`.

## Output

- Updated `design.md`; optional `design/domain-model.md`.
- `Status: DONE | utility: data-model | produced: <paths>`.

## Definition of Done

- Inputs were read from disk.
- Data impact is readable in `design.md`; domain behavior is in `design/domain-model.md` only when
  triggered; no parallel machine source of truth was created.
- Compatibility, migration order, and rollback are explicit when persistence changes.
- Handoff points to current-slice approval or status, never to another hidden stage chain.

## Anti-patterns

- Guessing missing prior-stage output.
- Baking project-specific conventions or provider assumptions into the core skill.
- Running git operations.
