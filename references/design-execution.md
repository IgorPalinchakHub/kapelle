# Bounded design execution

`design` separates a short architecture direction from accepted boundary detail. Performance
budgets reduce duplicate work; they never waive product coverage, scoped project rules, or blocking
risk analysis.

## High-level mode

The normal `/kapelle:design <slug>` invocation:

1. Reuses `proposal.md`, `spec.md`, `specs/`, `_context/architecture.md`, and the shared
   architecture baseline. Repository work is evidence-delta discovery only.
2. Uses at most 12 targeted lookup batches for unresolved architecture decisions. One batch may
   search several related paths. If the supplied context is materially wrong, record the gap and
   refresh only the feature overlay.
3. Dispatches the project architecture-rules capability immediately. Its prompt allows at most 12
   source lookup batches and requires:
   - a repository/source-affinity check before querying an external index;
   - binding rules and collisions first;
   - design-changing gaps second;
   - no generic framework advice or exhaustive rule catalogue.
4. May draft an outline while guidance runs, but does not finalize artifacts until the typed
   guidance result is collected.
5. Writes a concise `design.md` and compact surface plan with
   `<!-- kapelle-design-format: high-level-v2 -->` near the top. `validate_design.py` enforces at
   most 280 lines and 2800 words for this format. Target at most 220 lines and 2200 words so normal
   edits retain safety margin.
6. Records consequential choices as ADR candidates in section 9. It does not create new ADR files,
   exhaustive call-site tables, field-level domain models, full endpoint payloads, or test
   mechanics.

## High-level critic

At standard/full depth, dispatch one fresh critic after scoped rules are available. Its prompt:

- allows at most 12 focused artifact/source reads;
- checks spec contradictions, boundary viability, dependency direction, security, concurrency,
  destructive data, public contracts, failure behavior, and rule collisions;
- returns all blockers and material should-fix findings, but no NIT list;
- does not perform exhaustive implementation call-site or test-case enumeration;
- permits one correction pass.

Wait for the critic's terminal result. Do not send repeated status requests. If the runtime budget
is exhausted, cancel/stop that run before any inline fallback. Never let a critic and its inline
fallback work concurrently. Project architecture guidance has no inline substitute: a missing or
timed-out required project capability blocks design.

## Detail mode

`/kapelle:design <slug> --detail` means the developer accepts the high-level direction for
elaboration. It creates only independently reviewable:

- `design/*.md` boundary documents;
- field/status/domain skeletons when domain impact exists;
- full changed interface contracts under `contracts/`;
- ADR files for accepted consequential decisions;
- mechanical call-site and transaction detail needed before planning.

Reuse current architecture guidance and perform only scope-delta lookup. Escalate back to
`--revise` or `spec --revise` when detail changes the accepted direction or product behavior.

## Approval mode

`/kapelle:design <slug> --approve` is a pure gate operation. Route it before the high-level and
detail protocols. It runs `validate_architecture_package.py` once and, on PASS,
`review_gate.py approve` once. It performs no artifact reads for LLM review, repository lookup,
capability discovery, agent dispatch, critic run, generation, compaction, or artifact edit.

Validation failure ends the invocation with `REFUSED-validation` and a separate `--revise`
command. Approval never offers to repair and continue in the same invocation.

Legacy designs without the high-level-v2 marker retain structural validation but receive a
non-blocking size warning. They become subject to the hard size gate only after explicit
`/kapelle:design <slug> --compact`. Compaction is a separate write operation: one complete rewrite,
at most one correction, target 220 lines/2200 words, and no approval in that invocation.

## State ownership

Stages never hand-edit `_kapelle/manifest.json`, `_kapelle/state.json`, `STATUS.md`, or review-gate
JSON. Use `scripts/review_gate.py` for gates and `scripts/build_feature_status.py` for the derived
projection. Prefer one artifact write plus the single permitted correction pass.
