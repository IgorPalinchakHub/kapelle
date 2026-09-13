# Project architecture-rules capability

Kapelle obtains scoped project architecture guidance through a native project skill. The skill
owns the lookup procedure: which sources to read, where to search, and which subagent to use, if
any. Kapelle does not select an architecture-rules subagent directly or require one independently
of the skill. The skill name and rule provider are project-defined.
Bundled helpers and project-native read-only CLI calls follow
[`script-execution.md`](./script-execution.md).

## Discovery

1. Inspect native project instructions and available project or installed-plugin skill descriptions
   semantically. Select the narrowest skill that finds or resolves this project's architecture rules.
2. Read the selected `SKILL.md` and follow its lookup procedure. A skill may read rules directly or
   dispatch a project subagent; the presence of an agent alone does not replace the skill. If no
   applicable skill is available, report the missing capability without inventing one.
3. Supply the feature slug, artifact paths, affected aspects/modules/entrypoints, task paths when
   applicable, and the decision being planned or implemented. Load only relevant skill references.
4. Require a source-affinity check before an external index is used. If its indexed repository,
   modules, or framework do not match the current project, discard that source immediately and use
   applicable project-native sources.
5. Follow the skill's instructions for native rules, files, MCP, CLI, APIs, or project subagents.
   Every allowlisted read-only CLI call is one direct tool call: consume the tool result and never
   add `cd`, redirection, a scratchpad, exit-code `echo`, shell operators, background execution, or
   a polling loop.
   Run it once for the current vertical slice and request only binding rules, collisions, and
   design-changing gaps rather than an exhaustive catalogue. A high-level feature map may name
   likely future boundaries, but their rules remain directional and cannot authorize code until
   the boundary is promoted and falls inside refreshed guidance.
6. The main agent normalizes the returned guidance into the existing evidence contract, recording
   the selected skill name with `capability.kind: project-skill`, even when the skill delegates a
   lookup. Do not require project skills or their subagents to know Kapelle's JSON format. Persist
   the result at the stage-defined path. Run validate_json.py against
   dispatcher/architecture-guidance.schema.json using the command in the invoking SKILL.md.

   A non-zero exit blocks the stage; schema validation is never delegated to visual LLM
   inspection.

Do not maintain a Kapelle mapping from aspect, label, module, or rule code to a skill or agent.
Do not require a specific skill name, agent name, or provider. Keep lookup within the existing stage;
it does not add a separate approval round. Explain applicable constraints and proposed consequences
briefly to the developer before linking to sources; do not forward raw lookup output.

Legacy evidence with `capability.kind: project-subagent` must be reacquired through the project
skill before reuse. Do not relabel old evidence as skill-derived without performing the lookup.

## Lifecycle

- `start` refuses current-slice approval until the capability returns
  `ARCHITECTURE_GUIDANCE_READY` without blocking gaps.
- `implement` reuses this result for the current slice inside its recorded scope.
- `amend` refreshes it only when the next slice leaves the recorded scope.
- Refresh it only when the actual scope or design leaves the recorded modules, entrypoints, or
  paths.
- `verify` reconciles the implementation against this cached evidence.

Write evidence to:

```text
docs/features/<slug>/_kapelle/architecture-guidance/design.json
```

Missing capability:

```text
Status: REFUSED-missing-project-capability
capability: project architecture-rules skill
needed-for: current vertical slice
```

Kapelle may explain the required input/output contract, but it must not generate project rules or
pretend that generic framework knowledge is project architecture guidance.
