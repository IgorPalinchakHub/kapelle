---
name: survey
description: >
  Bootstrap the shared repository architecture baseline or write a worktree-safe feature-local
  architecture overlay, with explicit shared-baseline refresh.
---

# Skill: survey

Bootstrap shared repository context or inspect the current feature scope without rewriting shared
state.

## Inputs

- Optional `<slug>` for feature-scoped work.
- Optional `--refresh-baseline`, requiring explicit user confirmation.
- Reads: `repo`.
- Shared contract: [`../../references/stage-contract.md`](../../references/stage-contract.md).
- Agent contract: [`../../references/agent-orchestration.md`](../../references/agent-orchestration.md).
- Architecture-guidance contract:
  [`../../references/architecture-guidance.md`](../../references/architecture-guidance.md).
- Repository-context contract:
  [`../../references/repository-context.md`](../../references/repository-context.md).

## Protocol

1. Read `docs/architecture-map.md` when it exists. Treat its `reflects_commit` as provenance only;
   branch divergence never makes the shared file an automatic write target.
2. If `<slug>` is present, inspect only current-branch evidence relevant to that feature. Write
   `docs/features/<slug>/_context/architecture.md`; never create or update
   `docs/architecture-map.md`, even when the shared baseline is missing.
3. If no slug and the baseline exists without `--refresh-baseline`, do not dispatch a repository
   remap and do not write. Report `Status: BASELINE-READY` and hand off to `start`.
4. If no slug and the baseline is missing, dispatch `kapelle:explorer` once for repository stack, module
   boundaries, wiring, data stores, test commands, project skills/subagents, rules, and cited
   precedents; write `docs/architecture-map.md`.
5. If `--refresh-baseline` is present, show the proposed baseline sections and require explicit
   confirmation before dispatching the full refresh. Refuse combining it with `<slug>`. Do not
   interpret branch drift as confirmation.
6. Semantically discover the project's architecture-rules subagent. Record its native name and
   description evidence, or record a readiness gap; do not create a Kapelle alias or mapping.
7. Use native project capabilities when project-specific behavior is needed:
   [`../../references/project-capabilities.md`](../../references/project-capabilities.md).
8. Merge only cited findings and record unknowns instead of guessing.
9. Emit the stage-handoff block per [`../../references/handoff.md`](../../references/handoff.md).

## Output

- Bootstrap: `docs/architecture-map.md`.
- Feature scope: `docs/features/<slug>/_context/architecture.md`.
- Existing baseline without slug: no write.
- `Status: DONE | stage: survey | produced: <paths>`.

## Definition of Done

- Inputs were read from disk.
- Outputs exist and link to upstream artifacts instead of duplicating them.
- The applicable baseline or feature overlay records project skill/subagent discovery and
  architecture-rules capability readiness.
- Feature work never rewrites shared repository context.
- Skips are explicit.
- Handoff points to `start`.

## Anti-patterns

- Guessing missing prior-stage output.
- Treating `reflects_commit` or worktree divergence as permission to refresh the shared baseline.
- Copying the full shared baseline into a feature overlay.
- Baking project-specific conventions or provider assumptions into the core skill.
- Running git operations.
