# Lightweight dispatcher

Kapelle routes only:

```text
start -> implement -> verify
          ^           |
          +-- amend <-+
```

## Dispatch rules

1. `start` owns the minimal walking-skeleton package and approval for the current slice.
2. `implement` selects work only from that approved vertical slice.
3. The main agent discovers and applies the narrowest project capability. It reuses the
   architecture-rules evidence collected by `start` until scope changes.
4. A project architecture-rules subagent is provider-neutral; Kapelle does not prescribe its name
   or storage.
5. Planner, implementer, reviewer, explorer, critic, and Agent Teams are optional risk/uncertainty
   tools, not mandatory hops.
6. Machine artifacts used for routing are structurally validated with `validate_json.py`.
   `--pointer` validates a typed component and `--jsonl` validates line-oriented evidence.
   Structural failure blocks dispatch.
7. Implementation checkpoint defaults to workstream. Never intentionally leave the project
   unloadable between checkpoints.
8. Unit tests are not written during production implementation.
9. `verify` writes all unit tests and one feature-level verification record.
10. Each next requirement enters `amend`, which adds one vertical slice and preserves the working
    base. Unchanged local defects remain in the current workstream.
11. Only deterministic scripts write approvals, manifest, state, and STATUS.
12. No git mutations are allowed.

Optional `_kapelle/surface-plan.json` or task graphs may coordinate genuinely parallel work, shared
contracts, migrations, or complex dependencies. Normal features do not require them.
