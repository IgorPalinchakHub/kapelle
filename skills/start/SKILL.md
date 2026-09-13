---
name: start
description: >
  Map the known feature at high level, design one production-shaped walking-skeleton slice, and
  obtain approval before implementation.
---

# Skill: start

Invoke:

```text
/kapelle:start <slug> "<raw task>"
/kapelle:start <slug> --revise "<developer feedback>"
/kapelle:start <slug> --approve
```

Use [artifact-basics.md](../../references/artifact-basics.md) for the compact document format.
Read [architecture-guidance.md](../../references/architecture-guidance.md) when obtaining rules.
Read [developer-questions.md](../../references/developer-questions.md) only for a blocking decision.
Read [progressive-artifacts.md](../../references/progressive-artifacts.md) only for triggered detail
or a changed architectural quality constraint. Command rules are inline below; consult
[script-execution.md](../../references/script-execution.md) only for an execution ambiguity.


## Runtime paths

Plugin root: `${CLAUDE_PLUGIN_ROOT}`. Project root: `${CLAUDE_PROJECT_DIR}`.
Use these resolved absolute paths for commands below. Reference files receive no substitution.
On a host without skill substitution, derive plugin root from this skill's absolute path (two
parents above SKILL.md's directory) and project root from the host working directory. Verify both
exist; if unavailable, report the missing root. Never send unresolved variables to the shell.

## Mandatory command shape

- One Kapelle helper or inspection tool call is one direct executable invocation.
- Use absolute paths from the project-root session. Never add `cd`, shell operators, redirection,
  substitutions, loops, conditionals, background execution, polling, or scratchpads.
- Read stdout, stderr, and exit status from the tool result. Never append `echo`, `wc`, or another
  diagnostic command.
- Never run Git, including through `rtk proxy`, another wrapper, or a subagent. Use native
  Read/Glob/Search on the current worktree.

## Draft or revise

1. Require a stable slug and raw task. Inspect affected current behavior, ownership, entrypoints,
   and nearby evidence. Map known outcomes and candidate capabilities at high level; design only
   the first production-shaped end-to-end slice. Distinguish new behavior, behavior change,
   behavior-preserving refactor, defect, and documentation correction.
2. Plan inline by default. Use an explorer for unclear ownership; a read-only burst of at most
   three investigations only for unfamiliar cross-component scope. Use a critic for material
   ambiguity or high risk. No default business-analyst/critic/devil's-advocate chain.
3. Simple work normally needs no question. If blocked, explain current behavior, the proposed
   change, and consequence; recommend a supported option with its trade-off. Do not repeat
   answered questions or expose internal identifiers.
4. Follow the project's architecture-rules skill for this slice. It chooses sources and any
   subagent. Normalize and validate its findings at _kapelle/architecture-guidance/design.json:

```text
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate_json.py" "${CLAUDE_PROJECT_DIR}/docs/features/<slug>/_kapelle/architecture-guidance/design.json" "${CLAUDE_PLUGIN_ROOT}/dispatcher/architecture-guidance.schema.json"
```

5. Write the three documents using artifact-basics.md:
   - spec.md: current flow, Intended change, Resulting behavior, Preserved behavior,
     Acceptance scenarios; candidates remain non-binding.
   - design.md: Current architecture, Resulting architecture, Technical delta and the usable flow.
   - tasks.md: one walking-skeleton workstream with `Changes`, `Done when`, `Verify` and AC coverage;
     at most three checkboxes only when needed for reviewability.
   Include lightweight-v1, progressive-map-v1, and kapelle-artifact-contract: living-v1 markers.
6. Keep simple changes in these documents. Read progressive-artifacts.md only for independently
   reviewable alternatives/auth/failures (use-case detail); aggregates, transitions, invariants,
   events or ownership (design/domain-model.md); public contracts; expensive decisions (ADR);
   or a diagram that makes a complex flow clearer. No detail or diagram quota.
   Review applicable failure, permission, invariant and interaction risks. Reuse project quality
   defaults; never invent performance or recovery targets.
7. Reuse coverage. Add only basic or critical early tests with a concrete risk rationale; a focused
   unit test is allowed. All remaining tests stay at verify. Keep each slice coherent: update
   affected readers, contracts and migrations together without knowingly broken steps.
8. Validate structure before approval; this does not establish semantic correctness:

```text
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate_progressive_docs.py" "${CLAUDE_PROJECT_DIR}/docs/features/<slug>"
```

9. For a new feature, write `_kapelle/workflow.json` as:

```json
{
  "workflow": "human-controlled",
  "version": 2,
  "created_from": "raw-task",
  "profile": "lightweight"
}
```

   Preserve `created_from: legacy-migration` when revising a migrated feature.
   Validate it with `workflow-state.schema.json`, then run these as separate commands:

```text
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/build_feature_status.py" "${CLAUDE_PROJECT_DIR}/docs/features/<slug>"
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate_feature_state.py" "${CLAUDE_PROJECT_DIR}/docs/features/<slug>"
```
10. On revision, add the living-contract marker and compact structure when they are absent, then
    correct the high-level map or active slice without detailing candidate use cases.
    Any plan, verification, or final approval whose fingerprints no longer match becomes stale
    automatically. Do not promote candidate capabilities into committed behavior until the
    developer requests them through `/kapelle:amend`.

## Approve

`--approve` is a pure gate action: do not inspect the repository, dispatch agents, or edit the
human package. Run `validate_progressive_docs.py`, validate architecture guidance and the existing
documents, then run:

```text
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/review_gate.py" approve "${CLAUDE_PROJECT_DIR}/docs/features/<slug>" plan \
  --confirmation "Developer explicitly approved the current vertical slice."
```

The internal gate keeps the compatibility name `plan`, but human-facing output calls it the
current-slice approval. Never write approval JSON manually. Missing or invalid inputs produce
`Status: REFUSED-missing-input` and the exact correction command.

## Handoff

Show the high-level feature outcome, the usable outcome of the first slice, what remains candidate
or unknown, important trade-offs, files to review, and no more than three unresolved decisions.
After approval, the next command is:

```text
/kapelle:implement <slug> --checkpoint=workstream --validation=ask
```

Refresh `STATUS.md`, use the standard handoff block, hide agent chatter, and never run git
operations.
