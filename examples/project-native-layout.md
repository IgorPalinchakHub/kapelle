# Project-native capability layout

```text
.claude/
├── agents/
│   ├── backend-implementer.md
│   └── frontend-implementer.md
├── skills/
│   ├── architecture-rules/
│   │   └── SKILL.md
│   ├── service-create/
│   │   └── SKILL.md
│   └── test-create/
│       └── SKILL.md
└── rules/
    └── optional-native-guidance.md
```

Claude Code discovers capabilities from native descriptions. Kapelle provides task intent, aspect,
and artifact paths; it does not map the task to a named skill, agent, gate, or provider. Selected
project agents may discover and delegate to narrower project skills/subagents.

An architecture-rule lookup skill is required, but its name and provider are project-defined. Its
description must make the capability semantically discoverable. Its procedure decides where to
search and which subagent to use, if any; direct file, CLI, MCP, and API lookup are also supported.
The main agent normalizes its findings into `dispatcher/architecture-guidance.schema.json` with
`capability.kind: project-skill`. Kapelle does not require a separate architecture-rules agent.
