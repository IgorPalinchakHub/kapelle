# Config loader

The loader reads the optional `.claude/kapelle.config.json` and provides SDLC artifact and module context.
It does not register skills, agents, gates, rules, or knowledge providers.

## `load()` → ResolvedConfig

1. If the config does not exist, use:
   `{ "application": "<repository-name>", "artifact_root": "docs/features", "modules": [],
   "implementation": { "mode": "sequential", "max_parallel_agents": 3 } }`.
2. Validate a present config against `kapelle.config.schema.json`.
3. Apply defaults for omitted implementation settings.
4. Resolve the artifact root and optional module path prefixes.

## `resolveModuleHint(path)` → module | null

When modules are configured, return the module whose normalized path is the longest path-segment prefix
of the task path. The result is descriptive context passed to project capabilities. It never selects a
skill, agent, provider, or gate.

## Invariants

- Invalid explicit config fails loudly.
- Native Claude Code discovery owns project capabilities.
- Project instructions own development conventions and knowledge-provider selection.
- Agent-team mode never bypasses runtime availability, explicit approval, or file-overlap guards.
- Kapelle core does not know where rules live or how they are retrieved.
