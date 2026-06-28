# Project-native capability layout

```text
.claude/
├── agents/
│   ├── backend-implementer.md
│   └── project-guidance-provider.md
├── skills/
│   ├── service-create/
│   │   └── SKILL.md
│   └── test-create/
│       └── SKILL.md
├── rules/
│   └── optional-native-guidance.md
└── kapelle.config.json
```

Claude Code discovers capabilities from native descriptions. Kapelle provides task intent and artifact
paths; it does not map the task to a named skill, agent, gate, or provider.

`project-guidance-provider.md` is optional and project-specific. It may use a CLI, MCP, API, files, or any
other mechanism. A reusable organization-specific provider can instead ship as a separate plugin.
