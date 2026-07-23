---
name: specify
description: >
  Turn a raw feature idea into `proposal.md` and `spec.md` with acceptance criteria.
---

# Skill: specify

Turn a raw feature idea into a short proposal and an observable product specification.

## Inputs

- `<slug>` for feature-scoped work.
- Raw feature idea from the command or current user message. Minimum: problem and desired observable
  outcome.
- Reads: `idea + optional docs/features/<slug>/_context/architecture.md + optional
  docs/architecture-map.md`.
- Shared contract: [`../../references/stage-contract.md`](../../references/stage-contract.md).
- Agent contract: [`../../references/agent-orchestration.md`](../../references/agent-orchestration.md).
- Execution depth: [`../../references/execution-depth.md`](../../references/execution-depth.md).

## Protocol

1. Run the bounded input preflight before repository analysis:
   - verify only whether the target feature directory and feature-local architecture overlay exist;
   - compare the supplied slug/ticket only with branch or ticket metadata already provided by the
     host or feature context;
   - do not run git/shell discovery, read commits, search source code, inspect implementation
     classes, read unrelated specs as templates, or dispatch subagents.
2. Require these resolved inputs before any deeper read or write:
   - authoritative slug/ticket when supplied evidence conflicts;
   - whether this is a new specification or formalization of known in-flight work when ambiguous;
   - raw product idea: problem and desired observable outcome.
3. If any required input is missing or conflicting, ask for every unresolved field in one
   consolidated interaction, with at most three short questions. Do not ask ticket, scope, and idea
   in separate sequential rounds when they are already known to be unresolved. Emit
   `Status: NEEDS-INPUT | fields: <names>`, write nothing, and stop until the user answers.
4. Do not create `docs/features/<slug>/` until the authoritative slug is resolved. When the answer
   changes the slug, use only the corrected slug and do not leave an alias or partial directory.
5. After input is complete, read artifacts directly from disk. Prefer the feature-local
   architecture overlay for current branch evidence, then use the shared architecture baseline for
   unchanged context.
6. Keep repository reads product-focused and bounded. Search source only when a specific acceptance
   criterion cannot be grounded from the idea and existing context; record the exact unresolved
   question first. Broad code mapping, implementation archaeology, and detailed technical design
   belong to `survey` and `design`.
7. Draft `proposal.md` with the problem, goal, scope, non-goals, impact, risks, and unresolved
   product decisions. Draft `spec.md` with actors, user stories, measurable acceptance criteria,
   NFRs, edge cases, compatibility, and open questions. Do not introduce implementation routing.
8. Use native project capabilities only after input completeness, when project-specific product
   behavior is genuinely needed:
   [`../../references/project-capabilities.md`](../../references/project-capabilities.md).
9. Classify size and execution depth. At `lean`, perform one inline acceptance-criteria and failure
   branch check. At `standard`/`full`, dispatch `kapelle:devils-advocate`.
10. Resolve or explicitly defer every blocking finding.
11. Dispatch `kapelle:critic` only at `full` depth or when requirements conflict with repository
   constraints. Otherwise leave the independent ambiguity delta pass to `clarify`.
12. Write `proposal.md`, `spec.md`, and `_kapelle/size.json`. Keep execution-depth metadata in
    `_kapelle/size.json`, not in the human documents.
13. Run `scripts/build_feature_status.py docs/features/<slug> --initialize` on first creation (or
    the normal refresh when a manifest already exists) and emit the chat handoff per
    [`../../references/handoff.md`](../../references/handoff.md). The handoff is not appended to a
    human artifact.

## Output

- `docs/features/<slug>/proposal.md`, `spec.md`, and `_kapelle/size.json`.
- `Status: DONE | stage: specify | produced: <paths>`.

## Definition of Done

- Inputs were read from disk.
- Outputs exist and link to upstream artifacts instead of duplicating them.
- Skips are explicit.
- Handoff points to `clarify`.

## Anti-patterns

- Guessing missing prior-stage output.
- Exploring source code, commits, or implementation details before the raw idea and authoritative
  slug are resolved.
- Asking a multi-step ticket/scope/idea wizard when one consolidated input request is sufficient.
- Creating artifacts under a provisional or conflicting slug.
- Baking project-specific conventions or provider assumptions into the core skill.
- Running git operations.
