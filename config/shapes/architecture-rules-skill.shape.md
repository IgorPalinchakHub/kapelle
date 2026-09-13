# Project architecture-rules skill shape

Each project supplies a native skill whose description makes architecture-rule lookup semantically
discoverable, for example `.claude/skills/<project-defined-name>/SKILL.md` or the host's equivalent.
Its name is project-defined; an existing broader project skill may provide this procedure.

```md
---
name: <project-defined-name>
description: >
  Find and return the project architecture rules applicable to supplied feature aspects, modules,
  entrypoints, and file paths. Use for design, implementation planning, and code review.
---

Read the supplied feature artifacts and scope. Before using an external index, verify that its
repository, modules, and framework match the current project; discard an off-target index. Honor a
supplied lookup budget and return binding rules, source references, collisions, and design-changing
gaps rather than an exhaustive catalogue. Specify where to search and which project-supported
providers to use. If a subagent is needed, specify its selection and invocation procedure here;
otherwise read the relevant sources directly. Report blocking gaps instead of guessing.
```

The skill may use files, native rules, MCP, CLI, APIs, or project subagents. Kapelle does not prescribe
its tools, provider, rule identifiers, or storage. The main agent records the selected skill and
normalizes its findings into `dispatcher/architecture-guidance.schema.json`; the project skill does
not need a Kapelle-specific output format and never invokes Kapelle stages.
