# Using Kapelle

Kapelle is a staged SDLC harness. It keeps the feature documentation readable for people and puts
machine-only execution state under `_kapelle/`.

For a detailed Ukrainian command guide, see
[Детальний порядок команд](COMMAND_EXECUTION_UK.md).

## 1. What a feature looks like

```text
docs/features/<slug>/
  STATUS.md        # generated entry point: current state, blockers, next command
  proposal.md      # why and scope
  spec.md          # observable behavior for product/QA
  design.md        # technical/as-built specification for developers
  tasks.md         # compact workstream checklist
  test-plan.md     # validation strategy and commands
  contracts/       # developer-facing boundaries
  adr/             # important decisions
  _context/        # optional feature-local repository evidence
  _kapelle/        # machine state, evidence, history, telemetry
```

Open `STATUS.md` first. Normal review should not require reading `_kapelle/`.

Human documents are durable state. `_kapelle/` contains derived execution state and historical
evidence. If it is deleted, Kapelle can continue from the documents, current code/tests, and project
architecture rules. It cannot recreate deleted approvals, old review verdicts, command output,
telemetry, or validation results.

## 2. Project prerequisites

Kapelle expects:

- project instructions such as `AGENTS.md` or `CLAUDE.md`;
- native project skills/subagents with accurate descriptions;
- a project subagent that can find architecture rules for supplied aspects, modules, entrypoints,
  and paths;
- project validation commands;
- optional `.claude/kapelle.config.json`.

The architecture-rules subagent may have any project-defined name. Its output must match
`dispatcher/architecture-guidance.schema.json`. Missing capability produces:

```text
Status: REFUSED-missing-project-capability
```

Kapelle discovers project capabilities semantically. It has no stack/surface/agent routing table.

## 3. Choose an entry point

| Situation | Command |
|---|---|
| Shared architecture baseline is missing | `/kapelle:survey` |
| New feature or newly documented behavior | `/kapelle:survey <slug>` then `/kapelle:specify <slug>` |
| Feature directory already exists or `_kapelle/` may be stale/missing | `/kapelle:status <slug>` |
| Change to an existing documented feature | `/kapelle:change <slug> --mode=... "<description>"` |
| Bug restoring accepted behavior | `/kapelle:fix <slug> "<bug>"` |
| Requirements changed during implementation | `/kapelle:change <slug> --change=<id> --revise "<amendment>"` |

Existing application code alone does not make an existing Kapelle feature. Existing human feature
documents do.

## 4. Survey and worktrees

Bootstrap the shared baseline once:

```text
/kapelle:survey
```

If `docs/architecture-map.md` already exists, Kapelle reports `BASELINE-READY` and does not rewrite
it. `reflects_commit` is provenance only.

In a feature worktree:

```text
/kapelle:survey <slug>
```

This writes only:

```text
docs/features/<slug>/_context/architecture.md
```

Branch divergence never triggers a shared-map refresh. Explicit maintenance requires:

```text
/kapelle:survey --refresh-baseline
```

and user confirmation.

## 5. Normal feature workflow

```text
/kapelle:survey <slug>
/clear
/kapelle:specify <slug> "<problem and desired observable outcome>"
/clear
/kapelle:clarify <slug>
/clear
/kapelle:design <slug>
/clear
/kapelle:contracts <slug>        # only when declared interfaces need artifacts
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

`sequences` and `data-model` remain available as focused design enrichers for unusually complex
runtime/data work. They are not mandatory empty ceremony.

Every backbone stage refreshes `STATUS.md` and prints the exact next command. Use `/clear` between
substantial stages so the next stage proves it can resume from disk.

## 6. Status and recovery

Run:

```text
/kapelle:status <slug>
```

It:

1. reads the human feature package;
2. validates `_kapelle/manifest.json` and state;
3. recovers derived state when missing or corrupt;
4. reconciles documented task claims with available code/test evidence;
5. writes `STATUS.md`;
6. reports evidence that cannot be reconstructed;
7. selects the minimal next command.

A checked task without current validation evidence becomes `implemented-unverified`, not
`completed`. Recovery therefore never makes a feature falsely shippable.

The deterministic utilities are:

```text
python3 scripts/build_feature_status.py docs/features/<slug>
python3 scripts/rebuild_feature_state.py docs/features/<slug>
python3 scripts/validate_feature_state.py docs/features/<slug>
```

The host agent performs semantic code/architecture reconciliation; the scripts only derive
document/evidence state and never run code, tests, git, or network operations.

## 7. Legacy feature migration

Preview first:

```text
python3 scripts/migrate_feature_layout.py docs/features/<slug> --dry-run
```

Apply only after reviewing collisions/actions:

```text
python3 scripts/migrate_feature_layout.py docs/features/<slug> --apply
```

Migration is explicit and idempotent. It maps `sad.md` to `design.md`, creates readable
`proposal.md`/`tasks.md` where possible, moves machine state under `_kapelle/`, and preserves
historical evidence under `_kapelle/history/legacy/`.

## 8. Multi-aspect design and decomposition

`design` writes `_kapelle/surface-plan.json` with:

- backend/frontend/data/other aspects;
- dependencies and entrypoints;
- provider/consumer contracts;
- cross-aspect integration checks.

`decompose` writes:

```text
tasks.md
_kapelle/task-plan.json
_kapelle/task-plan-validation.txt
_kapelle/reviews/decomposition.json   # M/L/XL
```

For an M feature, prefer 3–7 workstreams and 7–15 tasks. This is a readability signal, not a reason
to weaken architecture or acceptance-criteria coverage.

`scripts/validate_task_plan.py` deterministically checks graph acyclicity, AC coverage, contract
provider/consumer ordering, integration ownership, and safe parallel file ownership.

## 9. Implementation and validation policy

Each task follows:

```text
UNDERSTAND -> CLASSIFY -> SELECT-CAPABILITY -> GUIDANCE
-> TEST-STRATEGY -> PLAN -> APPROVE -> IMPLEMENT -> REVIEW -> VALIDATE
```

Sequential mode is default. Agent Teams require runtime support, explicit user approval,
dependency-ready tasks, and pairwise-disjoint file ownership.

Development validation is independent from plan approval:

```json
{
  "validation": {
    "development_policy": "ask"
  }
}
```

- `ask` shows exact tests/static analysis/linters/build commands;
- `allow` runs the planned batch;
- `skip` runs none during development.

Per invocation:

```text
/kapelle:implement <slug> --validation=ask
/kapelle:implement <slug> --validation=allow
/kapelle:implement <slug> --validation=skip
```

Under `ask`, answer `run-all`, `run-selected`, or `skip-all`. Required skipped/cancelled checks
become `validation-deferred`; they never count as `PASS` and block ship readiness.

Per-task evidence lives in:

```text
_kapelle/task-runs/<task-id>.json
_kapelle/validation/<task-id>.json
_kapelle/telemetry/execution.jsonl
```

## 10. Existing-feature changes

```text
/kapelle:change <slug> --mode=enhancement "<observable behavior change>"
/kapelle:change <slug> --mode=bugfix "<accepted behavior to restore>"
/kapelle:change <slug> --mode=refactor "<behavior-preserving internal change>"
```

Kapelle captures baseline evidence, affected ACs, artifact impact, risk, and the minimal route.
Canonical edits start only after explicit approval.

Change state lives under:

```text
_kapelle/changes/<change-id>/
```

When requirements or architecture change mid-implementation:

```text
/kapelle:change <slug> --change=<change-id> --revise "<amendment>"
```

Kapelle pauses implementation, creates an immutable revision, invalidates downstream state,
reconciles tasks, and requests route approval. Resume only with:

```text
/kapelle:resume-change <slug> --change=<change-id>
```

## 11. Final convergence and ship

Feature review reconciles:

```text
proposal <-> final scope
spec <-> observable implementation
design <-> technical implementation
contracts <-> providers/consumers
tasks <-> implemented work
test-plan <-> validation
ADR <-> actual decisions
```

It writes:

```text
_kapelle/reviews/documentation-convergence.json
_kapelle/reviews/feature-review.json
```

Ship refuses stale review fingerprints, contract/document drift, active changes, or required
deferred validation. Successful readiness is shown in `STATUS.md`; optional human release notes use
`release.md`.

Kapelle never performs git operations. Commits, pushes, pull requests, and merges remain under
developer control.

## 12. Command reference

| Command | Purpose |
|---|---|
| `/kapelle:survey [<slug>]` | Shared baseline or feature-local architecture overlay |
| `/kapelle:status <slug>` | Show/rebuild status and recover minimal route |
| `/kapelle:specify <slug> ["<idea>"]` | Write proposal, product spec, ACs, and size |
| `/kapelle:clarify <slug>` | Resolve requirement ambiguity |
| `/kapelle:design <slug>` | Apply project architecture rules and write technical design |
| `/kapelle:sequences <slug>` | Optional complex runtime-flow enrichment |
| `/kapelle:data-model <slug>` | Optional focused data/schema enrichment |
| `/kapelle:contracts <slug>` | Produce declared provider/consumer contracts |
| `/kapelle:decompose <slug>` | Write readable tasks and validated machine graph |
| `/kapelle:plan-tests <slug>` | Map ACs/integration checks to validation |
| `/kapelle:implement <slug>` | Plan, implement, review, and validate tasks |
| `/kapelle:feature-review <slug>` | Check as-built documentation and implementation |
| `/kapelle:ship <slug>` | Verify readiness without git actions |
| `/kapelle:change ...` | Start or revise an existing-feature change |
| `/kapelle:resume-change ...` | Resume an approved reconciled revision |
| `/kapelle:fix ...` | Bugfix shorthand |

