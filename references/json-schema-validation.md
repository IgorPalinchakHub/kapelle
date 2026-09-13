# Deterministic JSON artifact validation

Kapelle never asks an LLM to decide whether a machine artifact conforms to JSON Schema.
Bundled helpers follow [`script-execution.md`](./script-execution.md).

## Structural validation

Use validate_json.py with the artifact path and its exact dispatcher schema, following the
command in the invoking SKILL.md. For nested legacy records use --pointer; for telemetry use
--jsonl; --schema-only audits a schema without an instance. These are validator options, not
additional required outputs. Obtain absolute paths from the invoking skill, never from shell
expansion of text read from this reference.

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
