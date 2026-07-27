---
name: status
description: >
  Show or rebuild concise feature status and recover disposable `_kapelle/` state without changing
  product behavior or implementation.
---

# Skill: status

Invoke:

```text
/kapelle:status <slug>
```

## Protocol

1. Refuse with `Status: REFUSED-missing-input` when `docs/features/<slug>/` does not exist.
2. Treat `spec.md`, `design.md`, and `tasks.md` as the normal durable package. Optional promoted
   use-case specs, domain model, contracts, ADRs, detailed design, and diagrams remain durable human
   documentation and participate in approval freshness when present.
3. Recognize `<!-- kapelle-workflow: lightweight-v1 -->` in `spec.md`. When `_kapelle/` is missing
   or invalid, run:

```text
scripts/rebuild_feature_state.py docs/features/<slug>
scripts/validate_feature_state.py docs/features/<slug>
```

   Recovery may infer checked work as `implemented-unverified`; it never fabricates approvals,
   command results, reviews, or PASS evidence.
4. A `human-controlled-v1` marker or unmarked feature routes to `/kapelle:migrate <slug>`. Keep the
   reconstruction workflow documentation-only and use its existing marker/routing.
5. For lightweight features, select only the earliest necessary route:
   - new raw-task package without a valid progressive artifact format → `/kapelle:start --revise`;
   - missing package/guidance or stale plan → `/kapelle:start`;
   - approved slice with unchecked work → `/kapelle:implement`;
   - implemented slice without current PASS → show the scope decision: add the next requirement
     through `/kapelle:amend`, or run `/kapelle:verify` when accumulated behavior is sufficient;
   - PASS without final approval → `/kapelle:verify <slug> --approve`;
   - final approval → completed.
6. Show current outcome, slice progress, important blockers/deferred validation, core files plus
   any present use-case/domain/contract detail to review, the optional `amend` route when scope is
   still evolving, and one exact routed command. Do not expose historical stage internals.

This utility performs no implementation edits, validation commands, git actions, or silent
migration.
