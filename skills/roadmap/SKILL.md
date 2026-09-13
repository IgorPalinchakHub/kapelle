---
name: roadmap
description: >
  Maintain feature roadmap state across Now, Next, Later, and Shipped.
---

# Skill: roadmap

Maintain roadmap state across Now/Next/Later/Shipped.


## Runtime paths

Plugin root: `${CLAUDE_PLUGIN_ROOT}`. Project root: `${CLAUDE_PROJECT_DIR}`.
Use these resolved absolute paths for commands below. Reference files receive no substitution.
On a host without skill substitution, derive plugin root from this skill's absolute path (two
parents above SKILL.md's directory) and project root from the host working directory. Verify both
exist; if unavailable, report the missing root. Never send unresolved variables to the shell.

## Inputs

- `<slug>` for feature-scoped work.
- Reads: `user request or feature artifacts`.
- Utility contract: [`../../references/utility-contract.md`](../../references/utility-contract.md).
- This is a project utility, not a feature backbone stage.

## Protocol

1. Require an explicit roadmap change or a feature whose current placement must be reconciled.
2. Read `docs/roadmap.md` and only the named feature artifacts.
3. Move or add the minimum roadmap entry requested by the developer. Do not infer commitments,
   dates, priority, or shipped status.
4. Write `docs/roadmap.md` and summarize the exact placement change.
5. Do not modify feature workflow state and do not emit a feature next-stage command.

## Output

- `docs/roadmap.md`.
- `Status: DONE | utility: roadmap | produced: docs/roadmap.md`.

## Definition of Done

- Inputs were read from disk.
- Outputs exist and link to upstream artifacts instead of duplicating them.
- Skips are explicit.
- No hidden feature-stage handoff is introduced.

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

Follow [script-execution.md](../../references/script-execution.md) for helper execution.
