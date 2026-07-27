---
name: start
description: >
  Map the known feature at high level, design one production-shaped walking-skeleton slice, and
  obtain approval before implementation.
---

# Skill: start

Invoke:

```text
/kapelle:start <slug> "<raw task>"
/kapelle:start <slug> --revise "<developer feedback>"
/kapelle:start <slug> --approve
```

Read [`../../references/developer-questions.md`](../../references/developer-questions.md) before
asking a question and [`../../references/architecture-guidance.md`](../../references/architecture-guidance.md)
before recording project rules. Follow
[`../../references/progressive-artifacts.md`](../../references/progressive-artifacts.md) for the
durable specification, system-design, use-case, and domain-model format.

## Draft or revise

1. Require a stable slug and a raw task for a new feature. Build a bounded high-level map of the
   known feature: current behavior, actors and outcomes, entrypoints, use cases, affected
   components, domain/data ownership, integrations, nearby tests, and precedents. Investigate only
   the first usable end-to-end path in implementation detail. Keep unknowns explicit.
2. The main agent integrates the map. Use an explorer only when ownership is unclear or relevant
   code spans unfamiliar modules. For a genuinely medium/large cross-component feature, it may run
   one bounded parallel read-only burst of at most three disjoint investigations: existing
   behavior, project architecture/rules, and contracts/tests/integrations. Subagents return concise
   evidence and do not write the human package.
   Use one critic pass only for material ambiguity or high risk: authorization, money, destructive
   data change, public contract, migration, concurrency, or cross-system side effects. Do not run a
   default business-analyst/critic/devil's-advocate chain.
3. Ask at most one consolidated developer question when a decision changes observable behavior.
   State the intended change and real options with trade-offs. Do not mention internal artifact,
   gate, task, blocker, or acceptance-criterion identifiers.
4. Discover relevant project skills, instructions, and the project architecture-rules capability.
   The binding guidance scope must cover the first slice; broader candidate boundaries in the
   high-level design remain directional until a later amendment refreshes their rules. Persist the
   current result in
   `_kapelle/architecture-guidance/design.json` and validate it:

```text
scripts/validate_json.py docs/features/<slug>/_kapelle/architecture-guidance/design.json dispatcher/architecture-guidance.schema.json
```

5. Create the minimum progressive human package:
   - `spec.md`: the full known high-level product map, with committed behavior clearly separated
     from candidate capabilities and unknowns. Begin it with:

```md
<!-- kapelle-workflow: lightweight-v1 -->
<!-- kapelle-artifacts: progressive-map-v1 -->
```

   - `design.md`: the high-level system context, likely component boundaries, responsibilities,
     end-to-end flow, domain/data ownership, contracts, decisions, risks, and deferrals. Design only
     the first committed slice in implementation detail; label candidate architecture directional.
   - `tasks.md`: one initial walking-skeleton workstream, split into at most three checkboxes only
     when the slice cannot remain reviewable as one checkbox. Do not place candidate capabilities here.
6. Add `specs/<use-case>.md` for the first slice only when alternatives, authorization, failures, or
   system reactions need independent review. Create `design/domain-model.md` when the slice changes
   an aggregate, lifecycle/status transition, money or authorization invariant, domain event,
   ownership boundary, or non-trivial relationship. Create contracts, other detailed design, an
   ADR, or a diagram only when its trigger in `progressive-artifacts.md` applies.
7. Keep documents easy to scan. Prefer roughly 250 lines for `spec.md`, 180 for `design.md`, and
   120 for `tasks.md` as soft ceilings. Validate the package:

```text
scripts/validate_progressive_docs.py docs/features/<slug>
```

   A non-zero result blocks approval. This validation checks structure, not semantic correctness.
8. The walking skeleton must be production-shaped, observable, and safe to extend; it is not a
   throwaway mock. It may return a deliberately narrow result, but must cross every boundary needed
   to prove the flow: input/authorization/validation, endpoint or command, use-case service, domain
   and persistence/integration boundary, stable minimal response, and focused boundary evidence as
   applicable. Do not scaffold every future endpoint or empty service. It must leave the project
   loadable and internally coherent. Do not plan a knowingly broken intermediate state such as an
   enum/schema rename separated from required readers and migrations.
9. Plan basic functional/characterization tests before production changes only for affected
   endpoints, commands, workers, or public use-case methods. Keep this work inside its owning
   workstream. Do not plan or write unit tests until `/kapelle:verify`.
10. For a new feature, write `_kapelle/workflow.json` as:

```json
{
  "workflow": "human-controlled",
  "version": 2,
  "created_from": "raw-task",
  "profile": "lightweight"
}
```

   Preserve `created_from: legacy-migration` when revising a migrated feature.
   Validate it with `workflow-state.schema.json`, then rebuild generated state with
   `scripts/build_feature_status.py docs/features/<slug>` and
   `scripts/validate_feature_state.py docs/features/<slug>`.
11. On revision, correct the high-level map or active slice without detailing candidate use cases.
    Any plan, verification, or final approval whose fingerprints no longer match becomes stale
    automatically. Do not promote candidate capabilities into committed behavior until the
    developer requests them through `/kapelle:amend`.

## Approve

`--approve` is a pure gate action: do not inspect the repository, dispatch agents, or edit the
human package. Run `validate_progressive_docs.py`, validate architecture guidance and the existing
documents, then run:

```text
scripts/review_gate.py approve docs/features/<slug> plan \
  --confirmation "Developer explicitly approved the current vertical slice."
```

The internal gate keeps the compatibility name `plan`, but human-facing output calls it the
current-slice approval. Never write approval JSON manually. Missing or invalid inputs produce
`Status: REFUSED-missing-input` and the exact correction command.

## Handoff

Show the high-level feature outcome, the usable outcome of the first slice, what remains candidate
or unknown, important trade-offs, files to review, and no more than three unresolved decisions.
After approval, the next command is:

```text
/kapelle:implement <slug> --checkpoint=workstream --validation=ask
```

Refresh `STATUS.md`, use the standard handoff block, hide agent chatter, and never run git
operations.
