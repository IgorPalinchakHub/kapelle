# XS/S fast lane

The fast lane combines business specification, high-level design, and delivery planning into one
review cycle. It never combines production implementation, unit testing, verification, or
finalization.

## Selection

`/kapelle:start --lane=auto` selects `fast` only when all are true:

- size is `XS` or `S`;
- one primary aspect and one coherent workstream;
- an established project pattern applies;
- no authorization, security, privacy, or compliance trigger;
- no destructive or ambiguous data migration;
- no new public contract or unresolved provider/consumer ownership;
- no unclear cross-component behavior;
- the expected plan is at most three production tasks.

Any failed condition selects `standard`. The developer may request `--lane=fast`, but a risk trigger
still forces standard and must be reported before artifacts are approved.

## Fast artifacts

One invocation may draft:

- `proposal.md`;
- `spec.md`;
- `design.md`;
- `tasks.md`;
- `_kapelle/surface-plan.json`;
- `_kapelle/task-plan.json`;
- `_kapelle/size.json`.

`spec.md` contains the complete small business specification. `tasks.md` contains a compact Test
strategy section, so `specs/`, `design/`, `contracts/`, and `test-plan.md` are not required unless
the discovered feature actually needs them.

One explicit approval persists `_kapelle/approvals/feature-plan.json`. Silence is never approval.
After approval, the route continues through `base-functional-tests`, `implement`, `unit-tests`,
`verify`, and `finalize`.

Coverage, architecture guidance, deterministic task validation, validation policy, and amendment
safety are identical to the standard lane.
