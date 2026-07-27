# Using Kapelle

## New feature

Start from the ticket or raw task:

```text
/kapelle:start <slug> "<raw developer task>"
```

The command maps the known feature at high level, inspects the first end-to-end path in detail,
discovers project guidance, and writes:

- `spec.md` — current behavior, committed behavior, known use-case map, invariants, candidates, and
  unknowns;
- `design.md` — high-level system boundaries plus the technical path needed by the first slice;
- `tasks.md` — one walking-skeleton workstream, optionally split into at most three checkpoints;
- `_kapelle/architecture-guidance/design.json` — validated project-rule evidence;
- generated `STATUS.md`.

Review those three Markdown files. Request focused changes:

```text
/kapelle:start <slug> --revise "<feedback>"
```

Approve the unchanged package:

```text
/kapelle:start <slug> --approve
```

Approval is deterministic and performs no analysis or artifact edits.

The progressive document gate checks the stable headings, order, non-empty sections, optional
use-case/domain-model shapes, and size caps. It does not claim to prove semantic design quality.

## Implementation

```text
/kapelle:implement <slug> --checkpoint=workstream --validation=ask
```

`workstream` is the default and recommended checkpoint. Use `task` only when you need very tight
control, or `none` when the slice is low risk and you want one result after all its ready work.

The main agent implements the end-to-end slice using relevant project-native skills. The first
slice crosses the applicable input/auth/validation, endpoint or command, use-case service, domain,
persistence/integration, and response boundaries. It does not scaffold empty future services. It
may add focused functional/characterization tests before production changes. It does not write unit
tests or run the whole static-analysis/lint suite during normal development.

Validation policy:

- `ask` — show the exact focused commands first;
- `allow` — run them without an extra prompt;
- `skip` — defer them; required checks must pass later in `verify`.

## Add the next requirement

```text
/kapelle:amend <slug> "<feedback or changed requirement>"
```

Kapelle inspects the working base, promotes only the requested candidate into committed behavior,
details that use case and its domain/contracts when triggered, and adds one smallest coherent
vertical slice. It does not design the remaining candidate map. The previous slice remains
documented and implemented. Approve the new slice:

```text
/kapelle:start <slug> --approve
```

Heavy immutable revision history is reserved for post-verification or high-risk amendments.

## Verification and completion

When all currently approved slices are implemented and you do not want to add another requirement:

```text
/kapelle:verify <slug> --validation=ask
```

Invoking `verify` explicitly declares the accumulated feature scope sufficient. The command
reconciles docs with code, writes all unit tests, and runs one applicable functional,
unit, integration/contract, static-analysis, lint, and build batch. Categories that do not apply are
omitted with a reason.

After PASS and developer/manual review:

```text
/kapelle:verify <slug> --approve
```

This is a pure final gate. Kapelle does not require diagrams, release JSON, a version number, or git
operations.

## Status and recovery

```text
/kapelle:status <slug>
```

`STATUS.md` shows workstream progress, deferred validation, core files plus any present
use-case/domain/contract detail to review, and one next command. If `_kapelle/` is gone, state is
rebuilt without fabricating approvals or PASS evidence.

## Old feature directories

```text
/kapelle:migrate <slug>
/kapelle:migrate <slug> --apply
```

The first command is a dry-run. Migration preserves old documents/evidence and adopts the
lightweight workflow. Former commands such as `spec`, `design`, `plan`,
`base-functional-tests`, `unit-tests`, and `finalize` are non-executing compatibility wrappers.

## Documentation-only reconstruction

```text
/kapelle:reconstruct <slug> "<existing feature scope>"
```

This separate route documents current code and architecture. It never routes to implementation,
testing, or completion.

## Optional utilities

These commands are independent helpers, not required stages:

- `/kapelle:survey [<slug>]` — bootstrap repository context or inspect feature-local architecture;
- `/kapelle:decide-adr <slug>` — capture one durable architecture decision;
- `/kapelle:contracts <slug>` — document a public or cross-component boundary;
- `/kapelle:data-model <slug>` — clarify data/schema and domain-model impact;
- `/kapelle:sequences <slug>` — document a genuinely complex runtime flow;
- `/kapelle:glossary <slug>` — reconcile ambiguous domain terms;
- `/kapelle:roadmap <slug>` — update project roadmap placement.

Utilities never chain into each other. When one changes an approved spec, design, task list, ADR,
or contract, review the result and renew current-slice approval with
`/kapelle:start <slug> --approve`.
