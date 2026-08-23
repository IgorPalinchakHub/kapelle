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

## 3. Committed behavior

### Intended change

Add lightweight traceability inside the compact human package. Every active living-contract
acceptance scenario receives an `AC-NN` identifier; every workstream names the scenarios it covers
and already states focused verification. Deterministic validation checks completeness, unknown
references, and coverage without creating a mandatory task DAG or exposing identifiers in developer
questions.

### Resulting behavior

- Each active acceptance scenario has one stable `AC-NN` identifier.
- Each active workstream uses `covers AC-NN` or a compact range and references only existing active
  scenarios.
- Every active scenario is covered by at least one workstream.
- Each workstream continues to provide one objective `Verify` statement, closing the path from
  observable result to implementation evidence.
- Compatibility packages without the living marker are not forced into the new traceability floor.

### Preserved behavior

- Human documents remain the readable review surface; no mandatory machine graph, owner, estimate,
  file inventory, or microtask layer is added.
- Identifiers never appear in developer questions or require the developer to decode an internal
  blocker or gate.
- Candidate capabilities and high-level use-case-map items remain outside active traceability.

### Acceptance scenarios

- **AC-15** Given a living active slice, when its specification is validated, then at least one
  stable `AC-NN` acceptance scenario exists.
- **AC-16** Given an active workstream, when its compact task block is validated, then it names at
  least one existing acceptance scenario that it covers.
- **AC-17** Given the active scenario set, when validation completes, then every scenario is covered
  by at least one workstream and unknown references fail clearly.
- **AC-18** Given traceability is valid, when a developer reads the package, then the path from
  observable scenario through workstream to focused verification is visible without a separate DAG.

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
