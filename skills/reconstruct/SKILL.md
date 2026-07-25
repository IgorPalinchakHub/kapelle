---
name: reconstruct
description: >
  Reverse-engineer an existing feature into evidence-backed hierarchical product and as-built
  architecture documentation, with explicit scope, review, and approval gates. Use when current
  code exists but its business behavior, product specification, or architecture design is missing
  or stale.
---

# Skill: reconstruct

Document an existing feature from current code without changing production behavior.

## Commands

```text
/kapelle:reconstruct <slug> "<feature scope>"
/kapelle:reconstruct <slug> --approve
/kapelle:reconstruct <slug> --spec
/kapelle:reconstruct <slug> --design
/kapelle:reconstruct <slug> --review
```

`--approve` approves whichever reconstruction draft `STATUS.md` currently identifies. It never
generates the next phase in the same invocation.

## Inputs

- `<slug>` and, for the first invocation, a bounded feature scope.
- Current repository code, configuration, schemas, tests, migrations, and project documentation.
- Shared or feature-local repository context when available.
- [`../../references/reconstruction.md`](../../references/reconstruction.md).
- [`../../references/agent-orchestration.md`](../../references/agent-orchestration.md).
- [`../../references/project-capabilities.md`](../../references/project-capabilities.md).
- [`../../references/architecture-guidance.md`](../../references/architecture-guidance.md).
- [`../../references/design-template.md`](../../references/design-template.md).
- [`../../references/artifact-presentation.md`](../../references/artifact-presentation.md).

## Common protocol

1. Refuse with `Status: REFUSED-missing-input` when the slug, initial scope, current required
   approval, or prior phase artifact is missing. Never guess a feature boundary.
2. Refuse to overwrite a feature directory owned by another workflow. A reconstruction directory
   has `<!-- kapelle-workflow: reconstruction-v1 -->` in `proposal.md` and
   `"workflow": "reconstruction"` in `_kapelle/workflow.json`.
3. Discover applicable project skills and subagents semantically. Dispatch selected project
   subagents to discover narrower native capabilities where useful.
4. Discover the project's architecture-rules subagent for the current aspects, modules,
   entrypoints, and paths. Persist its response under `_kapelle/architecture-guidance/`. A missing
   capability is an explicit readiness gap, never an invented rule.
5. Use `kapelle:explorer` for cited repository evidence and `kapelle:business-analyst` for
   observable product behavior. Use `kapelle:critic` and a fresh `kapelle:reviewer` at review.
6. Keep exploration bounded and sequential by default. For a large multi-aspect feature, dispatch
   at most one read-only exploration slice per coherent aspect, with a maximum of five; one
   coordinator owns synthesis and removes contradictions.
7. Classify every material claim as `observed`, `inferred`, `declared`, or `unknown`; give it a
   stable `RC-NNN` id and cite exact repository-relative source lines where evidence exists.
8. Write only under `docs/features/<slug>/`. Never edit implementation, tests, configuration, or
   migrations; never run development validation commands; never perform git operations.
9. Rebuild `STATUS.md` with `scripts/build_feature_status.py docs/features/<slug>` after every
   phase or approval.

## Initial scope phase

1. Inspect only enough repository topology and entrypoints to bound the feature.
2. Separate included behavior, excluded behavior, aspects, entrypoints, actors, and unknowns.
3. Create:
   - `proposal.md` with the durable reconstruction marker, summary, scope, non-goals, evidence
     limits, and open questions;
   - `_context/evidence-index.md` with the claim/source index;
   - `_kapelle/workflow.json` conforming to `workflow-state.schema.json`;
   - `_kapelle/reconstruction.json` conforming to `reconstruction.schema.json`.
4. Stop for scope review. Handoff to `/kapelle:reconstruct <slug> --approve`.

## Approval mode

1. Read `_kapelle/state.json` and approve only its current reconstruction gate:
   `reconstruction-scope`, `reconstruction-spec`, `reconstruction-design`, or `reconstruction`.
2. Require explicit confirmation in this invocation.
3. Run `scripts/review_gate.py approve docs/features/<slug> <gate> --confirmation "<explicit
   developer confirmation>"`. The helper derives the canonical filename and exact artifact set,
   writes the strict gate schema, and refreshes status. Never construct approval JSON manually.
4. Refuse final approval when reconstruction review is missing, stale, or `BLOCKED`.
5. Rebuild status and hand off to the next reconstruction command. Never hand off to development.

## Product specification phase (`--spec`)

1. Require current `reconstruction-scope` approval.
2. Trace entrypoints through permissions, validations, domain transitions, persistence, external
   effects, failure handling, retry/idempotency, and user-visible outcomes.
3. Treat tests as behavioral evidence and project prose as declared intent; do not convert either
   into unsupported product rationale.
4. Write:
   - `spec.md` as the high-level product/business map;
   - at least one independently useful `specs/*.md` detail document, split by scenario, rule set,
     subprocess, or integration behavior;
   - updated `_context/evidence-index.md`.
5. Acceptance criteria describe reconstructed observable behavior and link to claim ids. Unknowns
   stay explicit.
6. Stop for review and hand off to `/kapelle:reconstruct <slug> --approve`.

## Architecture design phase (`--design`)

1. Require current `reconstruction-spec` approval.
2. Ask the architecture-rules subagent for scoped rules and applicable project capabilities before
   synthesis.
3. Trace all relevant aspects together, including backend, frontend, workers, data, contracts, and
   integrations when present. Record shared contracts and dependencies in
   `_kapelle/surface-plan.json`; do not route agents through that file.
4. Write `design.md` with all headings from `design-template.md`, explicitly labelling As-built,
   Rule, and Deviation statements.
5. Write at least one independently useful `design/*.md` detail document. Add `contracts/*.md` only
   for interfaces that benefit from separate review.
6. Run `scripts/validate_design.py docs/features/<slug>/design.md`. Stop for review and hand off to
   `/kapelle:reconstruct <slug> --approve`.

## Evidence review phase (`--review`)

1. Require current `reconstruction-design` approval.
2. Dispatch `kapelle:critic` for contradictions and a fresh `kapelle:reviewer` for coverage across
   scope, product behavior, architecture, project rules, contracts, tests, unknowns, and
   business-to-design traceability.
3. Verify each observed/inferred claim has cited sources, all citations are inside the repository,
   source lines support the claim, detail documents are linked from their overview, and
   architecture deviations are explicit.
4. Write `_kapelle/reconstruction-coverage.json` conforming to
   `reconstruction-coverage.schema.json`. Fingerprint every cited source and generated artifact.
5. Use:
   - `PASS` when there are no material gaps;
   - `PASS-WITH-GAPS` when gaps are explicit and the package remains useful;
   - `BLOCKED` when a material contradiction or unsupported claim makes the package misleading.
6. Stop for final human review. Handoff to `/kapelle:reconstruct <slug> --approve`.

## Definition of Done

- Scope, product specification, and architecture design approvals are current.
- `spec.md` plus `specs/*.md` describe observable business/product behavior.
- `design.md` plus `design/*.md` describe the as-built architecture and its rule deviations.
- Every material claim is classified and evidence-linked.
- Reconstruction review is current and final explicit approval is current.
- `STATUS.md` reports `documented`; release and ship readiness remain false.

## Stage handoff

Use the standard handoff format, with `reconstruct` as the stage and the exact next reconstruction
command. After final approval, `Run next` is `/kapelle:status <slug>`.
