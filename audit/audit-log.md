# Implementation audit log

Kapelle records how each task was delegated and validated without interpreting a project's guidance
provider.

## Record shape

```json
{
  "task_id": "T1",
  "capability": {
    "skill": "provider-reported name",
    "agent": "provider-reported name or default"
  },
  "guidance": {
    "status": "GUIDANCE_READY | GUIDANCE_UNAVAILABLE | GUIDANCE_BLOCKED",
    "sources": ["provider-defined reference"],
    "items": [
      {
        "title": "Short title",
        "summary": "Applicable direction",
        "source": "provider-defined source"
      }
    ],
    "gaps": []
  },
  "validation": {
    "status": "passed | failed",
    "commands": ["project-reported command"],
    "evidence": ["project-reported output reference"]
  },
  "outcome": "implemented | blocked",
  "ts": "host timestamp"
}
```

Kapelle does not assign `curated`/`discovered` labels, require rule codes, or know how guidance was found.
Those semantics belong to the provider.

## Location

Append records to:

```text
docs/features/<slug>/_audit/implementation.jsonl
```

## Assertions

- Every completed task has capability-selection and passing validation evidence.
- Guidance evidence is present only when configured as required or when a provider supplies it.
- Blocking provider gaps prevent completion when guidance evidence is required.
- Audit recording never grants Kapelle ownership of provider behavior.
