# Contracts stage

The contracts stage turns declared interfaces and the shared data model into concrete contract artifacts.
It owns lifecycle gates and drift detection, not project-specific generation behavior.

## Protocol

1. Read `sad.md`, `surface-plan.json`, `data-model.md`, `sequences.md`, and existing contracts from
   disk.
2. Describe each required contract by intent, interface constraints, and expected output location.
3. Let Claude Code select applicable native project skills, agents, and tools semantically.
4. Allow the selected project capability to obtain guidance through any provider available in its
   environment.
5. Generate the contract using the selected project capability.
6. Run project-defined validation and the generic drift check, including every declared
   provider/consumer relationship.
7. Record an explicit unsupported result if no project capability can produce the contract.

## Invariants

- Kapelle core contains no contract-kind routing table.
- A new project capability requires no core edit.
- Provider selection and storage conventions remain outside Kapelle.
- Contract artifacts must agree with the shared data model and sequences.
