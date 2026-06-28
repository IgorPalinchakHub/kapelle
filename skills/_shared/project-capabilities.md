# Native Project Capabilities

Project development behavior is supplied through standard Claude Code resources:

```text
.claude/skills/<name>/SKILL.md
.claude/agents/<name>.md
.claude/rules/*.md
project or user plugins and MCP tools
```

Kapelle provides task intent, acceptance criteria, artifact paths, and repository hints. Claude Code
selects applicable project capabilities semantically from their native descriptions. Kapelle does not
maintain `label → skill`, `surface → pack`, or `skill → agent` mappings.

A distribution pack may install native resources, but its manifest is not read at runtime.
