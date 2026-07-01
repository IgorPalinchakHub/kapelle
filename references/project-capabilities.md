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

Project-specific capabilities live in the project itself or in separate reusable plugins.

## Discovery behavior

For each feature aspect or task, inspect native skill and subagent descriptions and select the
smallest applicable capability set. The selected project subagent is encouraged to discover and
delegate to other project skills or subagents when their descriptions match a narrower part of the
work. This recursive native discovery is allowed; a Kapelle-maintained routing registry is not.

Record:

- the selected capability names and kinds (`skill`, `subagent`, or host-default);
- the task/aspect intent each capability covers;
- why its native description matches;
- uncovered capability gaps.

Names are evidence, not configuration. A future project capability can replace an existing one
without changing Kapelle core.

Architecture-rule discovery is a required specialized project capability governed by
[`architecture-guidance.md`](./architecture-guidance.md).
