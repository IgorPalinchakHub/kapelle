# Feature layout contract

Kapelle layout version 2 separates durable human documentation from derived execution state.

## Human-readable durable state

The normal lightweight layout is:

```text
docs/features/<slug>/
  STATUS.md
  spec.md
  specs/                    # optional; detailed promoted use cases only
  design.md
  tasks.md
  contracts/                # optional; only when independently useful
  adr/                      # optional; only for durable decisions
  design/                   # optional; domain model or complex component detail
  diagrams/                 # optional; not a completion requirement
  _context/                 # optional feature-local repository evidence
    evidence-index.md       # reconstruction claim/source index
  _kapelle/                 # derived state and historical evidence
```

The root may contain additional human Markdown only when the feature genuinely needs it, for
example a complex `sequences.md`. JSON, JSONL, fingerprints, task-run plans, review verdicts, and
runtime logs must not be written in the feature root.

## Internal state

```text
_kapelle/
  manifest.json
  state.json
  workflow.json
  surface-plan.json         # optional complex/parallel coordination
  task-plan.json            # optional complex/parallel coordination
  recovery.json
  reconstruction.json
  reconstruction-coverage.json
  changes/
  architecture-guidance/
  task-runs/                # legacy/audited execution only
  validation/               # legacy/audited execution only
  approvals/
  telemetry/
  history/
```

- `manifest.json` identifies layout version 2 and fingerprints human artifacts.
- `state.json` is the current derived execution projection.
- `_kapelle/surface-plan.json` and `task-plan.json` are optional machine coordination graphs for
  genuinely complex or parallel work; normal routing does not require them.
- Evidence that cannot be reconstructed lives under validation, approvals, telemetry, changes, and
  history.

The reconstruction workflow creates at least one useful detail document under both `specs/` and
`design/`. It does not create `tasks.md` or `test-plan.md` and never enters delivery.

## Recovery invariant

Human documents contain the high-level known feature map, implemented base, current approved slice,
non-binding candidate capabilities, and any durable use-case/domain/contract detail. They are
sufficient to resume planning and reconcile implementation. If `_kapelle/` is missing or invalid,
rebuild it from the human package and current project evidence.
For the lightweight route, the invisible marker in `spec.md` reconstructs
`_kapelle/workflow.json`. Reconstruction retains its marker in `proposal.md`.

Recovery may derive scope, AC identifiers, surfaces, tasks, likely progress, validation needs, and
the minimal next route. It must not fabricate:

- approvals;
- previous agent/review verdicts;
- command output;
- token or cost telemetry;
- validation results not present in current, trustworthy project or CI evidence.

A checked human task without current validation evidence becomes `implemented-unverified`.
Evidence loss reduces certainty and completion readiness; it does not force a complete restart.
A recovered coordination graph is provisional: it may support validation-only work for already
implemented tasks, but it cannot authorize new code-writing or finalization until scoped
architecture guidance and planning replace it.

## Stage paths

| Logical artifact | Physical path |
|---|---|
| product specification | `spec.md` |
| detailed business specifications | `specs/*.md` |
| technical design | `design.md` |
| detailed component/domain design | `design/*.md` |
| aspect coordination | `_kapelle/surface-plan.json` |
| task checklist | `tasks.md` |
| execution graph (optional) | `_kapelle/task-plan.json` |
| architecture guidance | `_kapelle/architecture-guidance/*.json` |
| reconstruction scope | `_kapelle/reconstruction.json` |
| reconstruction evidence coverage | `_context/evidence-index.md`, `_kapelle/reconstruction-coverage.json` |
| task execution evidence (audited route only) | `_kapelle/task-runs/<task-id>.json` |
| human approvals | `_kapelle/approvals/*.json` |
| final verification | `_kapelle/verification.json` |
| feature status | `_kapelle/state.json` and generated `STATUS.md` |

There is one physical path for each logical artifact. Skills must not write a second source of truth
under a legacy path.

## Compatibility

Unmarked or `human-controlled-v1` feature directories are never silently routed through old
stages. First use
`/kapelle:migrate <slug>` or `scripts/migrate_workflow.py`. Physical layout-v1 directories may
also require:

```text
scripts/migrate_feature_layout.py <feature-dir> --dry-run
scripts/migrate_feature_layout.py <feature-dir> --apply
```

Migration parses and semantically validates legacy coordination and change state before writing,
preserves legacy evidence under `_kapelle/history/legacy/`, reports collisions before writing, and
is idempotent. The migration marker is written only after rebuilt feature-state validation passes.
