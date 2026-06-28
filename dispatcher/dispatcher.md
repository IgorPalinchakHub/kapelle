# Implementation dispatcher

The dispatcher executes dependency-ordered tasks without maintaining a second capability registry.
It uses explicit Kapelle execution roles while Claude Code selects project skills, agents, and tools
through native discovery and their descriptions.

## Protocol

For each pending task:

1. Validate it against `task-context.schema.json`.
2. Read the referenced feature artifacts and relevant repository context from disk.
3. Validate the complete dependency graph and compute dependency-ready batches.
4. Present the task intent, acceptance criteria, hints, and artifact paths to native project capabilities.
5. Let Claude Code select the applicable project skill and agent semantically. Do not resolve names from
   a Kapelle manifest and do not parse a routing label.
6. Before code, instruct the selected project capability to obtain applicable project guidance using any
   provider available in the project or user environment.
7. Accept provider-neutral guidance evidence:
   `{ status, guidance[], sources[], gaps[] }`. Kapelle does not know whether it came from CLI, MCP,
   files, APIs, project instructions, or another agent.
8. When `guidance_evidence` is `required`, stop if evidence is absent or reports unresolved blocking gaps.
   `optional` records available evidence without requiring a provider; `disabled` skips this check.
9. Execute `execution-contract.md`: explicitly dispatch `kapelle:test-author`,
   `kapelle:implementer`, and `kapelle:reviewer`; validate their structured results.
10. Use sequential mode by default. Use an Agent Team only when configured, available, explicitly
    approved, and safe for the ready task batch.
11. Run the project capability's validation commands.
12. Mark the task completed only when its Definition of Done, review, and validation pass.
13. Append task, capability, guidance, RED, implementation, review, and validation evidence to the
    feature audit log.

## Status lines

- `Status: CAPABILITY-SELECTED | skill: <name> | agent: <name-or-default>`
- `Status: EXECUTION-MODE | mode: sequential|agent-team | reason: <selection>`
- `Status: RED-CLASSIFIED | task: <id> | result: GOOD_RED|BAD_RED|FALSE_PASS|NON_RED`
- `Status: GUIDANCE-READY | sources: <n> | gaps: <n>`
- `Status: BLOCKED-guidance | gaps: <descriptions>`
- `Status: IMPLEMENTED-and-validated | task: <id>`

## Invariants

- **No runtime pack registry** — distribution metadata is never read during implementation.
- **No provider coupling** — Kapelle does not invoke a named CLI or prescribe rule storage.
- **Native discovery** — project capability descriptions are the selection mechanism.
- **Explicit roles** — agent execution comes from protocol dispatch, never custom frontmatter.
- **Safe concurrency** — unknown or overlapping file ownership remains sequential.
- **Official mechanisms only** — no generated or assumed `Workflow` tool.
- **Artifact is state** — tasks and handoffs remain durable on disk.
- **No git ownership** — Kapelle never runs git operations.
