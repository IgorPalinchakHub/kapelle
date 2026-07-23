# Human-readable artifact contract

## Summary

Kapelle exposes a compact, durable human feature package and keeps operational state isolated under
`_kapelle/`. The status command rebuilds derived state when needed and selects the smallest safe
next step.

## Actors

- Developer following or resuming the SDLC process.
- Product/project manager reviewing scope and behavior.
- QA reviewing acceptance criteria and validation.
- Kapelle stage reading and writing feature artifacts.

## Requirements

### Human feature package

- The feature root contains human-readable Markdown only, plus `contracts/`, `adr/`, optional
  `_context/`, and `_kapelle/`.
- `proposal.md` explains why and scope.
- `spec.md` explains observable behavior and acceptance criteria.
- `design.md` explains the as-designed and as-built technical solution.
- `tasks.md` is a compact workstream checklist.
- `test-plan.md` explains validation strategy and commands.
- `STATUS.md` is a deterministic projection, not an independent source of truth.

### Internal state

- Machine-readable plans, fingerprints, agent evidence, reviews, validation results, changes, and
  telemetry are stored below `_kapelle/`.
- A manifest records layout version, slug, human artifact paths, fingerprints, and recovery state.
- A state file records stage, task counts, blockers, validation/review/ship readiness, and next
  command.

### Recovery

- Missing or invalid `_kapelle/` triggers recovery from human documents and current project
  evidence.
- Checked tasks recovered without validation evidence become `implemented-unverified`.
- Recovery must report missing evidence and must not recreate approvals, old reviews, telemetry, or
  historical command output.
- Recovery chooses the minimal next stage rather than restarting the full lifecycle.

### Compatibility

- Legacy feature layouts can be inspected with a dry-run migration.
- Apply migration is explicit and idempotent.
- Migration preserves human requirements, contracts, ADRs, and historical evidence.

### Final convergence

- Feature review checks proposal/spec/design/contracts/tasks/test-plan/ADR against implementation.
- Ship requires a current documentation-convergence `PASS` and no required deferred validation.

## Acceptance criteria

- **AC-01** A new feature layout contract names the human artifacts and confines machine-only files
  to `_kapelle/`.
- **AC-02** `/kapelle:status <slug>` rebuilds `STATUS.md` deterministically from human documents and
  internal state.
- **AC-03** When `_kapelle/manifest.json` is absent or invalid, status recovery creates a valid
  manifest and state without requiring prior chat context.
- **AC-04** Recovery maps checked tasks without durable validation evidence to
  `implemented-unverified`, never `validated`.
- **AC-05** Recovery reports which approvals, reviews, telemetry, and validation evidence could not
  be reconstructed.
- **AC-06** The recovered state chooses a minimal next command based on available documents, tasks,
  and validation gaps.
- **AC-07** Feature-state validation detects status drift, impossible readiness, stale
  review/convergence evidence after document, coordination, or implementation changes, malformed
  active change state, and false recovered validation.
- **AC-08** Design, decomposition, implementation, review, ship, and change protocols use the
  layout-v2 paths.
- **AC-09** `tasks.md` stays compact while `_kapelle/task-plan.json` retains the full validated
  dependency graph and AC coverage.
- **AC-10** A migration command supports `--dry-run` and explicit `--apply`, preserves legacy
  evidence under `_kapelle/history/legacy`, and is idempotent.
- **AC-11** Plugin validation and unit tests cover layout, status, recovery, migration, and existing
  task-plan invariants.
- **AC-12** README and usage documentation explain the normal layout, status/recovery flow,
  migration, and evidence-loss boundary.

## Non-functional requirements

- Utilities use the Python standard library and run without network access.
- Writes are scoped below the supplied feature directory.
- Generated JSON is stable and sorted; generated Markdown has a stable section order.
- No utility executes git commands or project validation commands.
- Recovery and migration fail safely on ambiguous or malformed input.

## Explicitly deferred

- Semantic inspection of arbitrary source code is performed by the host agent with project
  capabilities; the deterministic recovery script only reconstructs document-derived state.
- Automatic removal of legacy files is not required; migration archives/moves only with `--apply`.

## Open questions

None blocking. Layout-v2 is a deliberate compatibility boundary and legacy support is explicit.
