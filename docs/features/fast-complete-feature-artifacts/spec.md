<!-- kapelle-workflow: lightweight-v1 -->
<!-- kapelle-artifacts: progressive-map-v1 -->
<!-- kapelle-artifact-contract: living-v1 -->
# Feature specification

## 1. Problem and intent

Kapelle must keep its fast, human-controlled vertical-slice workflow while leaving behind a clear
and complete description of the implemented feature. A developer or a later LLM session should be
able to understand current user behavior, the implemented change, the resulting technical flow,
and the important verification without recovering decisions from chat history.

The improvement must increase artifact precision without adding mandatory public stages, long
interviews, speculative design, or a fixed document bundle for every small change.

## 2. Current behavior

Kapelle currently writes a compact high-level `spec.md`, `design.md`, and `tasks.md`. It can add a
detailed use-case specification, domain model, contract, sequence, aspect design, or ADR when an
existing trigger applies. `/kapelle:verify` reconciles those documents with confirmed code.

New and explicitly revised packages now use the compact living-artifact contract. Brownfield
amendments record the current flow before the change and result; refactoring records current and
resulting affected architecture plus the technical delta. Verification owns final as-built
convergence, and compatibility packages remain valid until revised.

Developer questions now recommend an evidence-backed option first, normally offer two choices, and
use short decision-focused code only when it clarifies an API, schema, control-flow, or compatibility
choice. Diagrams are zero-by-default, evidence-triggered, Mermaid-based, explained in prose, and
reconciled with as-built code. Living packages require identified acceptance scenarios, compact
workstream coverage, and focused verification; deterministic validation rejects missing, unknown,
and uncovered active scenarios.

Planning now reviews applicable failure and quality concerns within the existing package. Detailed
use cases state postconditions and branch points; final verification maps their outcomes to actual
evidence. Dialogue explains current behavior, proposals, and consequences before links. Only basic
or concretely important tests are added early; remaining tests stay at verify. The public route is
unchanged and simple improvements retain one workstream. Maintainer drafting scenarios exercise
these decisions without claiming full agent-stage or production execution.

## 3. Committed behavior

### Intended change

Strengthen requirement and design completeness inside the existing compact slice. Explain decisions
with current behavior, proposed behavior, and consequences; review applicable failure and quality
concerns without extending the public workflow. Before implementation, add only basic or genuinely
important tests; all remaining tests stay at final verification.

### Resulting behavior

- Planning checks applicability of success, failures, permissions, invariants, and interactions.
  Only relevant scenarios become requirements; unrelated categories may be dismissed together.
- Architecturally significant quality requirements state context, agreed target, design response,
  and suitable verification. Unknown targets remain unknown; numbers are never invented.
- Detailed use cases explain success/failure postconditions and alternatives at their branch point.
- Decisions, review packets, and handoffs briefly explain what exists, what is proposed or changed,
  and why it matters before offering supporting artifact links.
- Simple improvements use the existing root documents and one workstream; no extra public stage,
  questionnaire, mandatory diagram, ADR quota, or per-criterion test-level approval is introduced.
- Early testing reuses existing coverage first, adding only basic boundary/characterization evidence
  or a narrowly justified test of a high-consequence rule. Remaining tests are written at verify.
- Small behavior-evaluation scenarios cover simple work, risky integration, and refactoring without
  making model-driven evaluation a required stage for downstream projects.

### Preserved behavior

- Human documents remain the readable review surface; no mandatory machine graph, owner, estimate,
  file inventory, or microtask layer is added.
- Identifiers never appear in developer questions or require the developer to decode an internal
  blocker or gate.
- Candidate capabilities and high-level use-case-map items remain outside active traceability.
- Existing artifact markers, headings, structural validators, AC coverage, and approval gates remain
  compatible. Explicit approvals and deferred-validation reporting remain required.

### Acceptance scenarios

- **AC-19** Given a simple local improvement, planning stays in the existing root package with one
  workstream and asks no question whose answer is already supported by the request or repository.
- **AC-20** Given a decision requiring user input, the message explains current behavior, the
  proposal, and its consequence without requiring the reader to open a paragraph or decode IDs.
- **AC-21** Given applicable failure, permission, invariant, or cross-component behavior, the slice
  names the observable outcome; absent concerns do not generate fictional requirements.
- **AC-22** Given a quality requirement that affects architecture, the design links its evidenced
  target and operating context to a decision and appropriate verification; unknowns stay explicit.
- **AC-23** Given a detailed use case with a failed or repeated operation, its alternatives identify
  the relevant step, resulting state, and applicable retry or partial-completion behavior.
- **AC-24** Given implementation work, existing tests are reused and only basic or high-consequence
  coverage is added early with a reason; remaining tests are deferred to verify without duplication.
- **AC-25** Given final verification, active root/detail scenarios are reconciled with concrete
  evidence; behavioral eval fixtures check simple, integration, and refactoring decisions separately
  from deterministic structural validation and never claim an unexecuted model run passed.

## 4. Use-case map

- **Prepare a new feature slice** — describe the first usable outcome with current, resulting, and
  preserved behavior at proportional depth.
- **Change an existing feature** — inspect the as-built flow, describe the delta, and update only
  affected specifications and design.
- **Plan a behavior-preserving refactor** — contrast current and target affected architecture while
  making compatibility and behavior-preservation obligations explicit.
- **Complete living documentation** — reconcile user and technical specifications with confirmed
  code during verification.
- **Ask a technical decision question** — show a recommendation, trade-offs, and a short code
  example only when it materially clarifies the choice.
- **Explain architecture and runtime behavior visually** — add focused, plain-language diagrams
  only when boundaries, ordering, failures, state, or refactoring deltas are otherwise hard to see.
- **Trace delivery completeness** — ensure committed outcome, acceptance scenario, workstream, and
  verification remain connected without adding internal identifiers to developer conversation.

## 5. Business rules and invariants

- Completeness means enough confirmed detail for a developer or LLM to continue without prior chat;
  it does not mean documenting every class, method, rule, or candidate use case.
- Current behavior and current architecture come from repository evidence, not assumptions.
- The active slice is the only implementation commitment. The known feature map may remain broader.
- User specifications describe observable outcomes, rules, alternatives, and failures without
  leaking implementation detail.
- Technical specifications describe responsibilities, boundaries, runtime flow, data, contracts,
  decisions, risks, and rollout at the affected scope.
- Verification owns final as-built convergence; a structural validator cannot claim semantic or
  architectural correctness.
- A small change may require no separate detail document or diagram.

## 6. Candidate capabilities

- Reduced semantic exposure of deprecated compatibility skills and legacy artifact formats.
- Optional concise human change history if a future architecture decision replaces the current
  `_kapelle/changes/`-only model.

## 7. Exclusions, assumptions, and open decisions

- The implemented improvement does not add a new `/kapelle:refactor`, `/kapelle:archive`, or diagram
  stage.
- It does not copy OpenSpec's full change-directory lifecycle or SDD's mandatory Arc42/ADR package.
- It does not make detailed files or diagrams mandatory for simple changes.
- The existing root headings and `progressive-map-v1` marker remain the compatibility boundary; the
  `living-v1` marker enables stronger checks only for newly authored or explicitly revised packages.
- No blocking product decision is currently open.
