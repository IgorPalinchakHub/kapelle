# Lightweight design execution

Technical design is part of `start`, not a separate stage.

1. Build a bounded high-level system map of the known feature: context, likely components,
   responsibilities, domain/data ownership, integrations, and cross-cutting constraints.
2. Obtain one scoped architecture-rules result that is binding for the first slice. Candidate
   boundaries stay directional until promoted and rechecked.
3. Detail only the thinnest production-shaped runtime path. It crosses every boundary needed for
   one usable outcome and contains no empty endpoint/service scaffolding.
4. Follow `progressive-artifacts.md`. Add a detailed use-case design, domain model, contract,
   sequence, ADR, or aspect design only when its explicit trigger applies.
5. Use one critic/correction pass only for high-risk or materially ambiguous design.
6. On `amend`, refine the high-level map and detail only the promoted use case. Do not pre-design
   the remaining candidate capabilities.

`start --approve` is a pure gate operation: no artifact reads beyond deterministic validation, no
agent dispatch, and no edits.
