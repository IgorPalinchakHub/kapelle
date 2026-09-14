---
name: status
description: >
  Show or rebuild concise feature status and recover disposable `_kapelle/` state without changing
  product behavior or implementation.
---

# Skill: status

Follow [`../../references/script-execution.md`](../../references/script-execution.md) for every
bundled Python helper.

Invoke:

```text
/kapelle:status <slug>
```


## Runtime paths

Plugin root: `${CLAUDE_PLUGIN_ROOT}`. Project root: `${CLAUDE_PROJECT_DIR}`.
Use these resolved absolute paths for commands below. Reference files receive no substitution.
On a host without skill substitution, derive plugin root from this skill's absolute path (two
parents above SKILL.md's directory) and project root from the host working directory. Verify both
exist; if unavailable, report the missing root. Never send unresolved variables to the shell.

## Protocol

1. Refuse with `Status: REFUSED-missing-input` when `docs/features/<slug>/` does not exist.
2. Treat `spec.md`, `design.md`, and `tasks.md` as the normal durable package. Optional promoted
   use-case specs, domain model, contracts, ADRs, detailed design, and diagrams remain durable human
   documentation and participate in approval freshness when present.
3. Recognize `<!-- kapelle-workflow: lightweight-v1 -->` in `spec.md`. When `_kapelle/` is missing
   or invalid, run:

```text
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/rebuild_feature_state.py" "${CLAUDE_PROJECT_DIR}/docs/features/<slug>"
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate_feature_state.py" "${CLAUDE_PROJECT_DIR}/docs/features/<slug>"
```

   Recovery may infer checked work as `implemented-unverified`; it never fabricates approvals,
   command results, reviews, or PASS evidence.
4. For an older or unsupported feature, read its specs/docs only and explain that changes require
   a new slug through start. Do not rebuild, migrate, edit or import its machine state.
5. For lightweight features, select only the earliest necessary route:
   - new raw-task package without a valid progressive artifact format → `/kapelle:start --revise`;
   - missing package/guidance or stale plan → `/kapelle:start`;
   - architecture guidance recorded by a removed capability kind (`project-subagent`) →
     `/kapelle:start <slug> --revise` to reacquire it through the project skill;
   - approved slice with unchecked work → `/kapelle:implement`;
   - implemented slice without current PASS → show the scope decision: add the next requirement
     through `/kapelle:amend`, or run `/kapelle:verify` when accumulated behavior is sufficient;
   - PASS without final approval → `/kapelle:verify <slug> --approve`;
   - final approval → completed.
6. Show current outcome, slice progress, important blockers/deferred validation, core files plus
   any present use-case/domain/contract detail to review, the optional `amend` route when scope is
   still evolving, and one exact routed command. When the route continues an unchecked workstream,
   show its identifier together with its short title or outcome from `tasks.md`, for example
   `W2 — remove the legacy unpublish flow`; never show a bare workstream identifier. Do not expose
   historical stage internals.

This utility performs no implementation edits, validation commands, git actions, or silent
conversion of older packages.
