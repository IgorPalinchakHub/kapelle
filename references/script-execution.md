# Bundled script execution

Run every Kapelle Python helper as one plain `python3` command from the project root:

```text
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/<script>.py" "${CLAUDE_PROJECT_DIR}/<project-path>" ...
```

Claude Code substitutes both placeholders in plugin skill content before the model sees it. In a
provider that does not substitute them, replace each placeholder with the normalized absolute
plugin root and project root shown by that provider before executing the command.

Never prefix a helper with `cd`, an environment-variable assignment such as `K=...`, `env`, a
subshell, or a shell wrapper. Never join it to another command with `;`, `&&`, `||`, or a pipe.
Run multiple helpers as separate tool calls. Do not execute an unresolved placeholder.

This shape keeps the executable and arguments auditable, preserves the caller's project working
directory, and lets a narrow Claude Code permission such as `Bash(python3:*)` match without
auto-allowing unrelated compound shell commands.
