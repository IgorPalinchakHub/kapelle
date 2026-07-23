# Human-readable artifact architecture

## Summary

Layout-v2 separates canonical human documents from derived execution state. Small deterministic
Python utilities build status, recover document-derived state, validate consistency, and migrate
legacy directories. Stage skills remain provider-neutral and use the same layout contract.

## Components

### Presentation contract

`references/feature-layout.md` owns physical paths and recovery classification.
`references/artifact-presentation.md` owns readability and generated-section rules.

### Status/recovery library

`scripts/feature_state.py` provides shared pure functions:

- discover and fingerprint human artifacts;
- parse generated task checklist markers;
- derive task counts, evidence gaps, readiness, and next command;
- write manifest/state/status with stable serialization.

Command wrappers:

- `build_feature_status.py`: build or refresh `STATUS.md` from current state;
- `rebuild_feature_state.py`: reconstruct `_kapelle/manifest.json`, state, and recovery report;
- `validate_feature_state.py`: deterministic consistency checks;
- `migrate_feature_layout.py`: dry-run/apply legacy conversion.

The deterministic layer does not inspect arbitrary source semantics. During `/kapelle:status`, the
host agent may use native project capabilities and scoped architecture guidance to enrich recovery
evidence before invoking the scripts.

### Schemas and vocabulary

New schemas define manifest, state, and recovery report. Vocabulary adds recovery feature states and
`implemented-unverified`. Artifact dependencies extend through documentation convergence,
feature-review, and ship.

### Stage protocols

- `specify` creates `proposal.md`, `spec.md`, and `_kapelle/size.json`.
- `design` creates `design.md`, `_kapelle/surface-plan.json`, ADRs, and guidance evidence.
- `sequences` is optional and normally updates runtime flows in `design.md`.
- `decompose` creates `tasks.md` and `_kapelle/task-plan.json`.
- `implement` writes per-task evidence below `_kapelle/task-runs/` and validation below
  `_kapelle/validation/`.
- `feature-review` writes convergence/review evidence below `_kapelle/reviews/`.
- `ship` updates readiness in state/STATUS rather than creating a competing `ship.md`.

Every feature stage runs a lightweight status refresh after writing its own artifacts.

## Data flow

```text
human docs + current project evidence
              |
              v
      recover/refresh state
              |
              v
 _kapelle/manifest.json + state.json
              |
              v
          STATUS.md
```

## Recovery certainty

- Document presence and fingerprints are deterministic.
- Task checkbox state is a claim, not validation evidence.
- Existing `_kapelle/validation/*` can support `validated` only when schema-shaped, current, and
  linked to every implementation path owned by the task.
- After complete internal-state loss, checked tasks are `implemented-unverified`.
- Recovered graphs are provisional: checked work may be validated, but new code-writing waits for
  refreshed architecture guidance and decomposition.
- Missing historical evidence remains listed in `recovery.json`.

## Migration strategy

Migration first parses and semantically validates legacy graphs, change state, mappings, and
collisions. `--dry-run` is default-safe and writes nothing.
`--apply`:

- creates target directories;
- copies/renames human artifacts where unambiguous;
- derives `proposal.md` and `tasks.md` with visible migration notes;
- moves machine evidence under `_kapelle/history/legacy/`;
- rebuilds state and status;
- writes a migration marker only after rebuilt-state validation passes, so reruns are safe no-ops.

Legacy content is preserved; ambiguous collisions stop before mutation.

## Trade-offs

- Markdown remains intentionally constrained so deterministic parsing stays reliable.
- Human and machine task representations are duplicated, but validation makes drift visible and the
  machine graph remains authoritative for execution dependencies.
- `_kapelle/` is recoverable for continuation, not lossless. This improves usability without making
  false evidence claims.
- Full source-code reconciliation remains an agent responsibility because a generic deterministic
  script cannot understand every project architecture.

## Security and operations

- Paths are resolved and symlink escapes outside the feature directory are refused.
- No shell, git, network, test, or linter command is executed by status/recovery/migration scripts.
- JSON writes use temporary sibling files followed by atomic replacement.

## No data schema change

No application database is involved. This is a plugin artifact-schema change from layout 1 to
layout 2.

## Validation

- Unit tests exercise fresh layout, deleted `_kapelle/`, false checked-task and review evidence,
  source/coordination drift, symlink escape, migration preflight/apply/idempotency, and legacy
  preservation.
- Existing task-plan and plugin validation remain green.
