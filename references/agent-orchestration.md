# Agent orchestration

The main agent is the default coordinator, planner, implementer, and first reviewer. Subagents are
tools for uncertainty or risk, not required stage hops.

## Triggered roles

- `explorer`: unclear ownership, unfamiliar modules, or a narrowly parallel read-only search.
- `critic`: material ambiguity or a high-risk plan.
- `reviewer`: high-risk implementation, design deviation, repeated failure, or explicit request.
- `business-analyst` and `devils-advocate`: exceptional complex business ambiguity only; never a
  default chain.
- `implementation-planner` and `implementer`: optional when independently delegated work is safer
  than main-agent execution.
- `test-author`: optional during final unit-test writing or specialized test infrastructure work.
- `change-reconciler`: optional for audited/high-risk amendments.

Use at most one critic/reviewer correction pass. Do not retry an unavailable optional role; continue
inline and disclose the reduced review. A required project architecture-rules capability has no
generic substitute.

## Bounded investigation bursts

For a medium/large feature with unfamiliar cross-component scope, the main agent may run one
parallel read-only burst of at most three disjoint investigations:

- observed behavior and ownership;
- applicable project architecture rules;
- contracts, tests, data, and integrations.

Each subagent has one concrete question, a narrow path/module scope, and a concise evidence return.
Subagents do not edit the human package. The main agent resolves contradictions and authors the
single specification/design.

## Agent Teams

Agent Teams require runtime support, explicit developer approval, stable approved contracts,
dependency-ready work, and pairwise-disjoint file ownership. Use at most three implementation
agents in one bounded burst. Good partitions are an independent backend provider, frontend
consumer, and worker/integration after their contract is fixed.

Do not use Agent Teams for the first tightly coupled walking skeleton, shared domain-model or
migration work, or when agents would edit common configuration/contracts. Otherwise execute
sequentially.

## Loop limits

- discovery: one pass plus one targeted expansion;
- plan/design critique: one pass and one correction;
- implementation correction: at most two attempts;
- final reviewer: one pass and one correction.

After a limit is reached, ask one standalone developer question or report the unresolved risk. Do
not create self-sustaining analyst/critic/reviewer loops.

Never expose raw role output as a developer question.
