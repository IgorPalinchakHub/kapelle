# Using Kapelle

For a command-by-command Ukrainian guide with inputs, internal behavior, outputs, approval points,
and next steps, see [Детальний порядок команд](COMMAND_EXECUTION_UK.md).

Kapelle is a staged SDLC harness. You run one stage at a time, review its durable artifact, clear the
conversation context, and run the next command printed by the stage handoff.

Kapelle owns lifecycle gates, plans, evidence, and generic execution roles. Project-specific skills,
subagents, architecture rules, tools, and validation commands remain native project capabilities.

## 1. Project prerequisites

Kapelle expects:

- project instructions such as `AGENTS.md` or `CLAUDE.md`;
- native project skills and subagents with accurate descriptions;
- a project subagent that can find architecture rules for supplied aspects, modules, entrypoints,
  and paths;
- working project validation commands;
- an optional `.claude/kapelle.config.json`.

The architecture-rules subagent may have any project-defined name. Its description must make the
capability semantically discoverable and its output must match
`dispatcher/architecture-guidance.schema.json`. See
`config/shapes/architecture-rules-agent.shape.md`.

Kapelle encourages selected project subagents to discover and delegate to narrower project skills
and subagents. Kapelle does not maintain a stack, surface, label, or agent routing registry.

## 2. Choose the correct entry path

| Situation | Start with |
|---|---|
| Shared architecture baseline does not exist | `/kapelle:survey` outside a feature worktree |
| New feature, including new behavior added to existing code | `/kapelle:survey <slug>` then `/kapelle:specify <slug>` |
| Kapelle feature artifacts already exist | `/kapelle:change <slug> --mode=... "<description>"` |
| Bug restoring behavior already required by the spec | `/kapelle:fix <slug> "<bug>"` |
| Requirements change during active implementation | `/kapelle:change <slug> --change=<id> --revise "<amendment>"` |

The decisive distinction is whether `docs/features/<slug>/` already contains the canonical Kapelle
feature artifacts. Existing application code alone does not make it an existing Kapelle feature.

## 3. Repository survey and worktrees

### Bootstrap the shared baseline

Run once, preferably from the integration branch before creating feature worktrees:

```text
/kapelle:survey
```

If `docs/architecture-map.md` already exists, this command reports `BASELINE-READY` and does not
rewrite it.

`reflects_commit` is provenance only. A divergent feature branch never makes the shared map stale
and never authorizes an automatic refresh.

### Inspect a feature worktree

```text
/kapelle:survey <slug>
```

This writes only:

```text
docs/features/<slug>/_context/architecture.md
```

It records current-branch evidence relevant to the feature and never creates or updates
`docs/architecture-map.md`, even when the shared baseline is missing.

### Explicit baseline maintenance

```text
/kapelle:survey --refresh-baseline
```

Kapelle shows the proposed shared-map changes and requires explicit confirmation. Do not use this
as a normal feature-worktree step.

## 4. New feature workflow

Use this path when the feature has no canonical Kapelle artifacts yet, even if it extends existing
application code.

```text
/kapelle:survey <slug>
/clear
/kapelle:specify <slug> ["<feature idea>"]
/clear
/kapelle:clarify <slug>
/clear
/kapelle:design <slug>
/clear
/kapelle:sequences <slug>
/clear
/kapelle:data-model <slug>
/clear
/kapelle:contracts <slug>
/clear
/kapelle:decompose <slug>
/clear
/kapelle:plan-tests <slug>
/clear
/kapelle:implement <slug>
/clear
/kapelle:feature-review <slug>
/clear
/kapelle:ship <slug>
```

Follow the handoff printed by each stage. A stage may write a `SKIPPED-confirmed` artifact when its
concern does not apply; do not skip commands merely because a feature looks simple.

Execution depth is adaptive:

- `lean` reuses evidence and avoids duplicate subagent runs;
- `standard` dispatches focused independent roles;
- `full` is selected for material ambiguity, security, public contracts, destructive data work, or
  unestablished cross-aspect coordination.

Depth changes analysis cost, not artifact, architecture-rule, acceptance-criteria, or validation
requirements.

### Example

```text
/kapelle:survey configurable-invoice-status-in-pipe
/clear
/kapelle:specify configurable-invoice-status-in-pipe \
  "Allow the invoice status used in the processing pipe to be configured while preserving the current default"
```

Then continue with the exact command in the handoff.

## 5. Existing feature changes

Use `change` when canonical artifacts already exist under `docs/features/<slug>/`.

### Enhancement

An enhancement expands or changes observable behavior:

```text
/kapelle:change configurable-invoice-status-in-pipe \
  --mode=enhancement \
  "Allow invoice status in the processing pipe to be configured while preserving the current status as the default"
```

### Bugfix

A bugfix restores behavior already required by the accepted specification:

```text
/kapelle:change <slug> --mode=bugfix "<description>"
```

The shorthand is:

```text
/kapelle:fix <slug> "<description>"
```

### Refactor

A refactor preserves observable behavior:

```text
/kapelle:change <slug> --mode=refactor "<description>"
```

Kapelle captures the current baseline, affected acceptance criteria, artifact impacts, risks, and
the smallest safe stage route. Review that assessment and respond with one of:

```text
approve
request changes: <feedback>
abort
```

After approval, run only the stages in the printed route. Preserve the change id on every command:

```text
/kapelle:<stage> <slug> --change=<change-id>
```

Do not invent a route or omit `--change`; use the exact handoff.

## 6. Requirements changing during implementation

Do not locally edit the plan and continue. Create a revision:

```text
/kapelle:change <slug> --change=<change-id> --revise "<amendment>"
```

Kapelle:

1. pauses further implementation dispatch;
2. checkpoints current evidence;
3. creates an immutable `rNNN` revision;
4. fingerprints impacted artifacts;
5. propagates stale state through artifact dependencies;
6. reconciles tasks as `keep`, `revalidate`, `rework`, `supersede`, or `revert-required`;
7. presents a new minimal route for approval.

After the approved stale artifacts are regenerated:

```text
/kapelle:resume-change <slug> --change=<change-id>
```

Resume refuses unexplained drift, incomplete reconciliation, or a plan based on old fingerprints.

## 7. Multi-aspect features

`design` creates `surface-plan.json`. Aspects are project-defined and may include backend, frontend,
database, worker, mobile, CLI, or another required slice.

The plan records:

- aspect ownership and dependencies;
- modules and entrypoints;
- provider/consumer contracts;
- cross-aspect integration checks.

`decompose` converts this into a dependency DAG. `implement` discovers applicable project skills and
subagents independently for each task aspect. Shared contracts are established before consumers,
and final validation covers the declared integration checks.

For M/L/XL work, `tasks.json` also contains architecture-aligned workstreams. Every task has one
primary aspect, explicit validation, risk, contract role, and file-ownership status. Kapelle runs
`scripts/validate_task_plan.py`; standard/hierarchical decomposition receives one independent critic
pass and at most one correction pass. Large feature size does not force every low-risk task into
full-cost execution.

The durable decomposition evidence is stored in `_audit/task-plan-validation.txt` and, for M/L/XL,
`_audit/decomposition-review.json`.

Parallel Agent Team execution remains opt-in. It requires runtime support, explicit approval,
dependency-ready tasks, and pairwise-disjoint `files_hint`. Kapelle does not create branches or
worktrees.

## 8. Implementation approvals

Every task has a durable implementation plan. Approval behavior comes from
`.claude/kapelle.config.json`:

- `always`: approve every task plan;
- `risk-based`: approve complex domain logic, public contracts, security/authorization, destructive
  migrations, ambiguous invariants, and cross-module changes;
- `never`: record the plan and continue without waiting.

Validation-command permission is separate from plan approval. Configure:

```json
{
  "validation": {
    "development_policy": "ask"
  }
}
```

- `ask` (default): show the exact tests, PHPStan/static-analysis, lint, build, and other commands;
- `allow`: run the planned validation batch without another prompt;
- `skip`: defer project validation during development.

For one invocation:

```text
/kapelle:implement <slug> --validation=ask
/kapelle:implement <slug> --validation=allow
/kapelle:implement <slug> --validation=skip
```

Under `ask`, choose `run-all`, `run-selected`, or `skip-all`. Cancelling a running command records
it as cancelled and does not trigger an automatic retry. Required skipped/cancelled checks set the
task to `validation-deferred`; later run `implement --validation=allow` to execute outstanding
checks. Deferred validation is never `PASS` and blocks `ship`.

When approval is required, silence is never approval. Use:

```text
approve
request changes: <feedback>
reject
```

## 9. Outputs to review

Typical feature state:

```text
docs/features/<slug>/
  _context/architecture.md
  .size
  spec.md
  sad.md
  surface-plan.json
  sequences.md
  data-model.md
  contracts/
  tasks.json
  test-plan.md
  adr/
  _audit/
    architecture-guidance/
    plans/
    implementation.jsonl
    implementation-telemetry.jsonl
  _review/
  ship.md
```

Kapelle never performs git operations. Review, commit, push, and pull-request actions remain under
developer control.

## 10. Common statuses

### Missing input

```text
Status: REFUSED-missing-input
missing: <path>
run-first: <stage>
```

Run the named stage first. Do not create a placeholder file.

### Missing architecture-rules capability

```text
Status: REFUSED-missing-project-capability
capability: project architecture-rules subagent
```

Add or expose the required project subagent with a semantically clear description.

### Architecture guidance blocked

Resolve the reported rule-source or scope gaps before design or code-writing.

### Contract drift

Update the shared data model, sequence, contract, or requirement through the appropriate stage.
Do not weaken the drift gate locally.

### Revision required

Use `/kapelle:change ... --revise`, regenerate the approved stale route, then run
`/kapelle:resume-change`.

### Attempt limit reached

Kapelle stops editing and preserves evidence. Revise the plan, acceptance criteria, constraints, or
task decomposition before retrying.

## 11. Command reference

| Command | Purpose |
|---|---|
| `/kapelle:survey [<slug>]` | Bootstrap shared context or create a feature-local worktree overlay |
| `/kapelle:survey --refresh-baseline` | Explicitly maintain the shared architecture baseline |
| `/kapelle:specify <slug> ["<feature idea>"]` | Resolve input once, then create goals, stories, requirements, and acceptance criteria |
| `/kapelle:clarify <slug>` | Resolve remaining requirement ambiguity |
| `/kapelle:design <slug>` | Apply project architecture rules and produce SAD, ADRs, and aspect plan |
| `/kapelle:sequences <slug>` | Describe runtime and cross-aspect flows |
| `/kapelle:data-model <slug>` | Define shared data/schema impact or an explicit no-change result |
| `/kapelle:contracts <slug>` | Generate and validate provider/consumer contracts |
| `/kapelle:decompose <slug>` | Build the dependency-ordered implementation DAG |
| `/kapelle:plan-tests <slug>` | Map acceptance criteria and integration checks to validation |
| `/kapelle:implement <slug>` | Plan, approve, implement, review, and validate tasks |
| `/kapelle:feature-review <slug>` | Run independent feature-level review |
| `/kapelle:ship <slug>` | Verify readiness and write ship notes without git actions |
| `/kapelle:change ...` | Start or revise an existing-feature change |
| `/kapelle:resume-change ...` | Resume an approved reconciled revision |
| `/kapelle:fix ...` | Bugfix shorthand |
