---
name: classify-size
description: >
  Reclassify feature size, interview depth, and fast/standard lane when explicitly needed;
  normal features are classified automatically by start.
---

# Skill: classify-size

Classify feature size and write `_kapelle/size.json`.

## Inputs

- `<slug>` for feature-scoped work.
- Reads: `feature idea/spec`.
- Shared contract: [`../../references/stage-contract.md`](../../references/stage-contract.md).

## Protocol

1. Validate required inputs. If missing, refuse with the named producing stage.
2. Read artifacts directly from disk.
3. Perform this stage's work without re-running prior stages.
4. Use native project capabilities when project-specific behavior is needed: [`../../references/project-capabilities.md`](../../references/project-capabilities.md).
5. For any code-writing path, request provider-neutral project guidance: [`../../references/guidance.md`](../../references/guidance.md).
6. Write `_kapelle/size.json` as `{ "size": "XS|S|M|L|XL", "execution_depth": "...",
   "interview_depth": "lean|standard|deep", "lane": "fast|standard", "reason": "..." }`.
7. Run `scripts/validate_json.py docs/features/<slug>/_kapelle/size.json
   dispatcher/size.schema.json`. Refuse completion on non-zero exit.
8. Refresh `STATUS.md` and emit the chat handoff per
   [`../../references/handoff.md`](../../references/handoff.md).

## Output

- `_kapelle/size.json`.
- `Status: DONE | stage: classify-size | produced: <paths>`.

## Definition of Done

- Inputs were read from disk.
- Outputs exist and link to upstream artifacts instead of duplicating them.
- Skips are explicit.
- Handoff points to the current human-controlled stage.

## Anti-patterns

- Guessing missing prior-stage output.
- Baking project-specific conventions or provider assumptions into the core skill.
- Running git operations.
