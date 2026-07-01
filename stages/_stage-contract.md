# Gated-stage backbone (the cli-surface contract every stage shares)

Every Kapelle stage is a gated, resumable, artifact-driven step (ADR-0007, sad Flow 5).
This contract is the shared backbone all stages in `kapelle/stages/` follow; a concrete stage
(e.g. `specify`, `design`, `contracts`) declares its own required inputs and fills in its body.

## A stage declares

- **`requires`** — the prior-stage artifact(s) it reads, by on-disk path
  (e.g. `contracts` requires `docs/features/<slug>/data-model.md`).
- **`produces`** — the artifact(s) it writes (its own on-disk state).
- **`prior_stage`** — the name of the stage that produces each required artifact (used in the refusal message).

## Dispatch protocol (the gate)

1. **Presence-check** every `requires` artifact on disk.
2. **Absent → REFUSE (AC-07).** Do not run. Emit a refusal that **names the prior stage to run first**:
   `Status: REFUSED-missing-input` · `missing: <path>` · `run-first: <prior_stage>`. Write nothing.
3. **Present → RESUME (AC-08).** Read the inputs **from disk** and proceed. Do **not** re-run any earlier
   stage — a `/clear`-ed context resumes purely from on-disk state. Normal feature work uses a
   presence check. Approved existing-feature changes additionally use revision fingerprints from
   `references/change-lifecycle.md`; no stage invents another stale heuristic.
4. Run the stage body; write `produces` to disk.

## Invariants

- **Artifact-is-state.** A stage's only durable state is the files it writes; nothing lives in conversation.
- **One logical artifact, one physical path.** Stage state is never hidden in another stage's file.
- **Writing/overwriting the stage's OWN artifacts is NOT an irreversible action** (ADR-0007) — it needs no
  developer hand-off. (Any *other* irreversible action is governed by the no-git guard — see
  [`./_irreversible-guard.md`](./_irreversible-guard.md), T14.)
- **One-way control.** A stage calls skills / subagents / tools; a skill never calls back up into a stage.
- **Confirmed-skips-never-silent.** An inapplicable stage writes its normal artifact with
  `Status: SKIPPED-confirmed` and evidence; a refusal always names the prior stage.

## Status lines (parsed by the caller)

- `Status: REFUSED-missing-input` · `missing: <path>` · `run-first: <prior_stage>`
- `Status: RESUMED` · `read: <paths>` · `re-ran-prior: none`
- `Status: DONE` · `produced: <paths>`

## Builds on this

- **T14** — the no-git / irreversible-action guard (declines git or destructive ops outside own artifacts).
- **T15** — the contracts stage (iterates entrypoints, injects a generator by kind).
