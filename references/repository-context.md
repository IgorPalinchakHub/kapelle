# Repository architecture context

Kapelle separates shared repository architecture from branch-specific feature evidence so parallel
worktrees do not rewrite the same file.

## Shared baseline

`docs/architecture-map.md` is a repository-wide baseline:

- create it only when it does not exist and survey was invoked without a feature slug;
- treat `reflects_commit` as provenance, not as a freshness gate;
- never rewrite it automatically because the current branch diverged or moved;
- refresh it only after an explicit `/kapelle:survey --refresh-baseline` request.

A baseline refresh is repository maintenance. Before writing, show the affected sections and require
explicit confirmation. Feature worktree drift is not sufficient authorization.

## Feature-local overlay

When survey has a feature slug, write current-branch evidence to:

```text
docs/features/<slug>/_context/architecture.md
```

The overlay contains only:

- current revision provenance;
- affected modules, aspects, entrypoints, and paths;
- differences relevant to this feature;
- cited current precedents;
- project skill/subagent discovery evidence;
- architecture-rules subagent readiness.

It links to the shared baseline and never copies the whole map. `specify` and `design` read the
feature overlay first, then use the shared baseline for unchanged repository context.

If the baseline is missing, feature-scoped survey still writes only the overlay and records that no
shared baseline was available. Bootstrap the shared baseline separately outside feature worktrees.

## Worktree invariant

Normal feature stages may write only under `docs/features/<slug>/`. They must not update shared
repository artifacts merely because a worktree has a different HEAD.
