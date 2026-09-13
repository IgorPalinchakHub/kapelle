# Agent shape

Core agents are generic SDLC roles distributed with Kapelle. Project agents are standard Claude Code
resources at `.claude/agents/<name>.md`.

Project agents may select project skills and guidance providers available in their environment. Kapelle
does not map tasks to agent names and does not prescribe how an agent obtains rules or other guidance.

Architecture-rule lookup is owned by the project skill described in
[`architecture-rules-skill.shape.md`](./architecture-rules-skill.shape.md). That skill decides whether
to delegate to a project agent; Kapelle does not require or select that agent directly.

Agents should read referenced files directly, keep their scope bounded, return typed evidence, and avoid
git operations unless the user explicitly owns that action outside Kapelle.
