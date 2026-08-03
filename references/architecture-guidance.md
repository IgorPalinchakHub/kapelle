# Project architecture-rules capability

Kapelle expects project-native architecture guidance for the scoped part of a feature. Prefer the
project's dedicated architecture-rules subagent when available; project skills and instructions may
help locate it. The subagent name and rule provider are project-defined.
Bundled helpers follow [`script-execution.md`](./script-execution.md).

## Discovery

1. Inspect native project and installed-plugin agent descriptions semantically.
2. Select a subagent whose description says it can find or resolve project architecture rules for
   a supplied scope. If the project has no such capability, report the gap instead of repeatedly
   searching or inventing rules.
3. Give it only the feature slug, artifact paths, affected aspects/modules/entrypoints, task paths
   when applicable, and the decision being planned or implemented.
4. Require a source-affinity check before an external index is used. If its indexed repository,
   modules, or framework do not match the current project, discard that source immediately and use
   applicable project-native sources.
5. The project subagent may use native rules, files, MCP, CLI, APIs, or other project capabilities.
   Run it once for the current vertical slice and request only binding rules, collisions, and
   design-changing gaps rather than an exhaustive catalogue. A high-level feature map may name
   likely future boundaries, but their rules remain directional and cannot authorize code until
   the boundary is promoted and falls inside refreshed guidance.
6. Persist the result at the stage-defined path and run:

```text
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate_json.py" "<absolute-result-path>" "${CLAUDE_PLUGIN_ROOT}/dispatcher/architecture-guidance.schema.json"
```

   A non-zero exit blocks the stage; schema validation is never delegated to visual LLM
   inspection.

Do not maintain a Kapelle mapping from aspect, label, module, or rule code to an agent. Do not require
a specific agent name or provider.

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
capability: project architecture-rules subagent
needed-for: current vertical slice
```

Kapelle may explain the required input/output contract, but it must not generate project rules or
pretend that generic framework knowledge is project architecture guidance.
