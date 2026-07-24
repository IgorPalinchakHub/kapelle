# Feature layout contract

Kapelle layout version 2 separates durable human documentation from derived execution state.

## Human-readable durable state

The superset layout is:

```text
docs/features/<slug>/
  STATUS.md
  proposal.md
  spec.md
  specs/                    # standard lane or genuinely needed fast detail
  design.md
  design/                   # standard detail only when useful
  tasks.md
  test-plan.md              # standard; fast may inline strategy in tasks.md
  contracts/
  adr/
  diagrams/
  _context/                 # optional feature-local repository evidence
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
  size.json
  surface-plan.json
  task-plan.json
  recovery.json
  changes/
  architecture-guidance/
  task-runs/
  validation/
  approvals/
  telemetry/
  history/
```

- `manifest.json` identifies layout version 2 and fingerprints human artifacts.
- `state.json` is the current derived execution projection.
- `_kapelle/surface-plan.json` and `task-plan.json` remain the canonical machine coordination graphs.
- Evidence that cannot be reconstructed lives under validation, approvals, telemetry, changes, and
  history.

## Recovery invariant

Human documents are sufficient to resume planning and reconcile implementation. If `_kapelle/` is
missing or invalid, rebuild it from the human package and current project evidence.
For the human-controlled route, the invisible marker in `proposal.md` reconstructs
`_kapelle/workflow.json`.

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
| proposal | `proposal.md` |
| product specification | `spec.md` |
| detailed business specifications | `specs/*.md` |
| technical design | `design.md` |
| detailed component/domain design | `design/*.md` |
| aspect coordination | `_kapelle/surface-plan.json` |
| task checklist | `tasks.md` |
| execution graph | `_kapelle/task-plan.json` |
| test plan | `test-plan.md` |
| size | `_kapelle/size.json` |
| architecture guidance | `_kapelle/architecture-guidance/*.json` |
| task execution evidence | `_kapelle/task-runs/<task-id>.json` |
| validation evidence | `_kapelle/validation/*.json` |
| human approvals | `_kapelle/approvals/*.json` |
| test-phase evidence | `_kapelle/base-functional-tests.json`, `unit-tests.json`, `verification.json` |
| final diagrams | `diagrams/*.mmd` |
| completion record | `_kapelle/release.json` |
| feature status | `_kapelle/state.json` and generated `STATUS.md` |

There is one physical path for each logical artifact. Skills must not write a second source of truth
under a legacy path.

## Compatibility

Unmarked feature directories are never silently routed through old stages. First use
`/kapelle:migrate <slug>` or `scripts/migrate_workflow.py`. Physical layout-v1 directories may
also require:

```text
scripts/migrate_feature_layout.py <feature-dir> --dry-run
scripts/migrate_feature_layout.py <feature-dir> --apply
```

Migration parses and semantically validates legacy coordination and change state before writing,
preserves legacy evidence under `_kapelle/history/legacy/`, reports collisions before writing, and
is idempotent. The migration marker is written only after rebuilt feature-state validation passes.
