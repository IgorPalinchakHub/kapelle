# Kapelle

Kapelle is a provider-neutral, spec-driven SDLC plugin for Claude Code.

```text
survey -> specify -> clarify -> design -> sequences -> data-model
       -> contracts -> tasks -> plan-tests -> implement -> review -> ship
```

## Core boundary

Kapelle owns:

- lifecycle stages and artifact gates;
- durable state under `docs/features/<slug>/`;
- task dependency ordering;
- explicit generic subagent orchestration;
- sequential test-first implementation and structured role verdicts;
- optional, guarded Agent Team execution;
- native project-capability delegation;
- provider-neutral guidance and validation evidence;
- review, handoff, and audit discipline.

Kapelle does not own:

- project skill or agent routing;
- project architecture conventions;
- rule storage or retrieval;
- query generation;
- CLI, MCP, API, or knowledge-provider selection;
- unofficial workflow runtimes;
- git operations.

## Runtime model

```text
Kapelle task intent + feature artifacts
                |
                v
Claude Code native project capability discovery
                |
                v
Project skill / agent
                |
                v
Any project or user guidance provider (optional)
                |
                v
Kapelle test-author -> implementer -> reviewer
                |
                v
Project validation + provider-neutral evidence
```

Project capabilities use standard Claude Code locations:

```text
.claude/skills/<name>/SKILL.md
.claude/agents/<name>.md
.claude/rules/*.md
```

Claude Code selects them from their native descriptions. Kapelle has no `label → skill`,
`surface → pack`, or `skill → agent` routing table.

Kapelle's bundled agents are generic SDLC execution roles. Skills dispatch them explicitly using
plugin-namespaced agent types such as `kapelle:reviewer`; an `agents:` frontmatter list is not used.

## Implementation modes

`implement` always executes this per-task lifecycle:

```text
SELECT-CAPABILITY -> GUIDANCE -> RED -> GREEN -> REFACTOR -> VERIFY -> GATE
```

Sequential execution is the default. Agent Teams are opt-in and are used only when Claude Code
supports them, the user approves team creation, and at least two dependency-ready tasks declare
non-overlapping `files_hint`. Unknown or overlapping ownership remains sequential. Kapelle does not
create worktrees or use an unofficial `Workflow` tool.

## Commands

```text
/kapelle:survey
/kapelle:specify <slug>
/kapelle:clarify <slug>
/kapelle:design <slug>
/kapelle:sequences <slug>
/kapelle:data-model <slug>
/kapelle:contracts <slug>
/kapelle:tasks <slug>
/kapelle:plan-tests <slug>
/kapelle:implement <slug>
/kapelle:review <slug>
/kapelle:ship <slug>
```

## Minimal project config

`.claude/kapelle.config.json` is optional:

```json
{
  "application": "my-app",
  "artifact_root": "docs/features",
  "guidance_evidence": "optional",
  "implementation": {
    "mode": "sequential",
    "max_parallel_agents": 3
  },
  "modules": [
    {
      "id": "root",
      "path": "."
    }
  ]
}
```

`guidance_evidence` controls only whether evidence is required. It never chooses or configures a provider.
Set `implementation.mode` to `agent-team` to request team execution; runtime checks and explicit
approval still apply.

## Guidance providers

A project agent may obtain applicable guidance using native rules, project instructions, another agent,
a CLI adapter, MCP, an API, or another plugin. Kapelle consumes only:

```json
{
  "status": "GUIDANCE_READY",
  "guidance": [
    {
      "title": "Short title",
      "summary": "Applicable direction",
      "source": "provider-defined source"
    }
  ],
  "sources": ["provider-defined reference"],
  "gaps": []
}
```

A provider coupled to a particular CLI or rule repository belongs in the project or in a separate reusable
provider plugin, not in Kapelle core.
