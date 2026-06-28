# Extension shapes

Kapelle integrates with native Claude Code resources rather than maintaining a runtime extension registry.

| Shape | Location | Selection |
|---|---|---|
| [Project skill](./skill.shape.md) | `.claude/skills/<name>/SKILL.md` | Native semantic discovery |
| [Project agent](./agent.shape.md) | `.claude/agents/<name>.md` | Native semantic discovery |
| [Guidance evidence](./guidance.shape.md) | Provider-defined | Returned through a minimal provider-neutral contract |

Distribution packs may bundle these files for installation, but their metadata does not participate in
runtime selection.
