---
name: verify
description: >
  Run complete post-implementation verification for a Kapelle feature across functional, unit,
  integration, contract, static-analysis, lint, and build checks with explicit user control.
---

# Skill: verify

Invoke:

```text
/kapelle:verify <slug> [--validation=ask|allow|skip]
```

## Protocol

1. Require `_kapelle/unit-tests.json` with current inputs and no unresolved production task.
2. Build one exact validation batch from project-native commands:
   - base and full functional tests;
   - unit tests;
   - integration and contract tests;
   - static analysis;
   - linters/format checks;
   - build checks.
3. Label every command required or optional and show scope.
4. Under `ask`, require `run-all`, `run-selected`, or `skip-all`. Under `allow`, run the batch.
   Under `skip`, execute none.
5. Required failed, skipped, or cancelled checks produce `FAILED` or `validation-deferred`; never
   PASS.
6. Persist task validation evidence for the complete implementation inventory and write
   `_kapelle/verification.json` matching `verification.schema.json`, including fingerprints for
   every production and test file in the verified feature inventory.
7. Run `scripts/validate_json.py docs/features/<slug>/_kapelle/verification.json
   dispatcher/verification.schema.json`. On non-zero exit, refuse completion and correct the
   artifact once; never validate it by visual comparison with the schema.
8. When behavior is wrong, hand off to developer testing or `/kapelle:amend`. When all required
   checks pass, refresh status and hand off to:

```text
/kapelle:finalize <slug> --version=1.0
```

`finalize` still requires explicit developer confirmation after manual testing.

Use the standard backbone handoff block from `references/handoff.md`.
