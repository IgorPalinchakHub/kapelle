---
name: implement
description: >
  Implement the currently approved vertical slice with lightweight project guidance, then return
  control so the developer can add the next requirement or complete the feature.
---

# Skill: implement

Read [`../../references/developer-questions.md`](../../references/developer-questions.md) before
asking for input. The project architecture-rules subagent result is cached by `start`.
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
2. Default to `--checkpoint=workstream`. Select the unchecked work belonging to the current vertical
   slice. `task` is an opt-in finer pause; `none` continues only through that approved slice.
3. The main agent owns understanding, local planning, implementation, and the first review. Discover
   the narrowest project-native skill or instruction relevant to this workstream and reuse the
   cached architecture guidance. Refresh guidance only if the actual code scope leaves its recorded
   paths/modules/entrypoints or the design changes.
4. Before production edits, add focused functional or characterization coverage when the workstream
   changes an endpoint, command, worker, public use-case method, or fragile legacy behavior and such
   coverage is practical. These are boundary-level tests, not unit tests.
5. Implement the thinnest complete end-to-end outcome. Prefer a real narrow path over speculative
   abstractions for future requirements. For the first slice, complete the production-shaped path
   through input/auth/validation, endpoint or command, use-case service, domain and
   persistence/integration boundary, and stable minimal result as applicable. Do not create all
   future endpoints, empty services, fake success responses, or TODO implementations. Do not leave
   the tree knowingly unloadable between checkpoints. If a schema, enum, or public contract changes,
   update its readers, migration/compatibility handling, and boundary tests in the same slice.
6. Do not write unit tests, unit-test fixtures, or strict-TDD loops here. All unit tests are planned
   and written once, after production implementation, by `/kapelle:verify`.
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
9. Mark the workstream checkbox complete only when its production outcome is present and its narrow
   development check is either passed or explicitly deferred. Add at most two indented lines:
   `Result:` and, when needed, `Deferred validation:`. Do not create per-task run narratives,
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
- checks passed or deferred;
- two explicit next choices after the slice:
  - `/kapelle:amend <slug> "<next business or technical requirement>"` to evolve the feature;
  - `/kapelle:verify <slug> --validation=ask` when the developer considers the current scope complete.

Questions must be standalone and concise. Never ask the developer to decode internal ids or raw
agent output. Never run git operations.
