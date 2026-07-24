---
name: unit-tests
description: >
  After all production tasks are implemented, plan and write unit tests for changed and new units,
  run them under explicit validation policy, and record complete post-implementation evidence.
---

# Skill: unit-tests

Invoke:

```text
/kapelle:unit-tests <slug> [--validation=ask|allow|skip]
```

## Protocol

1. Refuse while any production task is `pending`, `in-progress`, `blocked`, `stale`, or
   `needs-rework`. All production behavior must first be implemented.
2. Read implementation records and the complete changed-file inventory.
3. Discover project-native unit-test skills, conventions, fixtures, and commands.
4. Assess testable units and business branches:
   - domain/business decisions;
   - use-case orchestration;
   - transformations and calculations;
   - failure/retry/idempotency rules;
   - adapters only where isolated behavior is valuable.
5. Write a concise internal unit-test plan, then dispatch `kapelle:test-author` to create all
   selected unit tests. Do not rewrite product behavior to satisfy a test.
6. Run the unit-test batch under `ask | allow | skip`.
7. If a test reveals a product/design defect, stop with `NEEDS-AMENDMENT` and propose
   `/kapelle:amend`; do not silently change approved behavior.
8. Write `_kapelle/unit-tests.json` matching `unit-test-run.schema.json`. Fingerprint the
   post-implementation human documents plus structural task plan; include the complete
   implementation-file inventory in `implementation_fingerprints`.
9. Refresh status and hand off to `/kapelle:verify <slug> --validation=ask`.

Unit tests are intentionally written in this phase, never during `/kapelle:implement`.

Use the standard backbone handoff block from `references/handoff.md`.
