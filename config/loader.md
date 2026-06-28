# Config loader

The loader reads the optional `.claude/kapelle.config.json` and provides SDLC artifact and module context.
It does not register packs, skills, agents, gates, rules, or knowledge providers.

## `load()` → ResolvedConfig

1. If the config does not exist, use:
   `{ "application": "<repository-name>", "artifact_root": "docs/features", "modules": [] }`.
2. Validate a present config against `kapelle.config.schema.json`.
3. Resolve the artifact root and optional module path prefixes.

## `resolveModuleHint(path)` → module | null

When modules are configured, return the module whose normalized path is the longest path-segment prefix
of the task path. The result is descriptive context passed to project capabilities. It never selects a
skill, agent, provider, or gate.

## Invariants

- Invalid explicit config fails loudly.
- Native Claude Code discovery owns project capabilities.
- Project instructions own development conventions and knowledge-provider selection.
- Kapelle core does not know where rules live or how they are retrieved.
