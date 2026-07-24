# High-level design template

Every `design.md`, including fast-lane design, uses these headings in this order:

```md
# Design

## 1. Context and goal
## 2. Scope and constraints
## 3. Architecture rules applied
## 4. Building blocks and responsibilities
## 5. Runtime flows
## 6. Data and domain impact
## 7. Contracts and integrations
## 8. Cross-cutting concerns
## 9. Decisions and trade-offs
## 10. Validation and rollout
## 11. Open questions
```

For a small feature, an inapplicable section contains one sentence such as
`Not applicable — no persistence change`; do not omit headings. Keep `design.md` high-level and
easy to scan.

Detailed documents under `design/` are created only for independently reviewable boundaries:

- `domain-model.md` for aggregates, fields, invariants, relations, and status transitions;
- `backend.md`, `frontend.md`, or `workers.md` for substantial aspect-specific design;
- `integrations.md` for non-trivial cross-component behavior.

Contract details remain under `contracts/`. Do not duplicate the high-level design in subfiles.
