---
name: spec
description: >
  Expand or revise a standard-lane feature outline into a complete business specification using
  size-aware interview depth and bounded adversarial analysis.
---

# Skill: spec

Invoke:

```text
/kapelle:spec <slug> [--interview=auto|lean|standard|deep]
/kapelle:spec <slug> --revise "<developer feedback>"
/kapelle:spec <slug> --approve
```

Read [`../../references/interview-depth.md`](../../references/interview-depth.md).

## Protocol

1. Require `proposal.md`, `spec.md`, `_kapelle/workflow.json`, and standard lane. Fast-lane
   features are revised through `/kapelle:start <slug> --revise`.
2. The first normal invocation explicitly accepts the outline. Before expanding `spec.md`, run
   `scripts/review_gate.py approve docs/features/<slug> outline --confirmation "Developer invoked
   the specification stage and explicitly accepted the feature outline."`. The outline gate
   fingerprints stable `proposal.md`, so expanding `spec.md` does not invalidate it.
3. Resolve `auto` from `_kapelle/size.json` and risk evidence:
   - lean: inline consistency challenge, no critic/devil dispatch;
   - standard: business analysis plus one combined critic pass;
   - deep: business analyst, separate critic, separate devil's advocate.
   Never reduce behavioral coverage; allow one correction pass.
4. Cover actors, triggers, main/alternative flows, rules, validations, subprocesses, component
   reactions, failures, retry/idempotency, permission, compatibility, and measurable ACs.
5. Keep `spec.md` as the overview. Create only independently useful `specs/scenarios.md`,
   `business-rules.md`, `integrations.md`, or subprocess files.
6. On `--revise`, invalidate the business gate and all downstream evidence.
7. On `--approve`, require a complete package and run
   `scripts/review_gate.py check docs/features/<slug> outline`. After explicit confirmation, run
   `scripts/review_gate.py approve docs/features/<slug> business-spec --confirmation "Developer
   explicitly approved the complete business specification."`. Never generate missing specs or
   construct approval JSON during approval. Hand off to `/kapelle:design <slug>`.
8. Do not choose components, fields, endpoints, or implementation tasks.

Return changed decisions, selected interview depth, files to review, unresolved questions, and the
exact revise/approve command. Refresh status only through deterministic helpers; never hand-edit
manifest, state, status, or approval JSON. Use the standard handoff block. Never run git
operations.
