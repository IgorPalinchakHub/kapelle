---
name: design
description: >
  Create, detail, revise, or approve a pragmatic feature architecture using scoped project rules,
  including domain models, contracts, and low-coupling design documents when useful.
---

# Skill: design

Write the developer-facing technical specification, machine coordination plan, and ADRs.

Read [`../../references/design-template.md`](../../references/design-template.md) and
[`../../references/design-execution.md`](../../references/design-execution.md). Apply
[`../../references/developer-questions.md`](../../references/developer-questions.md) whenever
developer input is required. `design.md`
always uses its eleven headings in the specified order; run
`scripts/validate_design.py docs/features/<slug>/design.md` before approval.

Invoke:

```text
/kapelle:design <slug>
/kapelle:design <slug> --detail
/kapelle:design <slug> --revise "<developer feedback>"
/kapelle:design <slug> --compact
/kapelle:design <slug> --approve
```

## Inputs

- `<slug>` for feature-scoped work.
- Reads: `proposal.md + spec.md + CONTEXT.md optional + feature-local architecture context optional + shared
  architecture baseline optional`.
- Shared contract: [`../../references/stage-contract.md`](../../references/stage-contract.md).
- Agent contract: [`../../references/agent-orchestration.md`](../../references/agent-orchestration.md).
- Execution depth: [`../../references/execution-depth.md`](../../references/execution-depth.md).
- Architecture guidance:
  [`../../references/architecture-guidance.md`](../../references/architecture-guidance.md).

## Mode routing

Route on the invocation before reading feature artifacts or entering the generation protocol.

### Approval route

When `--approve` is present, do only this route and return:

1. Run
   `scripts/validate_architecture_package.py docs/features/<slug>`.
2. On non-zero exit, emit
   `Status: REFUSED-validation | stage: design | next: /kapelle:design <slug> --revise
   "resolve the reported package errors"` and stop. Do not read artifact bodies, edit files,
   discover capabilities, dispatch agents, compact content, or offer to repair and approve in the
   same invocation.
3. On PASS, run
   `scripts/review_gate.py approve docs/features/<slug> architecture --confirmation
   "Developer explicitly approved the detailed architecture package."`.
   The explicit `--approve` invocation is the developer confirmation; never ask for a second
   confirmation.
4. `review_gate.py` writes the approval and refreshes state/status. Do not run another status
   refresh. Never construct approval JSON manually. Hand off to `/kapelle:plan <slug>` and return.

### Compaction route

When `--compact` is present, compact only the existing `design.md`; never approve in the same
invocation. Preserve every decision and link already backed by `design/`, `contracts/`, or `adr/`.
Add `<!-- kapelle-design-format: high-level-v2 -->` within the first five lines. Target at most
220 lines and 2200 words, leaving margin below the hard 280/2800 limits. Perform one complete
rewrite and at most one correction after `validate_design.py`; if it still fails, stop with
`Status: REFUSED-validation`. Refresh status once and hand off to
`/kapelle:design <slug> --approve`.

All other modes use the generation protocol below.

## Generation protocol

1. Validate required inputs and standard lane. Fast-lane high-level design is produced by `start`.
   For standard lane, run
   `scripts/review_gate.py check docs/features/<slug> business-spec`. On non-zero exit, emit
   `Status: REFUSED-missing-input | missing: _kapelle/approvals/business-spec.json | run-first:
   /kapelle:spec <slug> --approve` and write nothing.
2. Read artifacts directly from disk.
3. Select execution depth per decision/aspect. Prefer
   `docs/features/<slug>/_context/architecture.md`, then use `docs/architecture-map.md` as a shared
   baseline. Never refresh the shared baseline from this stage. Perform evidence-delta discovery
   under the bounded design contract; dispatch `kapelle:explorer` only when the feature overlay is
   materially incomplete.
4. Identify the tentative aspects, modules, entrypoints, and paths. Semantically discover and
   dispatch the project's architecture-rules subagent for exactly that scope. Validate its output
   by persisting `_kapelle/architecture-guidance/design.json` and running
   `scripts/validate_json.py docs/features/<slug>/_kapelle/architecture-guidance/design.json
   dispatcher/architecture-guidance.schema.json`; refuse on non-zero exit, a missing capability,
   or blocking gaps.
5. Apply the architecture-capability source-affinity and lookup budget from
   `design-execution.md`. Let it discover narrower project capabilities only for unresolved
   decisions. Collect its terminal result once; do not poll it repeatedly.
6. In normal mode, draft a concise high-level `design.md` from the specification, cited
   precedents, and scoped architecture rules, using the fixed template.
   Add `<!-- kapelle-design-format: high-level-v2 -->` within the first five lines.
   Include affected components, backend/frontend/data responsibilities, runtime/failure flows,
   data/schema impact, contracts, security, compatibility, validation, and known deviations. Use a
   separate `sequences.md` only for unusually complex flows.
   Keep accepted decisions as ADR candidates; do not create new ADR files in normal mode.
7. Write a compact `_kapelle/surface-plan.json` with aspect dependencies, shared-contract
   ownership, and cross-aspect integration intent. Run
   `scripts/validate_json.py docs/features/<slug>/_kapelle/surface-plan.json
   dispatcher/surface-plan.schema.json`; refuse completion on non-zero exit.
8. At `standard` or `full` depth, dispatch one bounded high-level critic exactly as specified in
   `design-execution.md`. At `lean`, perform a focused inline consistency check. Never run the
   critic concurrently with its inline fallback. Resolve or explicitly defer every blocker.
   Translate any developer decision into intended implementation, consequence, and options with
   trade-offs; never expose critic prose or artifact/finding ids as the question.
9. After the developer accepts the high-level direction by invoking `--detail`, create only useful
   low-coupling, high-cohesion documents under `design/`. Include:
   - component responsibilities and dependencies;
   - backend, frontend, worker, data, and integration slices that actually apply;
   - proposed domain model skeleton with aggregates, classes, fields, relations, invariants, and
     status transitions;
   - contracts for every changed endpoint, command, event, or worker input/output;
   - ADRs only for consequential choices.
   Keep `design.md` as the overview and put contract details under `contracts/`.
10. On `--revise`, update the affected design package and invalidate architecture approval and all
    downstream approvals/evidence. If business behavior must change, propose `/kapelle:spec
    <slug> --revise` instead of silently editing the spec.
11. Write outputs: `design.md`, optional `design/*.md`, `_kapelle/surface-plan.json`, `adr/*.md`, and
    `_kapelle/architecture-guidance/design.json`.
12. Run `scripts/build_feature_status.py docs/features/<slug>` exactly once after artifact writes.
    Never hand-edit manifest, state, status, or approval JSON. Emit the chat handoff per
    [`../../references/handoff.md`](../../references/handoff.md).

## Output

- `design.md`, optional `design/*.md`, contracts, `_kapelle/surface-plan.json`, ADRs, approvals,
  and architecture-guidance evidence.
- `Status: DONE | stage: design | produced: <paths>`.

## Definition of Done

- Inputs were read from disk.
- Outputs exist and link to upstream artifacts instead of duplicating them.
- Every aspect and cross-aspect dependency is explicit and validated.
- Design decisions cite scoped project architecture rules.
- Skips are explicit.
- Handoff points to `--detail`, `--approve`, or `plan` as the current gate requires.
- Approval performs zero artifact edits and zero agent or capability dispatches.

## Anti-patterns

- Guessing missing prior-stage output.
- Repairing, compacting, or regenerating artifacts during `--approve`.
- Re-running validation until an exact line or word boundary is reached.
- Baking project-specific conventions or provider assumptions into the core skill.
- Running git operations.
