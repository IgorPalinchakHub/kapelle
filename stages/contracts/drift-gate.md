# Per-contract drift gate (vs the shared model)

Gates each candidate contract from the [contracts stage](./contracts.stage.md) (T15) against the feature's
**shared data model** (`docs/features/<slug>/data-model.md`). Keeping per-entrypoint contracts re-introduces
a divergence risk (spec §6.1, §11); this gate is what stops a contract silently diverging from a consumer's
expectations (AC-13, sad Flow 7, ADR-0008). Each entrypoint's contract is gated **independently** — one bad
kind blocks only its own contract.

## The check (per candidate contract)

Compare every field the contract exposes against the shared model:

| Contract vs model | Verdict |
|---|---|
| Field type **contradicts** the model's type for that field | **BLOCK** |
| Contract **omits** a field the model marks **required** | **BLOCK** |
| Contract **adds** a field the model doesn't have, and it is **optional** | **ALLOW** (compatible extension) |
| Contract matches the model (subset of model fields, compatible types) | **ALLOW** |

## Block protocol

```
Status: CONTRACT-DRIFT-BLOCKED
entrypoint: <kind>
invariant: "each entrypoint contract must stay consistent with the shared model"
violations:
  - field <name>: contract type <X> contradicts model type <Y>
  - field <name>: required by the model, omitted by the contract
```

Finalization of **that** contract is blocked; other entrypoints' contracts proceed on their own merits.
A passing candidate is written to `docs/features/<slug>/contracts/` (the stage's `produces`).

## Boundary cases (from the test plan)

- Contract contradicts a field type → **blocked** (AC-13).
- Contract omits a model-required field → **blocked** (AC-13).
- Contract adds only **optional** fields → **allowed** (AC-13 boundary — a compatible extension).

## Deferred (spec §8)

*Intentional* divergence (e.g. a frozen legacy interface vs a newer one) is a deferred open question — v1
**blocks all incompatible divergence**; an intentional-divergence allowance is out of scope.

## Invariants

- **Block contradiction or omission; allow optional extension.**
- **Name the invariant** on every block (consistent, parseable).
- **Per-entrypoint isolation** — contracts are gated one at a time, independently.
