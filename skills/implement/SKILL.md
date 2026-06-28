---
name: implement
model: inherit
effort: high
agents: [test-author, implementer, reviewer]
description: >
  Execute tasks through native project capabilities, provider-neutral guidance, and project validation. Invoke as /kapelle:implement <slug>.
---

# Skill: implement

`implement` is the generic dispatcher entrypoint. It reads `dispatcher/dispatcher.md` and delegates
project behavior through Claude Code native discovery.

## Inputs

- Gate: `docs/features/<slug>/tasks.json`.
- Feature artifacts under `docs/features/<slug>/`.
- Project instructions and native `.claude/skills`, `.claude/agents`, `.claude/rules`.
- Any user/project plugins, MCP tools, or provider capabilities already available to Claude Code.

## Protocol

1. Refuse if `tasks.json` is missing; run `tasks` first.
2. Validate tasks against `dispatcher/task-context.schema.json`.
3. Sort pending tasks by dependency order.
4. For each task:
   - read its referenced artifacts and repository context;
   - let Claude Code select applicable project skills and agents by native descriptions;
   - request applicable project guidance without naming or assuming a provider;
   - enforce only the configured provider-neutral evidence policy;
   - execute the selected capability's implementation and validation protocol;
   - update status only after Definition of Done and validation pass;
   - append capability, guidance, and validation evidence to
     `docs/features/<slug>/_audit/implementation.jsonl`.
5. Emit handoff to `/kapelle:review <slug>`.

## Definition of Done

- Every completed task has capability-selection and validation evidence.
- Required guidance evidence exists when the project enables that policy.
- No runtime pack manifest, rule storage convention, CLI, or provider name was assumed.

## Anti-patterns

- Selecting project capabilities from a Kapelle routing table.
- Requiring one specific rule provider or command.
- Encoding search topics or rule codes in Kapelle core.
- Running git operations.
