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
5. Writes a concise `design.md` and compact surface plan. `validate_design.py` enforces at most 280
   lines and 2800 words. Target 150–220 lines.
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

## State ownership

Stages never hand-edit `_kapelle/manifest.json`, `_kapelle/state.json`, `STATUS.md`, or review-gate
JSON. Use `scripts/review_gate.py` for gates and `scripts/build_feature_status.py` for the derived
projection. Prefer one artifact write plus the single permitted correction pass.
