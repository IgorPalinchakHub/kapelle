#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from jsonschema_lite import (
    audit_schema,
    validate_file,
    validate_file_at_pointer,
    validate_instance,
    validate_jsonl_file,
)

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS = ROOT / "dispatcher"


class JsonSchemaLiteTests(unittest.TestCase):
    def test_every_dispatcher_schema_uses_supported_subset_and_resolvable_refs(self) -> None:
        schemas = sorted(SCHEMAS.glob("*.schema.json"))
        self.assertEqual(26, len(schemas))
        failures = {
            path.name: audit_schema(path)
            for path in schemas
            if audit_schema(path)
        }
        self.assertEqual({}, failures)

    def test_existing_examples_validate_structurally(self) -> None:
        for instance, schema in [
            ("surface-plan.json", "surface-plan.schema.json"),
            ("architecture-guidance.json", "architecture-guidance.schema.json"),
            ("task-plan.json", "task-plan.schema.json"),
        ]:
            with self.subTest(instance=instance):
                self.assertEqual(
                    [],
                    validate_file(ROOT / "examples" / instance, SCHEMAS / schema),
                )

    def test_allof_if_then_and_min_properties(self) -> None:
        schema = SCHEMAS / "base-functional-tests.schema.json"
        blocked = {
            "status": "BLOCKED",
            "scope": [],
            "test_files": [],
            "covered_contracts": [],
            "input_fingerprints": {"spec.md": "a" * 64},
        }
        self.assertEqual([], validate_instance(blocked, schema))
        ready = dict(blocked, status="READY")
        errors = validate_instance(ready, schema)
        self.assertTrue(any("fewer than 1 items" in item for item in errors))
        no_fingerprints = dict(blocked, input_fingerprints={})
        self.assertTrue(validate_instance(no_fingerprints, schema))

    def test_oneof_and_union_types(self) -> None:
        schema = SCHEMAS / "workflow-state.schema.json"
        self.assertEqual(
            [],
            validate_instance(
                {
                    "workflow": "human-controlled",
                    "version": 1,
                    "created_from": "raw-task",
                    "lane": "standard",
                },
                schema,
            ),
        )
        self.assertTrue(
            validate_instance(
                {
                    "workflow": "human-controlled",
                    "version": 1,
                    "created_from": "raw-task",
                },
                schema,
            )
        )

    def test_local_and_relative_refs(self) -> None:
        task_plan = json.loads((ROOT / "examples" / "task-plan.json").read_text())
        task_plan["tasks"][0]["status"] = "not-a-task-state"
        self.assertTrue(
            validate_instance(task_plan, SCHEMAS / "task-plan.schema.json")
        )
        request = {
            "change_id": "change-1",
            "feature_slug": "feature",
            "mode": "enhancement",
            "description": "Changed behavior",
            "current_revision": 1,
            "active_state_path": "_kapelle/changes/change-1/state.json",
            "baseline": {
                "observed_behavior": [],
                "artifact_snapshots": [],
                "code_evidence": [],
            },
            "impacted_acceptance_criteria": [],
            "artifact_impacts": {
                "spec": "update",
                "design": "review",
                "surface_plan": "none",
                "sequences": "none",
                "data_model": "none",
                "contracts": "none",
                "test_plan": "review",
                "tasks": "review",
            },
            "route": ["start"],
            "approval": "pending",
            "status": "assessed",
        }
        self.assertEqual(
            [], validate_instance(request, SCHEMAS / "change-request.schema.json")
        )
        request["artifact_impacts"]["spec"] = "invalid"
        self.assertTrue(
            validate_instance(request, SCHEMAS / "change-request.schema.json")
        )

    def test_format_and_integer_do_not_accept_boolean(self) -> None:
        schema = SCHEMAS / "feature-manifest.schema.json"
        instance = {
            "layout_version": 2,
            "schema_version": "1.0",
            "slug": "feature",
            "human_artifacts": {},
            "recovery": {"mode": "native", "evidence_loss": []},
            "state_built_at": "not-a-date",
        }
        self.assertTrue(validate_instance(instance, schema))
        instance["state_built_at"] = "2026-07-25T17:00:00+00:00"
        self.assertEqual([], validate_instance(instance, schema))
        instance["layout_version"] = True
        self.assertTrue(validate_instance(instance, schema))

    def test_unknown_keyword_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            schema = Path(tmp) / "schema.json"
            schema.write_text(json.dumps({"type": "string", "maxItems": 1}))
            self.assertTrue(audit_schema(schema))

    def test_malformed_supported_keyword_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            schema = Path(tmp) / "schema.json"
            schema.write_text(
                json.dumps(
                    {
                        "type": "object",
                        "required": "name",
                        "$ref": 42,
                    }
                )
            )
            errors = audit_schema(schema)
            self.assertTrue(any(".required:" in item for item in errors))
            self.assertTrue(any(".$ref:" in item for item in errors))

    def test_json_lines_reports_record_number(self) -> None:
        event = {
            "run_id": "run-1",
            "slug": "feature",
            "task_id": "TASK-1",
            "event": "completed",
            "status": "PASS",
            "agent_runs": 1,
            "edit_attempts": 1,
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "execution.jsonl"
            path.write_text(
                json.dumps(event)
                + "\n\n"
                + json.dumps(dict(event, event="unknown"))
                + "\n"
            )
            errors = validate_jsonl_file(
                path, SCHEMAS / "execution-telemetry.schema.json"
            )
            self.assertEqual(1, len(errors))
            self.assertIn("line 3:", errors[0])

    def test_instance_json_pointer_selects_nested_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "run.json"
            path.write_text(
                json.dumps(
                    {
                        "review": {
                            "task_id": "TASK-1",
                            "role": "reviewer",
                            "status": "PASS",
                            "summary": "Reviewed",
                            "evidence": [],
                        }
                    }
                )
            )
            self.assertEqual(
                [],
                validate_file_at_pointer(
                    path,
                    SCHEMAS / "execution-verdict.schema.json",
                    "/review",
                ),
            )
            self.assertTrue(
                validate_file_at_pointer(
                    path,
                    SCHEMAS / "execution-verdict.schema.json",
                    "/missing",
                )
            )


if __name__ == "__main__":
    unittest.main()
