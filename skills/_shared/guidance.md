# Project Guidance

Before writing code, the selected project capability should obtain applicable guidance using whatever
mechanism the project or user environment provides. Examples include native `.claude/rules`, project
instructions, another agent, an MCP tool, a CLI adapter, an API, or no external provider.

Kapelle consumes only provider-neutral evidence:

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

Kapelle never prescribes search topics, rule codes, storage layout, a CLI command, or a provider name.
When project config requires evidence, absent evidence or blocking gaps stop code-writing.
