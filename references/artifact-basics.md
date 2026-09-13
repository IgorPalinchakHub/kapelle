# Compact feature artifacts

Map known behavior at high level; detail only the approved slice. For a small change, one sentence
per applicable section is enough. No questionnaires, diagrams, ADRs or additional files by default.

## spec.md

Begin with these markers, then the headings in order:

```md
<!-- kapelle-workflow: lightweight-v1 -->
<!-- kapelle-artifacts: progressive-map-v1 -->
<!-- kapelle-artifact-contract: living-v1 -->
# Feature specification
## 1. Problem and intent
## 2. Current behavior
## 3. Committed behavior
### Intended change
### Resulting behavior
### Preserved behavior
### Acceptance scenarios
## 4. Use-case map
## 5. Business rules and invariants
## 6. Candidate capabilities
## 7. Exclusions, assumptions, and open decisions
```

Current behavior is evidence-backed as-built behavior, not the requested result. State the observable
change, compatibility, and at least one success scenario using `AC-NN` and concise Given/When/Then.
Add only applicable failure, permission, invariant and interaction scenarios. Every committed
outcome has coverage. Candidates are hypotheses until promoted through amend. Keep unknowns explicit.
For a new isolated capability say when no prior behavior exists. Sections remain non-empty.

## design.md

```md
# System design
## 1. Context and constraints
## 2. System boundaries and responsibilities
### Current architecture
### Resulting architecture
### Technical delta
## 3. End-to-end flow
## 4. Domain and data
## 5. Contracts and integrations
## 6. Decisions, risks, and deferrals
## 7. Current walking skeleton
```

Explain affected ownership and the coherent usable path. Candidate architecture stays directional.
For refactors, make preserved public behavior explicit in spec.md. Reuse applicable project quality
defaults; record only decision-changing constraints and their verification. Never invent targets.

## tasks.md

Use one active workstream; at most three when needed for reviewability:

```md
# Tasks
- [ ] **W1 Deliver the outcome — covers AC-01**
  - Changes: affected behavior and technical areas.
  - Done when: observable completion signal.
  - Verify: smallest useful evidence.
```

Every active AC must be covered by active work; no unknown AC references. Preserve completed history.
Only basic or critical tests belong early; all remaining tests belong at verify. Do not add a DAG,
layer tasks, estimates or test stages for a small change. Internal identifiers stay out of questions.
Soft ceilings: spec 250, design 180, tasks 120 lines; hard root-document caps: spec 320 and design 240 lines.

## Conditional detail and completion

Read [progressive-artifacts.md](./progressive-artifacts.md) only for independently useful use-case,
domain, contract, aspect, ADR or diagram detail, changed quality constraints, or their final review.
At verify, reconcile current behavior, architecture, all implemented scenarios and their evidence.
Add detail only when its normal trigger applies; intent changes route through amend.
Structural validation checks shape, not correctness. Revisions add missing living-contract structure
without rewriting unrelated historical work; unmarked existing packages remain compatibility input.
