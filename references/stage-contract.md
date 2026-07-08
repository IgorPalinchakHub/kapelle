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
5. Emit the stage-handoff block.

Normal feature development uses presence gates only. Fingerprint freshness is activated only for an
approved existing-feature change, where a revision and dependency graph define what "current"
means. Stages must not invent an ad-hoc stale check.

Each logical artifact has one physical path in `dispatcher/artifact-dependencies.json`. A stage must
not hide its state in a section owned by another stage. An inapplicable stage writes its normal
artifact with `Status: SKIPPED-confirmed` and the evidence instead of omitting the file.

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

1. Read `docs/features/<slug>/changes/<change-id>/change.json` and its baseline.
2. Refuse if the current stage is absent from the approved route.
3. Restrict reads and edits to the approved impact matrix.
4. Update canonical feature artifacts in place; do not create a parallel source of truth.
5. Recompute produced-artifact fingerprints, update lineage sidecars, and clear `stale` only when
   the artifact was regenerated against the current revision.
6. Append stage status and produced paths to the change `progress.jsonl`.
7. Stop for renewed approval if an unapproved impact is discovered.
