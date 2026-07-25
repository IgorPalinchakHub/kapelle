# Project architecture-rules capability

Kapelle requires each project to provide a native subagent capable of finding the architectural
rules applicable to a scoped part of a feature. The subagent name and its rule provider are
project-defined.

## Discovery

1. Inspect native project and installed-plugin agent descriptions semantically.
2. Select a subagent whose description says it can find or resolve project architecture rules for
   a supplied scope.
3. Give it only the feature slug, artifact paths, affected aspects/modules/entrypoints, task paths
   when applicable, and the decision being planned or implemented.
4. Require a source-affinity check before an external index is used. If its indexed repository,
   modules, or framework do not match the current project, discard that source immediately and use
   applicable project-native sources.
5. The project subagent may use native rules, files, MCP, CLI, APIs, or other project capabilities.
   For high-level design, bound it to 12 focused lookup batches and request binding rules,
   collisions, and design-changing gaps rather than an exhaustive catalogue.
6. Persist the result at the stage-defined path and run `scripts/validate_json.py <result-path>
   dispatcher/architecture-guidance.schema.json`. A non-zero exit blocks the stage; schema
   validation is never delegated to visual LLM inspection.

Do not maintain a Kapelle mapping from aspect, label, module, or rule code to an agent. Do not require
a specific agent name or provider.

## Required gates

- `survey` records whether the project capability was discovered; absence is a readiness gap.
- `design` refuses architecture decisions until the capability returns
  `ARCHITECTURE_GUIDANCE_READY` without blocking gaps.
- `implement` refreshes the result for each task's actual aspects and file scope before planning.
- `finalize` verifies the implementation against the scoped rules evidence in fresh context.

Write evidence to:

```text
docs/features/<slug>/_kapelle/architecture-guidance/design.json
docs/features/<slug>/_kapelle/architecture-guidance/<task-id>.json
```

Missing capability:

```text
Status: REFUSED-missing-project-capability
capability: project architecture-rules subagent
needed-for: <design|task-id>
```

Kapelle may explain the required input/output contract, but it must not generate project rules or
pretend that generic framework knowledge is project architecture guidance.
