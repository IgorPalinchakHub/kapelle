# Kapelle

Kapelle is a human-controlled SDLC harness for Claude Code and Codex. It turns a raw developer
task into reviewable business and technical artifacts, coordinates project-native skills and
architecture rules, implements production code with human checkpoints, and completes separate
test and verification phases.

```text
start -> spec -> design -> plan -> base-functional-tests
      -> implement -> unit-tests -> verify -> finalize
```

There is one public pipeline. Legacy feature directories are routed to `migrate`; they never
silently enter a second workflow.

## Planning lanes

`/kapelle:start` classifies size, risk, interview depth, and lane.

Standard lane keeps separate business, architecture, and delivery reviews:

```text
start -> spec -> design -> plan
```

Fast lane is limited to low-risk XS/S work over an established pattern:

```text
start --lane=fast -> one combined planning approval
```

Fast lane may inline the complete specification in `spec.md`, keep technical design in one
structured `design.md`, and place test strategy in `tasks.md`. It still requires architecture
rules, deterministic task validation, base functional tests, production implementation, all unit
tests, complete verification, and final developer approval.

Any security, authorization, destructive data, new public-contract, unclear ownership, or
cross-component risk escalates to standard.

## Human-readable feature package

```text
docs/features/<slug>/
  STATUS.md
  proposal.md
  spec.md
  specs/                 # standard lane, only useful business subdocuments
  design.md              # stable Arc42-inspired high-level structure
  design/                # independently reviewable detailed designs
  contracts/
  tasks.md
  test-plan.md           # standard lane; fast lane may inline it
  adr/
  diagrams/
  _context/
  _kapelle/              # derived coordination and evidence
```

`design.md` always contains Context, Constraints, Architecture rules, Building blocks, Runtime,
Data/domain, Contracts, Cross-cutting concerns, Decisions, Validation/rollout, and Open questions.
Detailed component/domain documents stay separate.

If `_kapelle/` is deleted, `/kapelle:status` reconstructs routing from the durable marker in
`proposal.md`, human documents, and current code. It never invents approvals, reviews, command
output, or validation evidence.

## Commands

```text
/kapelle:start <slug> "<raw task>" [--lane=auto|fast|standard] [--interview=auto|lean|standard|deep]
/kapelle:spec <slug> [--interview=auto|lean|standard|deep]
/kapelle:design <slug> [--detail|--revise "<feedback>"|--approve]
/kapelle:plan <slug> [--revise "<feedback>"|--approve]
/kapelle:base-functional-tests <slug> [--validation=ask|allow|skip]
/kapelle:implement <slug> [--checkpoint=task|workstream|none] [--validation=ask|allow|skip]
/kapelle:unit-tests <slug> [--validation=ask|allow|skip]
/kapelle:verify <slug> [--validation=ask|allow|skip]
/kapelle:amend <slug> "<feedback>"
/kapelle:finalize <slug> --version=1.0
/kapelle:status <slug>
/kapelle:migrate <slug> [--apply] [--lane=standard|fast]
```

Repository/design utilities such as `survey`, `sequences`, `data-model`, `contracts`,
`decide-adr`, `glossary`, and `roadmap` may enrich the same pipeline. They are not an alternative
backbone.

## Test timing

Kapelle intentionally uses:

```text
approved contracts
-> base endpoint/public-use-case functional tests
-> all production implementation
-> all unit tests
-> complete functional/integration/static/lint/build verification
```

Unit tests are not authored during `implement`. Required skipped or cancelled validation is
`validation-deferred`, never PASS.

## Project capabilities

Kapelle discovers project skills and subagents semantically. Every project supplies a native
subagent that returns architecture rules for the current aspects, modules, entrypoints, and paths.
Kapelle does not prescribe its name, storage, provider, CLI, or MCP mechanism.

Sequential execution is the default. Agent Teams require configuration, runtime support, explicit
developer approval, dependency-ready work, and pairwise-disjoint file ownership.

Kapelle never commits, pushes, merges, tags, creates branches/worktrees, or opens pull requests.

## Documentation

- [Quick start (Ukrainian)](docs/QUICK_START_UK.md)
- [Detailed command order (Ukrainian)](docs/COMMAND_EXECUTION_UK.md)
- [Usage and migration](docs/USAGE.md)
