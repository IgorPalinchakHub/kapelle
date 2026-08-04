# Direct command execution

## Bundled Python helpers

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

## Project-native read-only commands

Apply the same command shape to an allowlisted read-only CLI discovered through a project skill,
subagent, or instruction:

```text
<project-read-cli> search --source "<rules-path>" --query "<focused query>" --json
```

The executable must be the first token. Run one CLI invocation per Bash tool call and consume its
stdout, stderr, and exit status from the standard tool result.

Do not prefix the command with `cd`, `env`, an assignment, a shell, or a subshell. Do not append
`echo $?`, redirect stdout or stderr to a scratchpad, or combine commands with `;`, `&&`, `||`, or
a pipe. If output is too broad, make the query narrower and run another direct invocation.

The Bash tool call is synchronous: wait for its result normally. Never launch the CLI in the
background and never create a follow-up polling command using `while`, `sleep`, file-existence
tests, `head`, `tail`, or `cat` against a scratchpad. If a tool call is still running, use the
provider's native continuation/wait mechanism rather than shell polling.

This lets a project grant only the intended command family, for example
`Bash(<project-read-cli> *)`. A PreToolUse auto-allow hook is unnecessary for Kapelle's normal command
shapes and would have to parse arbitrary shell syntax safely.

## Filesystem and repository inspection

Apply the direct-command rule to every shell inspection. Use the tool call's working-directory
field instead of shell `cd`. Prefer native Read, Glob, and Search capabilities for the current
worktree.

Never generate a shell program containing `for`, `while`, `if`, arithmetic expansion, or repeated
commands merely to inspect several paths. Use one native bulk command when the project explicitly
provides one, or make separate bounded tool calls.

Kapelle performs no Git operations. Do not inspect branches, commits, or repository objects with
`git cat-file`, `git show`, `git ls-tree`, or similar commands during a Kapelle stage. If the
developer explicitly requests a branch comparison outside the Kapelle workflow, treat it as a
separate developer operation rather than stage evidence.
