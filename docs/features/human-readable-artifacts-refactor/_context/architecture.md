# Architecture overlay: human-readable-artifacts-refactor

Status: READY-with-explicit-self-hosting-guidance

## Scope

This refactor changes Kapelle's feature artifact contract, stage protocols, deterministic
validators, recovery utilities, migration support, and user documentation.

## Authoritative guidance

- `AGENTS.md`: artifact state, gated stages, bounded execution, no git operations, architecture
  guidance, change lifecycle, and validation policy.
- `references/stage-contract.md`: one physical path per logical artifact and resumable disk state.
- `docs/HUMAN_READABLE_ARTIFACTS_REFACTOR_PLAN_UK.md`: approved target layout and recovery
  invariants.
- Existing schemas and validators under `dispatcher/` and `scripts/`.

## Current boundaries

- `skills/*/SKILL.md` define provider-neutral stage behavior.
- `references/*.md` define shared cross-stage contracts.
- `dispatcher/*.json` define machine-readable state and vocabulary.
- `scripts/*.py` provide deterministic validation.
- `README.md` and `docs/*.md` are user-facing documentation.

## Architecture-rules capability

No project-native architecture-rules subagent is present in this plugin repository. This is a
readiness gap for normal Kapelle project use. For this self-hosted refactor only, the user-approved
plan plus `AGENTS.md` and the existing contracts are explicit authoritative guidance. No generic
framework conventions are being substituted for missing project rules.

## Relevant precedents

- `scripts/validate_task_plan.py` keeps graph and AC correctness deterministic.
- `dispatcher/vocabulary.json` is the canonical state vocabulary.
- `references/stage-contract.md` is the single stage contract.
- `skills/survey/SKILL.md` already separates shared baseline from feature-local context.

## Constraints

- Human documents remain durable and reviewable after `_kapelle/` is removed.
- Machine state moves under `_kapelle/`; lost approvals and validation evidence are not recreated.
- Legacy layouts remain readable through an explicit migration/recovery path.
- No runtime routing table or provider-specific model policy is introduced.
- No git command is added to any Kapelle protocol or utility.

