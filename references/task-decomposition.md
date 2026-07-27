# Workstream decomposition

`tasks.md` is a developer checklist of implemented and currently approved slices, not the known
use-case map and not a speculative full-feature micro-task graph.

## Rules

- Start with one walking-skeleton workstream. Split it into at most three checkboxes only when a
  single checkpoint would not be reviewable.
- Each later developer-requested requirement adds one smallest coherent vertical slice.
- Keep the known feature map in `spec.md`; only promoted committed behavior enters `tasks.md`.
- Order by real dependency and keep coupling low.
- Do not split by layers when endpoint, use case, persistence, compatibility, and boundary test must
  change together.
- Every checkpoint leaves the project loadable and internally coherent.
- Include focused pre-change functional/characterization coverage in the owning workstream.
- Keep candidate capabilities out of `tasks.md`; they remain non-binding hypotheses in `spec.md`.
- Do not add unit-test workstreams; all unit tests are written in `verify`.
- State only outcome, important dependency, expected observable behavior, and short result.

Use optional machine dependency/file-ownership graphs only for true parallel work, shared
contracts, migrations, or complex dependency safety.
