# Human-controlled development workflow

Kapelle minimizes ceremony while keeping two explicit decisions:

```text
raw task
  -> high-level feature map + high-level system design
  -> one minimal walking skeleton
  -> developer slice approval
  -> production implementation
  -> detail/promote the next use case through amend (repeat when needed)
  -> all unit tests + complete verification
  -> developer final approval
```

Silence is never approval.

## Checkpoints

- `--checkpoint=workstream` is the default: return after a cohesive, reviewable outcome.
- `--checkpoint=task` is opt-in for high-risk work.
- `--checkpoint=none` is opt-in for low-risk execution of all ready work in the approved slice.

A checkpoint reports observable behavior, changed areas, checks, risks, and the next action. It
does not expose agent transcripts or machine-artifact identifiers.

## Agent use

The main agent owns normal analysis, slice planning, coding, and first review. Additional roles are
conditional:

- explorer — unclear ownership or unfamiliar modules;
- critic/reviewer — high risk, important ambiguity, design deviation, repeated failure, or explicit
  request;
- Agent Teams — explicit approval plus disjoint file ownership.

Normal work does not run business analyst to critic to devil's advocate or planner to implementer
to reviewer chains.

For a medium/large cross-component feature, `start` or `amend` may use one read-only parallel burst
of at most three disjoint investigations. The main agent integrates the result and is the only
writer of the human package. Agent Teams are an implementation optimization after contracts are
stable, never a prerequisite for planning or the first skeleton.

## Test timing

Focused endpoint/use-case functional tests or legacy characterization tests may precede their
production change. All unit tests are written after production implementation. Complete functional,
unit, integration/contract, static-analysis, lint, and build verification happens once in
`/kapelle:verify`.

Development checks use `ask | allow | skip`. Deferred required checks block PASS and final approval.

## Incremental requirements

Start with a high-level map of all known use cases and one production-shaped end-to-end path.
Candidate capabilities are hypotheses, not approved scope. `/kapelle:amend` promotes one requested
business or technical requirement, details only that use case and its affected design/domain/
contracts, and adds one coherent slice. That slice receives a new approval before code. Heavy
revision history is reserved for high-risk or post-verification changes.

## Bounded loops

- discovery: one initial pass plus at most one targeted expansion;
- specification/design: draft, at most one critic pass, at most one correction;
- implementation: narrow check and at most two correction attempts before developer input;
- final review: at most one reviewer/correction pass.

Deterministic scripts own structural validation and gates. Agents do not loop until they agree.

## Completion

Invoking `verify` explicitly means the developer considers the accumulated slices sufficient for
the feature. Current PASS verification plus explicit final approval completes the process. Diagrams,
release records, versions, and git operations are optional project concerns, not harness gates.
