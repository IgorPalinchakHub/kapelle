# Shared Stage Contract

This is the single canonical stage contract. Every Kapelle stage is a gated, resumable,
artifact-driven step that declares:

- **`requires`** — the prior-stage artifact(s) it reads, by on-disk path;
- **`produces`** — the artifact(s) it writes (its own on-disk state);
- **`prior_stage`** — the stage that produces each required artifact (used in the refusal message).

Protocol:

1. Presence-check every required artifact on disk.
2. If missing, refuse with `Status: REFUSED-missing-input | missing: <path> | run-first: <stage>`.
   Write nothing.
3. Read inputs from disk. Do not depend on previous chat context and do not re-run any earlier
   stage — a `/clear`-ed context resumes purely from on-disk state.
4. Produce only the stage's own artifact(s).
5. Refresh `_kapelle/manifest.json`, `_kapelle/state.json`, and generated `STATUS.md`.
6. Emit the stage-handoff block in chat; do not append it to a human feature artifact.

The single human-controlled workflow uses deterministic fingerprints for explicit approvals and
phase evidence. An unmarked feature is routed to `migrate`, never to a second stage graph. Task
checkbox/status changes use structural fingerprints so progress does not invalidate an approved
plan. Amendments use revision fingerprints and the dependency graph.

Review gates are written only by `scripts/review_gate.py`. It derives the exact canonical filename
and artifact set from `dispatcher/artifact-dependencies.json`, writes the strict
`review-gate.schema.json` shape with full SHA-256 values, and refreshes generated status. Stages
must check the required gate through this helper and must never accept aliases or narrative gate
JSON.

Each logical artifact has one physical path in `dispatcher/artifact-dependencies.json`.
Human-readable artifacts are durable state. `_kapelle/` contains derived execution state and
historical evidence; it can be rebuilt for continuation, but deleted approvals, reviews, command
output, validation results, and telemetry are never invented. An inapplicable optional stage
records `SKIPPED-confirmed` in `_kapelle/state.json`.

Writing or overwriting the stage's own artifacts is not an irreversible action. Any other
irreversible action is governed by [`../stages/_irreversible-guard.md`](../stages/_irreversible-guard.md).
Control flow is one-way: a stage calls skills, subagents, and tools; a skill never calls back up
into a stage.

Status lines parsed by the caller:

- `Status: REFUSED-missing-input | missing: <path> | run-first: <prior_stage>`
- `Status: RESUMED | read: <paths> | re-ran-prior: none`
- `Status: DONE | produced: <paths>`

Normal feature stages write only below `docs/features/<slug>/`. Shared repository artifacts such as
`docs/architecture-map.md` are never refreshed from branch drift; see
[`repository-context.md`](./repository-context.md).

When invoked with `--change=<change-id>`:

1. Read `docs/features/<slug>/_kapelle/changes/<change-id>/change.json` and its baseline.
2. Refuse if the current stage is absent from the approved route.
3. Restrict reads and edits to the approved impact matrix.
4. Update canonical feature artifacts in place; do not create a parallel source of truth.
5. Recompute produced-artifact fingerprints, update lineage sidecars, and clear `stale` only when
   the artifact was regenerated against the current revision.
6. Append stage status and produced paths to the change `progress.jsonl`.
7. Stop for renewed approval if an unapproved impact is discovered.

Before any feature stage, a missing or invalid `_kapelle/manifest.json` triggers the recovery
protocol in `skills/status/SKILL.md`. Recovery selects the earliest genuinely missing or stale
stage; it does not restart the pipeline by default.
