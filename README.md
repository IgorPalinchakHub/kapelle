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
- native project-capability delegation;
- provider-neutral guidance and validation evidence;
- review, handoff, and audit discipline.

Kapelle does not own:

- project skill or agent routing;
- project architecture conventions;
- rule storage or retrieval;
- query generation;
- CLI, MCP, API, or knowledge-provider selection;
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
Implementation + project validation + provider-neutral evidence
```

Project capabilities use standard Claude Code locations:

```text
.claude/skills/<name>/SKILL.md
.claude/agents/<name>.md
.claude/rules/*.md
```

Claude Code selects them from their native descriptions. Kapelle has no `label → skill`,
`surface → pack`, or `skill → agent` routing table.

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
  "modules": [
    {
      "id": "root",
      "path": "."
    }
  ]
}
```

`guidance_evidence` controls only whether evidence is required. It never chooses or configures a provider.

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

## Distribution packs

`packs/backend` and `packs/worker` are install-time example bundles. A pack manifest contains only bundle
identity and version. The installer discovers its `skills/`, `agents/`, and optional `rules/` files and
installs them into standard `.claude` locations.

```bash
python3 scripts/install_project_pack.py \
  --pack backend \
  --project /path/to/project \
  --dry-run

python3 scripts/install_project_pack.py \
  --pack backend \
  --project /path/to/project
```

The manifest is not copied to the target project and is never read at runtime. Identical files are skipped;
conflicts require an explicit `--force`.
