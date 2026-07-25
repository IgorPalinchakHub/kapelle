---
name: status
description: >
  Show or rebuild a feature's human-readable status and recover missing `_kapelle/` state without
  implementing code.
---

# Skill: status

Build the feature entry point, recover disposable execution state when needed, and select the
smallest safe next command.

## Inputs

- `<slug>` and `docs/features/<slug>/`.
- Human artifacts that currently exist: `proposal.md`, `spec.md`, `design.md`, `tasks.md`,
  `test-plan.md`, contracts, ADRs, and optional sequences.
- Optional `_kapelle/` state and current project implementation evidence.
- Layout contract: [`../../references/feature-layout.md`](../../references/feature-layout.md).
- Presentation contract:
  [`../../references/artifact-presentation.md`](../../references/artifact-presentation.md).
- Architecture guidance:
  [`../../references/architecture-guidance.md`](../../references/architecture-guidance.md).

## Protocol

1. Refuse with `Status: REFUSED-missing-input` if the feature directory does not exist. Do not
   create a speculative feature or guess a slug.
2. Read the human artifacts directly from disk. Validate `_kapelle/manifest.json` and
   `_kapelle/state.json` when they exist.
3. If internal state is missing, partial, corrupt, or layout-incompatible:
   - inspect only current implementation and tests relevant to the documented feature scope;
   - semantically discover the project architecture-rules subagent for the affected
     modules/entrypoints and persist current guidance under `_kapelle/architecture-guidance/`;
   - run `scripts/rebuild_feature_state.py docs/features/<slug>`;
   - reconcile documented tasks with current code evidence;
   - keep checked work without trustworthy current validation as `implemented-unverified`;
   - list approvals, reviews, command output, telemetry, or validation evidence that could not be
     reconstructed.
4. Recognize both durable markers:
   `<!-- kapelle-workflow: human-controlled-v1; lane: fast|standard -->` and
   `<!-- kapelle-workflow: reconstruction-v1 -->`. Rebuild reconstruction routing from
   `proposal.md`, `_context/evidence-index.md`, human specification/design documents, and current
   evidence without routing it to development. When neither marker exists, route only to
   `/kapelle:migrate <slug>`. When legacy root JSON, `_audit/`, `_review/`, `changes/`, `sad.md`,
   `.size`, or `ship.md` is detected, also show the layout migration dry-run. Do not apply either
   migration without explicit approval.
5. Treat `_kapelle/approvals/feature-outline.json` and `business-specification.json` as invalid
   aliases. Report the canonical `outline.json` or `business-spec.json` gate as missing and route
   to its prior approval stage; never reinterpret or rename narrative evidence silently.
6. Run `scripts/build_feature_status.py docs/features/<slug>` and then
   `scripts/validate_feature_state.py docs/features/<slug>`.
7. If validation finds drift, repair only generated/derived state from current evidence. Do not
   modify product requirements or implementation code from this utility.
8. Report the feature state, blockers/evidence gaps, readiness, and exact minimal next command.

## Output

- Refreshed `docs/features/<slug>/STATUS.md`.
- Rebuilt `_kapelle/manifest.json`, `_kapelle/state.json`, and `_kapelle/recovery.json` when needed.
- `Status: DONE | stage: status | produced: <paths> | next: <command>`.

## Definition of Done

- `STATUS.md` matches `_kapelle/state.json`.
- Missing historical evidence is explicit.
- Recovery did not report unchecked evidence as validated.
- The next command starts at the earliest genuinely missing/stale stage, not at the beginning by
  default.

## Prohibited actions

- Implementation edits.
- Tests, linters, static analysis, builds, or migrations.
- Git operations.
- Silent workflow or layout migration.
- Fabricating approvals, reviews, or validation evidence.
