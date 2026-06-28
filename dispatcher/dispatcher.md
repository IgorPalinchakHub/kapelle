# Implementation dispatcher

The dispatcher executes dependency-ordered tasks without maintaining a second capability registry.
Claude Code selects applicable project skills, agents, and tools through native discovery and their
descriptions.

## Protocol

For each pending task:

1. Validate it against `task-context.schema.json`.
2. Read the referenced feature artifacts and relevant repository context from disk.
3. Present the task intent, acceptance criteria, hints, and artifact paths to native project capabilities.
4. Let Claude Code select the applicable project skill and agent semantically. Do not resolve names from
   a Kapelle manifest and do not parse a routing label.
5. Before code, instruct the selected project capability to obtain applicable project guidance using any
   provider available in the project or user environment.
6. Accept provider-neutral guidance evidence:
   `{ status, guidance[], sources[], gaps[] }`. Kapelle does not know whether it came from CLI, MCP,
   files, APIs, project instructions, or another agent.
7. When `guidance_evidence` is `required`, stop if evidence is absent or reports unresolved blocking gaps.
   `optional` records available evidence without requiring a provider; `disabled` skips this check.
8. Execute the project capability's own development protocol and validation commands.
9. Mark the task completed only when its Definition of Done and reported validation pass.
10. Append task, capability, guidance, and validation evidence to the feature audit log.

## Status lines

- `Status: CAPABILITY-SELECTED | skill: <name> | agent: <name-or-default>`
- `Status: GUIDANCE-READY | sources: <n> | gaps: <n>`
- `Status: BLOCKED-guidance | gaps: <descriptions>`
- `Status: IMPLEMENTED-and-validated | task: <id>`

## Invariants

- **No runtime pack registry** — distribution metadata is never read during implementation.
- **No provider coupling** — Kapelle does not invoke a named CLI or prescribe rule storage.
- **Native discovery** — project capability descriptions are the selection mechanism.
- **Artifact is state** — tasks and handoffs remain durable on disk.
- **No git ownership** — Kapelle never runs git operations.
