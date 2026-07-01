# Agent shape

Core agents are generic SDLC roles distributed with Kapelle. Project agents are standard Claude Code
resources at `.claude/agents/<name>.md`.

Project agents may select project skills and guidance providers available in their environment. Kapelle
does not map tasks to agent names and does not prescribe how an agent obtains rules or other guidance.

One project agent must expose the architecture-rules capability described in
[`architecture-rules-agent.shape.md`](./architecture-rules-agent.shape.md). Its name remains
project-defined and it returns typed, scope-specific evidence.

Agents should read referenced files directly, keep their scope bounded, return typed evidence, and avoid
git operations unless the user explicitly owns that action outside Kapelle.
