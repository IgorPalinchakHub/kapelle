---
name: verify
description: >
  Reconcile a feature with its specification, write all unit tests at the end, run one risk-based
  validation batch, and obtain final developer approval.
---

# Skill: verify

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
/kapelle:verify <slug> [--validation=ask|allow|skip]
/kapelle:verify <slug> --developer-verified "<what was checked and the result>"
/kapelle:verify <slug> --approve
```

## Verify

1. Treat invocation of `/kapelle:verify` as the developer's explicit statement that no additional
   feature slices are currently required. Require a current `plan` approval and every approved
   production slice checked in `tasks.md`. Refuse and point to `/kapelle:implement` when current
   work is incomplete. If scope is still evolving, point to `/kapelle:amend` instead.
2. Compare the as-built code with `spec.md`, `design.md`, detailed `specs/`, `design/domain-model.md`,
   contracts, ADRs, and project architecture guidance when present. Reconcile committed behavior,
   use-case flows, domain state/behavior, system boundaries, and integration contracts. Update the
   human documents only to describe confirmed implementation decisions; never silently promote a
   candidate capability. Behavior mismatches go through `/kapelle:amend`.
   Converge `current -> change -> result -> preserved`: update `Current behavior` to the confirmed
   resulting user flow while retaining concise implemented-change context. For refactoring,
   reconcile brief prior affected architecture, resulting architecture, technical delta, and
   preserved behavior/contracts. Root documents become the canonical current map.
   Create or update `specs/*.md`, focused `design/*.md`, contracts, ADRs, or diagrams only when
   implementation evidence meets their normal trigger and the artifact remains independently
   useful after completion. Final detail must let another developer or LLM understand the current
   user and affected technical flows without the authoring chat; do not narrate every class or
   method.
   Reconcile active acceptance scenarios with completed workstreams and performed verification.
   Every implemented active scenario remains linked to at least one workstream and relevant test or
   manual evidence; candidate capabilities remain outside this trace.
3. Plan and write all unit tests now, grouped by changed behavior and failure modes. Do not generate
   tests for trivial accessors or implementation details merely to increase count.
4. Build one exact, risk-based validation batch from project-native commands. Include applicable
   functional, unit, integration/contract, static-analysis, lint/format, and build checks. Omit
   categories that genuinely do not apply and explain why in the review summary.
5. Under `ask`, show the exact commands once and ask whether to run all, run selected, accept the
   developer's completed verification, or defer. Under `allow`, run them. Under `skip`, execute
   none. A failed required check yields `FAILED`; a skipped or cancelled required check yields
   `validation-deferred` unless the developer later explicitly confirms that the complete
   applicable verification batch passed outside Kapelle.
6. Treat an unambiguous developer statement such as "I manually tested and verified everything;
   all planned checks pass" as valid verification evidence. Do not demand captured command output.
   Record it as `developer-attested`, preserve the developer's wording, and state clearly that
   Kapelle did not observe the output. If the statement covers only selected behavior, mark only
   those categories as covered and keep the remaining required checks deferred. Ask one concise
   standalone question only when the reported coverage or result is genuinely unclear.
7. Use a fresh reviewer only for high-risk features, material architecture deviations, repeated
   failures, or explicit developer request. Keep one review/correction pass. Do not run a
   multi-agent review chain.
8. Run the progressive validator for progressive packages:

```text
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate_progressive_docs.py" "${CLAUDE_PROJECT_DIR}/docs/features/<slug>"
```

   Record one `_kapelle/verification.json` with the deterministic writer, passing every affected
   implementation/test/config/migration file through `--implementation-file`:

```text
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/record_verification.py" "${CLAUDE_PROJECT_DIR}/docs/features/<slug>" \
  --status PASS \
  --evidence-source agent-observed|developer-attested|mixed \
  --category <covered-category> \
  --check "<exact command or concise manual check>" \
  --implementation-file <project-relative-file> \
  [--developer-confirmation "<explicit developer statement>"]
```

   The writer fingerprints current inputs and implementation, validates against
   `dispatcher/verification.schema.json`, writes the evidence, and refreshes `STATUS.md`.
   `developer-attested` and `mixed` require `--developer-confirmation`.
   For an independent structural check, run:

```text
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate_json.py" "${CLAUDE_PROJECT_DIR}/docs/features/<slug>/_kapelle/verification.json" "${CLAUDE_PLUGIN_ROOT}/dispatcher/verification.schema.json"
```

   Do not create per-task validation JSON, separate unit-test-run state, diagrams, release notes, or
   agent transcripts unless independently useful to the developer. Reconcile every existing
   triggered diagram with as-built participants, ordering, and failure behavior; remove or correct
   stale diagrams rather than preserving misleading visuals. Run an available project-native
   Mermaid renderer or checker when applicable; otherwise require closed, non-empty source and the
   structural validator's nearby plain-language explanation check.
9. On PASS, present: implemented flow, test coverage, commands/results, evidence source, remaining
   manual checks, risks, and the exact final approval command.

## Final approval

`--approve` is a pure gate action. Do not edit code/docs, run commands, or dispatch agents. Require
current PASS verification—agent-observed, developer-attested, or mixed—and explicit final developer
confirmation, then run:

```text
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/review_gate.py" approve "${CLAUDE_PROJECT_DIR}/docs/features/<slug>" final \
  --confirmation "Developer explicitly approved the verified feature."
```

Never write approval JSON manually.

The feature is complete when the current `final` approval exists. No version number, release JSON,
diagram, commit, or push is required by Kapelle.

Refresh `STATUS.md`, use the standard handoff block, and never run git operations.
