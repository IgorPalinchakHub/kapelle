# Backbone and Utility Handoff

Use this at the end of each backbone stage:

```md
## <stage> — <slug>

**What I did**
- <what existed, what changed, and the practical result>

**Review before continuing**
- <important decision or limitation explained briefly>; `<artifact>` is supporting evidence

**Run next**
`/kapelle:<next-stage> <slug>`
```

Keep a simple-change handoff to the result, a material limitation if any, checks, and the next
action. Never hand back only filenames, paragraph references, or identifiers. Follow
`developer-questions.md` for current/proposal/consequence explanations. Do not add another review
round for each document or repeat a decision the developer already made.

When the handoff mentions a task or workstream identifier, immediately pair it with its short
human-readable title or outcome from `tasks.md`. Never make the developer remember a bare `W2`,
`T04`, or similar identifier. Prefer the outcome first when the identifier adds no value.

```md
**Next workstream**
`W2` — remove the legacy unpublish flow

**Run next**
`/kapelle:implement <slug> --checkpoint=workstream --validation=ask`
```

Recommend `/clear` only when the current context is noisy or an independent final review matters.
Do not require it between normal workstream checkpoints.

Optional utilities use the same readable sections but label the heading `utility`. They never
invent a second pipeline. When they change `spec.md`, `design.md`, `tasks.md`, an ADR, or a durable
contract, their next command is `/kapelle:start <slug> --approve`; otherwise it is
`/kapelle:status <slug>`.
