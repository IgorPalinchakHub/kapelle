# Kapelle

Kapelle is a human-controlled SDLC harness for Claude Code and Codex. It turns a raw developer
task into reviewable business and technical artifacts, coordinates project-native skills and
architecture rules, implements production code with human checkpoints, and completes separate
test and verification phases. It can also reconstruct evidence-backed product and as-built
architecture documentation for an existing feature without entering delivery.

```text
start -> spec -> design -> plan -> base-functional-tests
      -> implement -> unit-tests -> verify -> finalize
```

There is one public development pipeline. A separate documentation-only `reconstruct` workflow
never hands off to planning or implementation. Legacy feature directories are routed to `migrate`;
they never silently enter either workflow.

## Existing-feature reconstruction

```text
scope -> approve -> spec -> approve -> design -> approve -> review -> approve
```

`/kapelle:reconstruct` traces existing code, tests, configuration, schemas, and project
documentation. It produces a high-level `spec.md` with detailed `specs/*.md`, and a high-level
`design.md` with detailed `design/*.md`. Material claims are classified as observed, inferred,
declared, or unknown and linked to fingerprinted source evidence.

Architecture reconstruction uses the project's semantically discovered skills/subagents and its
architecture-rules subagent. Documents distinguish the as-built implementation, applicable rules,
and deviations. Documentation completion does not imply implementation, verification, or release
readiness.

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

When Kapelle needs a decision, it asks a standalone plain-language question: what it intends to
implement, why the choice matters, and the options with their trade-offs. Internal task, blocker,
DoD, gate, acceptance-criterion, and artifact identifiers are not used as human-facing context.

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
New-format overviews are capped at 280 lines and 2800 words, with a 220-line/2200-word target that
leaves editing margin. Legacy overviews receive a size warning until explicit compaction. The first design pass uses
feature-local evidence-delta discovery, one bounded architecture-rules lookup, and one bounded
high-level critic. Detailed component/domain documents, contracts, accepted ADRs, mechanical
call-site analysis, and test mechanics stay in `--detail`.

Review gates have canonical names such as `outline.json` and `business-spec.json`. Stages write
them only through the deterministic review-gate helper with exact artifact sets and full SHA-256
fingerprints; aliases and narrative approval JSON are not accepted.

All machine JSON and JSONL artifacts are checked by the bundled fail-closed JSON Schema validator
before they affect routing or stage completion. Structural validation is centralized; specialized
validators add only graph, filesystem, fingerprint, and readiness rules that JSON Schema cannot
express.

If `_kapelle/` is deleted, `/kapelle:status` reconstructs routing from the durable marker in
`proposal.md`, human documents, and current code. It never invents approvals, reviews, command
output, or validation evidence.

## Commands

```text
/kapelle:start <slug> "<raw task>" [--lane=auto|fast|standard] [--interview=auto|lean|standard|deep]
/kapelle:spec <slug> [--interview=auto|lean|standard|deep]
/kapelle:design <slug> [--detail|--revise "<feedback>"|--compact|--approve]
/kapelle:plan <slug> [--revise "<feedback>"|--approve]
/kapelle:base-functional-tests <slug> [--validation=ask|allow|skip]
/kapelle:implement <slug> [--checkpoint=task|workstream|none] [--validation=ask|allow|skip]
/kapelle:unit-tests <slug> [--validation=ask|allow|skip]
/kapelle:verify <slug> [--validation=ask|allow|skip]
/kapelle:amend <slug> "<feedback>"
/kapelle:finalize <slug> --version=1.0
/kapelle:status <slug>
/kapelle:migrate <slug> [--apply] [--lane=standard|fast]
/kapelle:reconstruct <slug> "<feature scope>"
/kapelle:reconstruct <slug> [--approve|--spec|--design|--review]
```

`design --approve` is a pure deterministic gate: it performs no repository exploration, agent
dispatch, generation, compaction, or artifact edits. On validation failure it stops and routes to
a separate `--revise` invocation. Use `--compact` explicitly to migrate a legacy long overview;
compaction never approves in the same invocation.

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
- [Reverse engineering guide (Ukrainian)](docs/RECONSTRUCTION_UK.md)
- [Usage and migration](docs/USAGE.md)
