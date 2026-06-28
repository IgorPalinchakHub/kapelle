# No-git / irreversible-action guard

Extends the [gated-stage backbone](./_stage-contract.md) (T13). Standing invariant (sad §2): the harness
performs **zero version control** and no destructive action outside its own artifacts — the **Developer**
owns every irreversible action (AC-09, ADR-0007, sad Flow 5).

## What the guard intercepts

Before any stage performs an action, classify it:

| Action | Classification | Guard verdict |
|---|---|---|
| Write/overwrite the harness's **own** artifact files (`docs/features/<slug>/…`, `kapelle/…` it owns) | reversible (artifact-is-state) | **ALLOW** |
| Any **version-control** op (`git init/add/commit/push/tag/branch/reset/rebase/…`) | irreversible | **DECLINE → hand back** |
| A **destructive** op **outside** the harness's own artifacts (delete/move/overwrite a source file, drop a DB, `rm -rf`, publish, deploy) | irreversible | **DECLINE → hand back** |

The boundary is: *is the target one of the harness's own on-disk artifacts?* If yes → allowed (writing
its own state is not irreversible, ADR-0007). If no, or if it is version control → declined.

## Decline protocol

When an irreversible action is reached, the stage does **not** perform it. It emits:

```
Status: DECLINED-irreversible
action: <the requested action>
reason: the harness owns no irreversible actions — version control and destructive ops stay with the Developer
hand-back: <exact step the Developer should run, e.g. `git add . && git commit -m "…"`>
```

…and returns control to the Developer. The harness holds **no capability** to perform the action — this is
a structural absence, not a permission check it could be talked past.

## Invariants

- **No-git, always.** There is no code path in any stage that runs version control.
- **Own artifacts are exempt** — writing/overwriting `docs/features/<slug>/…` is the normal mechanism, not
  an irreversible action.
- **Confirmed, never silent** — a declined action is always reported with the hand-back step.
