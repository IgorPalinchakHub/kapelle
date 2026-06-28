# Shared Stage Contract

Each stage declares its required inputs and outputs.

Protocol:

1. Check required artifacts on disk.
2. If missing, refuse with `Status: REFUSED-missing-input | missing: <path> | run-first: <stage>`.
3. Read inputs from disk. Do not depend on previous chat context.
4. Produce only the stage's own artifact(s).
5. Emit the stage-handoff block.

This mirrors `stages/_stage-contract.md`, but is short enough to load with each Claude Code skill.
