# Kapelle

Kapelle is a provider-neutral, spec-driven SDLC plugin for Claude Code.

```text
survey -> specify -> clarify -> design -> sequences -> data-model
       -> contracts -> tasks -> plan-tests -> implement -> review -> ship
```

## Core boundary

Kapelle owns:

- lifecycle stages and artifact gates;
- durable state under `docs/features/<slug>/`;
- task dependency ordering;
- explicit backend, frontend, data, and other aspect coordination through `surface-plan.json`;
- explicit generic subagent orchestration;
- adaptive execution depth that avoids duplicate agent analysis for small, low-risk work;
- sequential plan-first implementation and adaptive test strategies;
- risk-based plan approval, bounded retries, and execution telemetry;
- traceable bugfix, enhancement, and refactor lifecycles for existing features;
- optional, guarded Agent Team execution;
- native project-capability delegation;
- mandatory scoped architecture rules from a project-provided subagent;
- provider-neutral guidance and validation evidence;
- review, handoff, and audit discipline.

Kapelle does not own:

- project skill or agent routing;
- project architecture conventions;
- rule storage or retrieval;
- query generation;
- CLI, MCP, API, or knowledge-provider selection;
- unofficial workflow runtimes;
- git operations.

## Runtime model

```text
Kapelle task intent + feature artifacts
                |
                v
Native project skill + subagent discovery
                |
                v
Project architecture-rules subagent
                |
                v
Project skills / agents per feature aspect
                |
                v
Kapelle planner -> test-author -> implementer -> reviewer
                |
                v
Project validation + provider-neutral evidence
```

Project capabilities use standard Claude Code locations:

```text
.claude/skills/<name>/SKILL.md
.claude/agents/<name>.md
.claude/rules/*.md
```

Claude Code selects them from their native descriptions. Selected project subagents may discover
and delegate to narrower project skills/subagents. Kapelle has no `label → skill`, `surface → pack`,
or `skill → agent` routing table.

Each project must expose a native subagent, under any project-defined name, that can find and return
the architecture rules applicable to supplied aspects, modules, entrypoints, and paths. Kapelle
validates its provider-neutral result before design and before each implementation task.

`design` writes `surface-plan.json`. It describes aspects such as backend, frontend, database, or
other project-defined slices; provider/consumer contracts; dependency order; and cross-aspect
integration checks. It contains no capability routing.

Kapelle's bundled agents are generic SDLC execution roles. Skills dispatch them explicitly using
plugin-namespaced agent types such as `kapelle:reviewer`; an `agents:` frontmatter list is not used.

## Implementation modes

`implement` executes this per-task lifecycle:

```text
UNDERSTAND -> CLASSIFY -> SELECT-CAPABILITY -> GUIDANCE
-> TEST-STRATEGY -> PLAN -> APPROVE
-> IMPLEMENT -> REVIEW -> VALIDATE
```

Testing is adaptive: bug fixes and isolated behavior normally use strict TDD; legacy changes use
characterization; complex business logic uses scenario-first invariant coverage; external
boundaries use contract-first; migrations and configuration use validation-first.

Execution depth is also adaptive. Small, low-risk stages reuse upstream evidence and run routine
checks inline. Larger, ambiguous, cross-aspect, security-sensitive, or contract-changing work
dispatches the full independent role set. Every stage remains separately invocable; Kapelle does
not hide the lifecycle behind a one-click orchestrator.

Sequential execution is the default. Plans are always durable, while approval is controlled by
`approval_policy`. Agent Teams are opt-in and are used only when Claude Code supports them, the user
approves team creation, and dependency-ready tasks declare non-overlapping `files_hint`. Unknown or
overlapping ownership remains sequential. Kapelle does not create worktrees or use an unofficial
`Workflow` tool.

## Commands

```text
/kapelle:survey
/kapelle:specify <slug>
/kapelle:clarify <slug>
/kapelle:design <slug>
/kapelle:sequences <slug>
/kapelle:data-model <slug>
/kapelle:contracts <slug>
/kapelle:tasks <slug>
/kapelle:plan-tests <slug>
/kapelle:implement <slug>
/kapelle:review <slug>
/kapelle:ship <slug>
/kapelle:change <slug> [--mode=bugfix|enhancement|refactor] "<description>"
/kapelle:change <slug> --change=<id> --revise "<amendment>"
/kapelle:resume <slug> --change=<id>
/kapelle:fix <slug> "<bug description>"
```

## Changing an existing feature

Use one entrypoint for fixes, additions, and refactors:

```text
/kapelle:change billing --mode=enhancement "Support partial invoice cancellation"
```

Kapelle records:

```text
docs/features/billing/changes/<change-id>/
  change.json
  change.md
  active-state.json
  artifact-state/
  revisions/r001/
  reconciliation.json
  progress.jsonl
```

Before canonical feature artifacts are edited, Kapelle maps the current behavior, snapshots
impacted SDLC artifacts, identifies affected acceptance criteria, computes the smallest safe stage
route, and asks for approval.

- `bugfix` restores behavior already required by the feature;
- `enhancement` changes or expands observable behavior and updates acceptance criteria;
- `refactor` preserves observable behavior and defaults to characterization tests.

`/kapelle:fix` is a shorthand for `change --mode=bugfix`. During an approved change, every selected
stage receives `--change=<change-id>`, restricts itself to the impact matrix, and records progress.
Newly discovered impact stops execution for renewed approval instead of silently expanding scope.

### Changing requirements during implementation

```text
/kapelle:change billing --change=partial-cancel \
  --revise "Cancellation must support individual invoice lines"
```

Kapelle pauses the entire active implementation, checkpoints current evidence, creates immutable
revision `rNNN`, fingerprints affected artifacts, propagates stale state through the artifact
dependency graph, and reconciles every existing task as:

```text
keep | revalidate | rework | supersede | revert-required
```

After stale artifacts are regenerated and the revised route is approved:

```text
/kapelle:resume billing --change=partial-cancel
```

Resume recomputes fingerprints, verifies complete reconciliation, and refuses stale plans. Kapelle
never performs an automatic git revert; `revert-required` produces an explicit corrective task.

## Minimal project config

`.claude/kapelle.config.json` is optional:

```json
{
  "application": "my-app",
  "artifact_root": "docs/features",
  "guidance_evidence": "optional",
  "implementation": {
    "mode": "sequential",
    "max_parallel_agents": 3,
    "approval_policy": "risk-based",
    "max_task_attempts": 3,
    "max_agent_runs_per_task": 8,
    "telemetry": true
  },
  "modules": [
    {
      "id": "root",
      "path": "."
    }
  ]
}
```

`guidance_evidence` controls only whether evidence is required. It never chooses or configures a provider.
Set `implementation.mode` to `agent-team` to request team execution; runtime checks and explicit
approval still apply.

`risk-based` approval blocks before code for complex domain logic, public contracts, security or
authorization changes, destructive migrations, ambiguous invariants, and cross-module work. Usage
telemetry records actual host-provided token counts only; Kapelle does not invent cost estimates.

## Guidance providers

A project agent may obtain applicable guidance using native rules, project instructions, another agent,
a CLI adapter, MCP, an API, or another plugin. Kapelle consumes only:

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

A provider coupled to a particular CLI or rule repository belongs in the project or in a separate reusable
provider plugin, not in Kapelle core.
