# Project architecture-rules subagent shape

Each project provides one native subagent whose description makes this capability semantically
discoverable. Its name is project-defined.

```md
---
name: <project-defined-name>
description: >
  Find and return the project architecture rules applicable to supplied feature aspects, modules,
  entrypoints, and file paths. Use for design, implementation planning, and code review.
---

Read the supplied feature artifacts and scope. Before using an external index, verify that its
repository, modules, and framework match the current project; discard an off-target index. Honor a
supplied lookup budget and return binding rules, collisions, and design-changing gaps rather than
an exhaustive catalogue. Obtain rules through the project's own supported providers. Return only
evidence matching `dispatcher/architecture-guidance.schema.json`. Report blocking gaps instead of
guessing.
```

The agent may use project skills, files, native rules, MCP, CLI, APIs, or other agents. Kapelle does
not prescribe its tools, provider, rule identifiers, or storage.
