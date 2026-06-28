# Native project skill shape

A project skill is a standard Claude Code resource at `.claude/skills/<name>/SKILL.md`. Its native
frontmatter description is the discovery contract. Kapelle does not register or route it.

## Expected behavior

- Read task and artifact paths from disk.
- State the project-specific purpose and applicability clearly enough for semantic discovery.
- Accept provider-neutral guidance when supplied.
- Run the project's own implementation and validation protocol.
- Return changed files, validation evidence, gaps, and a typed outcome.
- Never invoke an earlier or later Kapelle lifecycle stage.
