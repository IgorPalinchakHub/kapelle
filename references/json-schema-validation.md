# Deterministic JSON artifact validation

Kapelle never asks an LLM to decide whether a machine artifact conforms to JSON Schema.
Bundled helpers follow [`script-execution.md`](./script-execution.md).

## Structural validation

Run:

```text
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate_json.py" "<absolute-artifact-path>" "${CLAUDE_PLUGIN_ROOT}/dispatcher/<artifact>.schema.json"
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate_json.py" "<absolute-task-run-path>" "${CLAUDE_PLUGIN_ROOT}/dispatcher/<component>.schema.json" --pointer /<component>
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate_json.py" "<absolute-events-path>" "${CLAUDE_PLUGIN_ROOT}/dispatcher/execution-telemetry.schema.json" --jsonl
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate_json.py" ignored "${CLAUDE_PLUGIN_ROOT}/dispatcher/<artifact>.schema.json" --schema-only
```

The bundled validator implements exactly the JSON Schema subset used by Kapelle. It audits every
schema before validating an instance and fails closed when a new unsupported keyword, unresolved
reference, escaping reference, malformed pattern, or unsupported format appears.

## Semantic readiness

Schema validity proves shape, types, required fields, and declared constraints only. Stage
validators separately enforce facts JSON Schema cannot express, including:

- current fingerprints and approvals;
- acyclic dependency graphs;
- acceptance-criterion and contract ownership;
- referenced artifact existence and path confinement;
- architecture guidance readiness rather than merely a schema-valid `BLOCKED` result.

Machine artifacts may be used for routing or stage completion only after both layers pass.

## Maintenance rule

JSON Schema is the single source of truth for structure. Python stage validators must call the
shared engine and contain only cross-file, graph, filesystem, freshness, or readiness semantics.
`validate_plugin.py` audits every dispatcher schema so schema-language drift fails plugin
validation immediately.
