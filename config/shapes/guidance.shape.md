# Guidance evidence shape

Kapelle accepts guidance evidence from any project or user capability:

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

Kapelle does not define provider discovery, rule storage, query generation, source labels, or retrieval
commands. Providers may use native files, project instructions, CLI tools, MCP, APIs, agents, or no
external storage.
