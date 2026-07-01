# Shared Stage Contract

Each stage declares its required inputs and outputs.

Protocol:

1. Check required artifacts on disk.
2. If missing, refuse with `Status: REFUSED-missing-input | missing: <path> | run-first: <stage>`.
3. Read inputs from disk. Do not depend on previous chat context.
4. Produce only the stage's own artifact(s).
5. Emit the stage-handoff block.

Normal feature development uses presence gates only. Fingerprint freshness is activated only for an
approved existing-feature change, where a revision and dependency graph define what "current"
means. Stages must not invent an ad-hoc stale check.

Each logical artifact has one physical path in `dispatcher/artifact-dependencies.json`. A stage must
not hide its state in a section owned by another stage. An inapplicable stage writes its normal
artifact with `Status: SKIPPED-confirmed` and the evidence instead of omitting the file.

When invoked with `--change=<change-id>`:

1. Read `docs/features/<slug>/changes/<change-id>/change.json` and its baseline.
2. Refuse if the current stage is absent from the approved route.
3. Restrict reads and edits to the approved impact matrix.
4. Update canonical feature artifacts in place; do not create a parallel source of truth.
5. Recompute produced-artifact fingerprints, update lineage sidecars, and clear `stale` only when
   the artifact was regenerated against the current revision.
6. Append stage status and produced paths to the change `progress.jsonl`.
7. Stop for renewed approval if an unapproved impact is discovered.

This mirrors `stages/_stage-contract.md`, but is short enough to load with each Claude Code skill.
