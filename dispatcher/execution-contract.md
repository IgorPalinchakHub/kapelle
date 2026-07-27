# Execution contract

## Inputs

- current `spec.md`, `design.md`, and `tasks.md`;
- current vertical-slice approval;
- cached scoped architecture guidance;
- repository code, tests, and project-native instructions/skills.

## Workstream execution

1. Select unchecked work only from the current approved vertical slice.
2. Confirm that cached architecture-rules scope covers the actual modules, entrypoints, and paths;
   refresh only on scope drift.
3. Use one relevant project capability when available.
4. Add focused boundary/characterization coverage when appropriate.
5. Implement the thinnest complete end-to-end outcome without speculative future abstractions.
6. Run the smallest useful development check under `ask | allow | skip`.
7. Review inline; dispatch a fresh reviewer only on risk or request.
8. Update the checkbox and short result, then rebuild status.

`task`, `workstream`, and `none` checkpoints control only how often control returns to the
developer. Workstream is the default.

## Bounds

- Maximum normal attempts come from config.
- Optional role runs are bounded; no role loop may self-escalate.
- Agent Teams require explicit developer approval and pairwise-disjoint ownership.
- Requirement/design changes pause remaining work and route to `amend`.
- A completed slice returns control: `amend` adds the next requirement; `verify` explicitly closes
  the current feature scope.
- Unit tests wait for `verify`.
- No git mutations.
