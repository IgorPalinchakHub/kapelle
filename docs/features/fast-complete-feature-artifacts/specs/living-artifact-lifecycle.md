# Living artifact lifecycle

## Outcome

Each implemented Kapelle slice leaves a concise, complete, as-built user and technical description
that can guide later development without the chat that produced it.

## Trigger and actors

- A developer starts a new feature, amends an existing feature, or requests a refactor.
- Kapelle inspects the relevant current behavior and architecture.
- A developer reviews and approves the active slice.
- A later developer, QA reviewer, or LLM reads the resulting package.

## Preconditions

- The feature slug and requested outcome are stable enough to bound one vertical slice.
- Relevant repository behavior can be inspected, or unknowns are explicitly recorded.
- Scoped project architecture guidance is ready for the affected paths.
- Candidate capabilities are separated from committed behavior.

## Main flow

1. `start` or `amend` classifies the request as new behavior, an existing-feature change, a
   behavior-preserving refactor, a defect, or a documentation correction.
2. Kapelle inspects only the current behavior and affected technical scope needed for the slice.
3. `spec.md` records the current state, intended change, resulting behavior, preserved behavior,
   and acceptance scenarios.
4. `design.md` records the affected current architecture, resulting responsibilities and flow,
   technical delta, constraints, and risk-triggered details.
5. When a real decision remains, Kapelle recommends an evidence-backed option with its downside and
   uses a short code example only when that makes the decision materially clearer.
6. When boundaries, ordering, lifecycle, data flow, or refactoring deltas are hard to understand in
   prose, Kapelle adds the smallest triggered Mermaid visual and explains it in plain language.
7. `tasks.md` records one coherent workstream with changed areas, completion signal, focused
   verification, and coverage of active `AC-NN` scenarios.
8. The developer approves the slice and implementation proceeds through the existing workflow.
9. `verify` compares code, tests, contracts, diagrams, and project guidance with the human package.
10. Kapelle updates canonical and triggered detail documents to the confirmed as-built state and
   reports any mismatch that needs `amend`.

## Alternatives and failures

- If the request is a simple new behavior with no prior flow, current behavior is stated as absent
  and preserved behavior may be limited to nearby contracts or explicitly not applicable.
- If current behavior cannot be established safely, the unknown remains explicit; Kapelle asks one
  concise question only when the answer changes behavior, architecture, compatibility, or risk.
- If a refactor changes observable behavior, it is reclassified as a behavior change and receives
  user acceptance scenarios for that change.
- If implementation contradicts approved behavior or design, `verify` does not silently rewrite
  intent; it routes the contradiction through `amend`.
- If a legacy package lacks the new compact substructure, compatibility validation continues until
  that feature is explicitly revised.

## System reactions

- Structural validation rejects newly authored incomplete change/result/refactor/task structures
  but does not claim that prose is semantically correct.
- Approval fingerprints include the current human package and become stale when its meaning changes.
- `STATUS.md` is rebuilt from deterministic state after package changes.
- Detailed use-case or technical files are created only when their existing evidence triggers apply.
- Machine coordination and audit evidence remain below `_kapelle/`.

## Acceptance scenarios

- A developer can review one compact active slice and identify what exists, what changes, what the
  result will be, what stays unchanged, and how success will be checked.
- A later reader can follow the final user flow and affected technical flow without prior chat.
- A refactor makes before/target responsibility changes explicit without describing the whole repo.
- A simple slice remains in root documents and does not create empty detail files or diagrams.
- A legacy progressive package remains valid until explicitly revised into the stronger contract.
- Every active acceptance scenario is visibly connected to a coherent workstream and focused
  verification, while developer questions remain free of internal identifiers.
