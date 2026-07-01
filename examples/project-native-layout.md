# Project-native capability layout

```text
.claude/
├── agents/
│   ├── backend-implementer.md
│   ├── frontend-implementer.md
│   └── architecture-rules.md
├── skills/
│   ├── service-create/
│   │   └── SKILL.md
│   └── test-create/
│       └── SKILL.md
├── rules/
│   └── optional-native-guidance.md
└── kapelle.config.json
```

Claude Code discovers capabilities from native descriptions. Kapelle provides task intent, aspect,
and artifact paths; it does not map the task to a named skill, agent, gate, or provider. Selected
project agents may discover and delegate to narrower project skills/subagents.

`architecture-rules.md` is required, but its filename and provider are project-defined. Its
description must make the capability semantically discoverable, and it returns evidence matching
`dispatcher/architecture-guidance.schema.json`. It may use a CLI, MCP, API, files, or any other
project-supported mechanism.
