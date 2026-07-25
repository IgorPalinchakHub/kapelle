---
name: finalize
description: >
  Finalize a developer-approved Kapelle feature by reconciling as-built specifications, running
  clean-context review, generating feature and architecture diagrams, and recording version 1.0.
---

# Skill: finalize

Invoke:

```text
/kapelle:finalize <slug> --version=1.0
```

## Protocol

1. Require current PASS verification, no deferred required checks, no active amendment, and no
   unresolved blocking decision.
2. Require explicit developer confirmation that manual testing and debugging are complete. Silence
   is not confirmation.
3. Reconcile current implementation against proposal, business specs, design subdocuments,
   domain/status models, contracts, tasks, test plan, and ADRs.
4. Do not regenerate documentation from scratch or rewrite requirements to match accidental code.
   Any observable mismatch routes to `/kapelle:amend`.
5. Dispatch `kapelle:reviewer` in fresh read-only context and require PASS across all aspects,
   contracts, functional behavior, unit coverage, verification, and project architecture rules.
6. Generate diff-friendly diagram sources:
   - `diagrams/feature-flow.mmd`;
   - `diagrams/architecture.mmd`.
   Use C4/PlantUML or Draw.io only when a project capability and developer preference justify it.
7. After diagrams exist and explicit confirmation is present, run
   `scripts/review_gate.py approve docs/features/<slug> final --confirmation "Developer confirmed
   manual testing and explicitly approved the final as-built result."`. Never construct approval
   JSON manually.
8. Write `_kapelle/release.json` matching `release.schema.json`, with the requested version and
   current document and verified implementation fingerprints.
9. Mark the feature `completed`, refresh `STATUS.md`, and report the final human documentation.

Kapelle does not commit, tag, push, merge, or create a pull request. It never hand-edits manifest,
state, status, or approval JSON.

Use the standard backbone handoff block from `references/handoff.md`.
