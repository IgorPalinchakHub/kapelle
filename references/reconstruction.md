# As-built reconstruction contract

`/kapelle:reconstruct` documents an existing feature from current repository evidence. It is a
documentation workflow, not a shortcut into the development backbone.

## Durable package

The workflow uses the regular feature layout:

```text
docs/features/<slug>/
  STATUS.md
  proposal.md
  spec.md
  specs/*.md
  design.md
  design/*.md
  contracts/*.md          # when useful
  _context/evidence-index.md
  _kapelle/
    workflow.json
    reconstruction.json
    reconstruction-coverage.json
    architecture-guidance/
    approvals/
```

`spec.md` and `design.md` are concise maps. At least one independently useful detail document is
created under both `specs/` and `design/`; further splitting follows real business or architecture
boundaries rather than classes or layers.

## Evidence model

Every material product or architecture claim has a stable `RC-NNN` id and one classification:

- `observed`: directly supported by executable code, configuration, schema, or test evidence;
- `inferred`: a reasoned interpretation of multiple observed facts;
- `declared`: stated by project documentation or architecture rules but not proven by execution;
- `unknown`: material behavior or intent that current evidence cannot establish.

Observed and inferred claims cite repository-relative paths and exact line ranges. The coverage
record fingerprints every cited source and every generated human artifact. A source or artifact
change makes the review stale.

Tests are evidence of behavior, not automatically product intent. Names and comments are evidence
only at `declared` or `inferred` strength unless implementation corroborates them.

## Architecture truth

Technical documents clearly distinguish:

- **As-built** — what the current implementation does;
- **Rule** — scoped guidance returned by the project's architecture-rules subagent;
- **Deviation** — where the implementation and applicable rule differ.

Do not rewrite a deviation as the desired architecture. Do not invent business rationale for an
implementation pattern.

## Gates

The workflow is:

```text
scope -> approve -> spec -> approve -> design -> approve -> review -> approve
```

The generic `--approve` approves only the current draft and stores exact artifact fingerprints.
Silence is never approval. A `BLOCKED` review cannot be approved.

Completion means that the documentation package was reviewed against current evidence. It does not
mean the feature was implemented, verified for release, or shipped. The workflow never hands off to
`plan`, `implement`, test stages, or `finalize`.
