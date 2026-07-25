# Using Kapelle

## 1. Development workflow

New work begins with:

```text
/kapelle:start <slug> "<raw developer task>"
```

Existing directories without the durable human-controlled marker begin with:

```text
/kapelle:migrate <slug>
/kapelle:migrate <slug> --apply --lane=standard
```

Migration preserves human documents and code, adds workflow routing, rebuilds derived state, and
reports lost evidence. It does not recreate approvals or validation.

## 2. Lane and interview selection

```text
/kapelle:start <slug> "<task>" --lane=auto --interview=auto
```

Lane:

- `fast`: XS/S, one aspect/workstream, established pattern, at most three production tasks, no
  risk trigger;
- `standard`: separate spec, architecture, and plan review;
- `auto`: fast only when every eligibility condition is evidenced.

Interview:

- `lean`: inline challenge and only one consolidated blocking question;
- `standard`: business analysis and one combined critic pass;
- `deep`: separate business analyst, critic, and devil's advocate;
- `auto`: derived from size and risk.

Interview depth changes questions and agent runs, not coverage.

## 3. Fast lane

One `start` invocation drafts:

```text
proposal.md
spec.md
design.md
tasks.md
_kapelle/surface-plan.json
_kapelle/task-plan.json
```

The developer reviews the complete package once. If not approved immediately:

```text
/kapelle:start <slug> --revise "<feedback>"
/kapelle:start <slug> --approve
```

After approval:

```text
/kapelle:base-functional-tests <slug> --validation=ask
```

Discovery of a risk trigger before approval changes the lane to standard.

## 4. Standard lane

```text
/kapelle:start <slug> "<task>"
/kapelle:spec <slug>
/kapelle:spec <slug> --approve
/kapelle:design <slug>
/kapelle:design <slug> --detail
/kapelle:design <slug> --approve
/kapelle:plan <slug>
/kapelle:plan <slug> --approve
```

`spec.md` remains the business overview; independently useful scenarios/rules/integrations go to
`specs/`.

`design.md` follows the stable high-level template, targets 150–220 lines, and is rejected above
280 lines or 2800 words. The first pass reuses feature context, bounds architecture/critic
lookups, records ADR candidates, and avoids exhaustive implementation mechanics. `--detail`
creates only useful component/domain/integration documents under `design/`, accepted ADRs, and
detailed interfaces under `contracts/`.

All approvals use canonical gate files and exact full fingerprints. A stage never accepts aliases
such as `feature-outline.json` or `business-specification.json`, and it never hand-edits generated
state or `STATUS.md`.

`plan` writes outcome-oriented `tasks.md`, a standard-lane `test-plan.md`, and the deterministic
task graph.

## 5. Delivery

```text
/kapelle:base-functional-tests <slug> --validation=ask
/kapelle:implement <slug> --checkpoint=task --validation=ask
/kapelle:unit-tests <slug> --validation=ask
/kapelle:verify <slug> --validation=ask
```

Checkpoints:

- `task`: return after every task;
- `workstream`: return after every coherent workstream;
- `none`: continue through all dependency-ready production tasks.

`implement` writes production code only. `unit-tests` runs after all production tasks. `verify`
handles full functional, unit, integration, contract, static-analysis, lint, and build checks.

During implementation, verification, or developer testing:

```text
/kapelle:amend <slug> "<changed requirement or feedback>"
```

Amendment versions current state, computes impact, asks for route approval, invalidates downstream
evidence, and returns to the earliest necessary stage.

## 6. Finalization

After manual testing and debugging:

```text
/kapelle:finalize <slug> --version=1.0
```

Finalization reconciles as-built behavior and design, runs fresh review, generates Mermaid feature
flow and architecture diagrams, records final approval, and marks the feature completed.

## 7. Recovery and status

```text
/kapelle:status <slug>
```

`STATUS.md` is generated and is the entry point. When internal state is missing, the proposal
marker preserves lane routing. Missing approvals and validation return the developer to the
minimal safe gate.

## 8. Optional utilities

- `survey`: shared repository baseline or feature-local architecture evidence;
- `sequences`: unusually complex runtime flows;
- `data-model`: complex persistence/migration analysis;
- `contracts`: specialized interface enrichment;
- `decide-adr`: consequential architectural decision;
- `glossary`: domain terminology;
- `roadmap`: feature portfolio state.

Utilities enrich artifacts; they never create a second pipeline.

## 9. Reconstruct an existing feature

Use the separate documentation workflow when the code already exists and the goal is to explain
current behavior and architecture:

```text
/kapelle:reconstruct <slug> "<feature scope>"

# Example
/kapelle:reconstruct payments-refund "Existing refund flow from API entrypoint to settlement"
/kapelle:reconstruct payments-refund --approve
/kapelle:reconstruct payments-refund --spec
/kapelle:reconstruct payments-refund --approve
/kapelle:reconstruct payments-refund --design
/kapelle:reconstruct payments-refund --approve
/kapelle:reconstruct payments-refund --review
/kapelle:reconstruct payments-refund --approve
```

The result is a hierarchical product package (`spec.md`, `specs/*.md`) and as-built architecture
package (`design.md`, `design/*.md`), plus an evidence index and fingerprinted coverage record.
`--approve` always approves only the current draft shown by `STATUS.md`.

This workflow writes documentation only. It does not create tasks, change production code, run
delivery stages, or claim release readiness. See
[the Ukrainian reconstruction guide](RECONSTRUCTION_UK.md).
