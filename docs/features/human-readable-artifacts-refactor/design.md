# Design

## 1. Context and goal

Kapelle must expose one understandable, human-controlled SDLC route. Durable product and technical
documents stay at the feature root, while recoverable execution state and evidence stay under
`_kapelle/`. A developer can remove that internal directory and later resume from the documents and
current project state without fabricated approval or validation evidence.

## 2. Scope and constraints

The design covers the human feature layout, deterministic status and recovery, workflow migration,
an XS/S fast lane, adaptive interview depth, and stage protocols. It remains provider-neutral,
performs no git operations, and keeps explicit developer approvals. It does not introduce
one-click autonomous orchestration or reconstruct deleted historical evidence.

## 3. Architecture rules applied

- Human-readable Markdown is durable state; machine-only data lives under `_kapelle/`.
- `STATUS.md` is a deterministic projection, not a second source of truth.
- Missing inputs or evidence fail safely instead of being inferred.
- Project architecture rules are discovered through native project capabilities.
- The deterministic runtime uses Python's standard library and writes only inside the feature
  directory.
- One public backbone owns routing; former stage names are non-executing compatibility wrappers.

## 4. Building blocks and responsibilities

- `references/feature-layout.md` defines physical paths and recovery classes.
- `references/artifact-presentation.md` defines the human presentation contract.
- `references/fast-lane.md` and `references/interview-depth.md` control process depth without
  weakening artifact coverage.
- `references/design-template.md` defines the stable high-level design structure and the boundary
  for detailed documents under `design/`.
- `scripts/feature_state.py` discovers artifacts, validates freshness, derives readiness, and
  selects the next command.
- `build_feature_status.py`, `rebuild_feature_state.py`, and `validate_feature_state.py` expose
  deterministic status, recovery, and consistency checks.
- `migrate_feature_layout.py` migrates physical layout v1 to v2;
  `migrate_workflow.py` adopts the single human-controlled workflow.
- Backbone skills own nine stages: `start`, `spec`, `design`, `plan`,
  `base-functional-tests`, `implement`, `unit-tests`, `verify`, and `finalize`.

## 5. Runtime flows

For a standard feature, `start` creates the reviewed outline, then `spec`, `design`, and `plan`
produce separate approval gates before delivery. For an eligible XS/S feature, `start --lane=fast`
creates the specification, design, and plan in one bounded pass and asks for one `feature-plan`
approval. Both lanes then share the same delivery stages.

Status first validates the workflow marker and internal state. If `_kapelle/` is missing or invalid,
it rebuilds reconstructible state, labels checked work without evidence as
`implemented-unverified`, lists unrecoverable evidence, and selects the smallest safe next step.
An unmarked historical feature routes only to `migrate`; it never silently re-enters a legacy
pipeline.

## 6. Data and domain impact

No application database is involved. This is a plugin artifact-schema change. Workflow state now
records `lane: fast|standard`; size state records both lane and interview depth. Fast-lane planning
uses the same canonical product, design, surface, and task artifacts as the standard lane, so it can
fall back to standard execution without data conversion.

## 7. Contracts and integrations

JSON schemas under `dispatcher/` define workflow, approval, feature, task, validation, and release
state. `scripts/validate_task_plan.py` validates dependency ordering and acceptance-criteria
coverage. `scripts/validate_design.py` validates the fixed high-level design headings. Native
project architecture and delivery capabilities are discovered semantically and remain outside
Kapelle's core routing.

## 8. Cross-cutting concerns

Recovery preserves security and correctness through path confinement, stable serialization, atomic
writes, bounded agent passes, explicit validation policy, and refusal on ambiguous input. Interview
depth changes the number of questions and critique passes, never acceptance-criteria,
architecture-rule, contract, or validation coverage. Fast-lane eligibility excludes unclear,
cross-cutting, security-sensitive, destructive-data, or large-task features.

## 9. Decisions and trade-offs

- A single public backbone removes routing ambiguity; deprecated wrappers remain temporarily only
  to provide an actionable migration message.
- Fast lane merges planning interactions, not artifacts. This keeps recovery and later expansion
  simple at the cost of retaining several small files.
- The high-level design has a fixed Arc42-like shape. This improves scanability while separate
  `design/` documents prevent complex component detail from bloating it.
- Human and machine task representations coexist, but deterministic validation exposes drift and
  the machine graph remains authoritative for execution dependencies.
- `_kapelle/` recovery is safe continuation, not lossless restoration.

## 10. Validation and rollout

Unit tests cover feature routing, deleted internal state, false checked-task evidence, migration,
fast-lane approval, structured-design validation, and task-plan invariants. `validate_plugin.py`
checks the public backbone, schemas, wrappers, docs, manifests, and bundled skills. Existing feature
directories are adopted explicitly with `/kapelle:migrate`; no approval or historical test result
is recreated during rollout.

## 11. Open questions

None blocking. Compatibility wrappers can be removed in a later major cleanup after users have had
one release to migrate command usage.
