---
name: implement
description: >
  Implement the currently approved vertical slice with lightweight project guidance, then return
  control so the developer can add the next requirement or complete the feature.
---

# Skill: implement

Read [`../../references/developer-questions.md`](../../references/developer-questions.md) before
asking for input. The project architecture-rules skill result is cached by `start`.
Read [`../../references/progressive-artifacts.md`](../../references/progressive-artifacts.md) to
preserve the active workstream and traceability contract.
Follow [`../../references/script-execution.md`](../../references/script-execution.md) for every
bundled Python helper and shell inspection command.


Before changing an existing package, require the current workflow. For a feature from an older
plugin version, read its specs/docs as context only and start a new change with a new slug through
start. Never modify that old package or reuse its approvals, completed tasks or verification.

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

Invoke:

```text
/kapelle:implement <slug> [--checkpoint=workstream|task|none] [--validation=ask|allow|skip]
```

## Protocol

1. Require the lightweight workflow marker, `spec.md`, `design.md`, `tasks.md`, current
   `_kapelle/architecture-guidance/design.json`, and a current `plan` approval. Check the gate with:

```text
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/review_gate.py" check "${CLAUDE_PROJECT_DIR}/docs/features/<slug>" plan
```

   Refuse code-writing on failure. A recovered feature returns to `/kapelle:start <slug>` to rebuild
   or approve its plan.
2. Default to `--checkpoint=workstream`. Select a top-level unchecked workstream belonging to the
   current vertical slice. Preserve its `AC-NN` coverage and its `Changes`, `Done when`, and
   `Verify` fields. `task` is an opt-in finer pause; `none` continues only through that approved
   slice.
3. The main agent owns understanding, local planning, implementation, and the first review. Discover
   the narrowest project-native skill or instruction relevant to this workstream and reuse the
   cached architecture guidance. Refresh guidance only if the actual code scope leaves its recorded
   paths/modules/entrypoints or the design changes.
4. Follow `../../references/human-control.md` Test timing. Reuse existing coverage first; before
   production edits, add only basic boundary/characterization evidence or a small test protecting a
   concrete high-consequence behavior. A focused unit test is allowed when it is the smallest
   useful evidence. Explain the prevented failure and existing coverage gap in `Verify`. Simple
   reversible changes do not require a new test when an existing check is sufficient.
5. Implement the thinnest complete end-to-end outcome. Prefer a real narrow path over speculative
   abstractions for future requirements. For the first slice, complete the production-shaped path
   through input/auth/validation, endpoint or command, use-case service, domain and
   persistence/integration boundary, and stable minimal result as applicable. Do not create all
   future endpoints, empty services, fake success responses, or TODO implementations. Do not leave
   the tree knowingly unloadable between checkpoints. If a schema, enum, or public contract changes,
   update its readers, migration/compatibility handling, and boundary tests in the same slice.
6. Do not write the remaining test suite or run universal strict-TDD loops here. Beyond the basic
   and critical early tests above, all remaining tests are planned and written at `/kapelle:verify`.
   Keep early test setup minimal and reuse it later; do not create speculative fixtures or a
   separate test-author agent chain.
7. Use an explorer only for newly discovered ownership uncertainty. Use a fresh critic/reviewer only
   for high-risk changes, unresolved design deviation, or explicit developer request.
   Do not dispatch planner and implementer subagents by default.
   Agent Teams require stable approved contracts, dependency-ready parallel work, disjoint file
   ownership, runtime support, and explicit developer approval. Do not use a team for the initial
   tightly coupled skeleton. A team burst uses at most three agents and the main agent owns
   integration.
8. Development checks follow `ask | allow | skip`:
   - prefer syntax/load checks and the smallest affected functional test;
   - do not run full static analysis, lint, or broad suites unless requested;
   - skipped or cancelled required checks are reported as deferred, never PASS.
9. Mark only the active top-level workstream checkbox complete when its production outcome is
   present and its narrow development check is either passed or explicitly deferred. Do not remove
   or rewrite its `AC-NN` coverage or its `Changes`, `Done when`, and `Verify` fields. Add at most
   two indented lines: `Result:` and, when needed, `Deferred validation:`. Do not create per-task run narratives,
   planner/reviewer transcripts, or telemetry by default.
10. If implementation reveals a missing business rule, domain behavior, contract, boundary, or
    design contradiction, stop and route to `/kapelle:amend`. A normal implementation defect can be
    fixed inside the current workstream.
11. Rebuild and validate generated status after each checkpoint.

## Checkpoint response

Return only:

- business outcome implemented;
- changed areas;
- observable behavior and important trade-off;
- a short current-to-result explanation before file or paragraph links;
- checks passed or deferred;
- when naming the next workstream, its identifier plus short title or outcome from `tasks.md`, never
  a bare identifier such as `W2`;
- two explicit next choices after the slice:
  - `/kapelle:amend <slug> "<next business or technical requirement>"` to evolve the feature;
  - `/kapelle:verify <slug> --validation=ask` when the developer considers the current scope complete.

Questions must be standalone and concise. Never ask the developer to decode internal ids or raw
agent output. Never run git operations.
