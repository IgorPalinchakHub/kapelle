# Kapelle

Kapelle is an incremental, human-controlled SDLC harness for Claude Code and Codex. It first maps
the known feature in a high-level specification and system design, then implements the smallest
production-shaped walking skeleton and grows it one developer-requested vertical slice at a time.

```text
start base -> approve -> implement
                          |
              amend next slice -> approve -> implement
                          |
                        verify
```

The normal feature package is intentionally small:

```text
docs/features/<slug>/
  STATUS.md
  spec.md
  specs/            # optional detailed promoted use cases
  design.md
  design/           # optional domain model or focused technical detail
  tasks.md
  _kapelle/          # derived state, approvals, rules evidence, final verification
```

ADRs, contracts, detailed design, and diagrams are optional. Kapelle creates them only when they
remain useful to a developer after the feature is complete.

## Normal commands

```text
/kapelle:start <slug> "<raw developer task>"
/kapelle:start <slug> --revise "<feedback>"
/kapelle:start <slug> --approve

/kapelle:implement <slug> --checkpoint=workstream --validation=ask

/kapelle:verify <slug> --validation=ask
/kapelle:verify <slug> --developer-verified "<what passed>"
/kapelle:verify <slug> --approve

/kapelle:amend <slug> "<changed requirement or feedback>"
/kapelle:status <slug>
```

`start` inspects existing behavior, obtains scoped project architecture rules, and writes a
high-level map of the known feature and system boundaries. It details and plans only the smallest
production-shaped walking skeleton. Future capabilities remain non-binding candidates. The
developer approves this first vertical slice before code.

`implement` builds that end-to-end slice. The main agent plans and codes directly, reusing project
guidance. Planner/implementer/reviewer subagent chains are not the default. Focused boundary or
characterization tests are written before risky production changes when useful.

After each slice, the developer chooses:

```text
/kapelle:amend <slug> "<next business or technical requirement>"
/kapelle:start <slug> --approve
/kapelle:implement <slug>

# or, when accumulated behavior is sufficient:
/kapelle:verify <slug>
```

`verify` reconciles the as-built feature with the docs, writes all unit tests, and runs one
risk-based validation batch. If the developer already completed that batch manually or in another
session, Kapelle accepts an explicit passing confirmation without requiring copied output and
labels the result `developer-attested`. A second, explicit approval completes the feature.

Detailed use-case specifications, `design/domain-model.md`, contracts, sequences, and ADRs are
created just in time when their documented trigger applies. A simple slice stays in `spec.md` and
`design.md`.

## Human control

- Default checkpoint is one workstream, not one micro-task.
- Start with one walking-skeleton workstream; split it into at most three checkboxes only when
  needed for review.
- Each requested increment becomes one coherent vertical slice and leaves the application loadable.
- Development validation can be `ask`, `allow`, or `skip`; deferred required checks block final
  approval until they pass or the developer explicitly confirms complete external verification.
- Developer questions describe the intended behavior and concrete options with trade-offs. They do
  not expose task, blocker, DoD, gate, or artifact identifiers.
- In Claude Code, bundled validators run as one direct `python3` command using the plugin and
  project root substitutions. Kapelle does not prepend `cd`, assign a temporary path variable, or
  combine helper calls, so a narrow `Bash(python3:*)` permission can match them.
- Project-native read-only CLIs use the same direct-command shape and consume the tool result
  without scratchpad redirection, so narrow project command permissions can match them.
- File inspection uses native file tools or one direct command with the tool working directory;
  Kapelle does not emit `cd` plus shell loops or inspect other branches with Git.
- Kapelle never runs git mutations.

## Project capabilities

Kapelle discovers relevant project skills, instructions, and the project architecture-rules
subagent semantically. Architecture guidance is collected once during `start` and reused until the
scope changes. Medium/large discovery may use one read-only burst of at most three agents. Agent
Teams remain opt-in, are not used for the first skeleton, and require stable contracts plus safe,
disjoint ownership.

## Optional utilities

The normal route needs only `start`, `implement`, `amend`, `verify`, and `status`. Use these
standalone utilities only when their output is independently useful:

```text
/kapelle:survey [<slug>]          # repository baseline or feature-local architecture context
/kapelle:decide-adr <slug>        # one durable architectural decision
/kapelle:contracts <slug>         # human-readable boundary contracts
/kapelle:data-model <slug>        # data/schema and domain-model impact
/kapelle:sequences <slug>         # complex runtime flow
/kapelle:glossary <slug>          # disputed domain terms
/kapelle:roadmap <slug>           # project roadmap placement
```

Utilities do not form another pipeline. If one changes the approved feature package, return to
`/kapelle:start <slug> --approve`; otherwise return to status.

## Existing feature directories

Old Kapelle features are not routed through the former multi-stage pipeline:

```text
/kapelle:migrate <slug>
/kapelle:migrate <slug> --apply
```

Migration preserves human documents and historical evidence, adopts the lightweight marker, and
never invents approvals or validation results.

If `_kapelle/` is deleted, `/kapelle:status` rebuilds routing from `spec.md`, `design.md`,
`tasks.md`, and current code. Checked work becomes `implemented-unverified` until a current
verification PASS exists.

## Documentation-only reconstruction

`/kapelle:reconstruct` remains a separate workflow for explaining code that already exists. It
classifies claims as observed, inferred, declared, or unknown and never enters implementation or
release.

## Documentation

- [Quick start (Ukrainian)](docs/QUICK_START_UK.md)
- [Detailed command order (Ukrainian)](docs/COMMAND_EXECUTION_UK.md)
- [Usage and migration](docs/USAGE.md)
- [Reverse engineering guide (Ukrainian)](docs/RECONSTRUCTION_UK.md)
