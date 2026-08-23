#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from feature_state import (
    FeatureStateError,
    document_fingerprints,
    file_fingerprint,
    initialize_feature_state,
    input_fingerprints,
    normalized_task_plan_fingerprint,
    normalized_tasks_fingerprint,
    parse_tasks,
    phase_evidence_current,
    rebuild_feature_state,
    refresh_feature_status,
    relative_fingerprint,
)
from migrate_feature_layout import apply_migration, migration_plan
from validate_feature_state import validate
from validate_task_plan import validate as validate_task_plan
from validate_design import REQUIRED_HEADINGS
from validate_progressive_docs import (
    ARTIFACT_MARKER,
    DESIGN_HEADINGS as PROGRESSIVE_DESIGN_HEADINGS,
    SPEC_HEADINGS,
    WORKFLOW_MARKER,
)


class FeatureStateTests(unittest.TestCase):
    def valid_design(self) -> str:
        lines = ["# Design", ""]
        for heading in REQUIRED_HEADINGS:
            lines.extend([heading, "", "Current evidence or not applicable.", ""])
        return "\n".join(lines)

    def valid_guidance(self, aspects: list[str]) -> dict[str, object]:
        return {
            "status": "ARCHITECTURE_GUIDANCE_READY",
            "capability": {
                "name": "project-architecture-rules",
                "kind": "project-subagent",
            },
            "scope": {
                "aspects": aspects,
                "modules": [],
                "entrypoints": [],
                "paths": [],
            },
            "rules": [],
            "sources": [],
            "gaps": [],
        }

    def progressive_document(self, title: str, headings: list[str]) -> str:
        lines = [title, ""]
        for heading in headings:
            lines.extend([heading, "", "Concrete content.", ""])
        return "\n".join(lines)

    def make_feature(self, root: Path, *, checked: bool = False) -> Path:
        feature = root / "docs" / "features" / "readable-feature"
        feature.mkdir(parents=True)
        (feature / "proposal.md").write_text(
            "# Readable feature\n\n## Summary\n\nMake feature state readable.\n"
        )
        context = feature / "_context"
        context.mkdir()
        (context / "architecture.md").write_text("# Architecture context\n")
        (feature / "spec.md").write_text(
            "# Specification\n\n- **AC-01** Status is visible.\n"
        )
        (feature / "design.md").write_text(self.valid_design())
        marker = "x" if checked else " "
        (feature / "tasks.md").write_text(
            f"# Tasks\n\n## Delivery\n\n- [{marker}] **T01 Build status** — covers AC-01\n"
        )
        (feature / "test-plan.md").write_text("# Test plan\n\nRun unit tests.\n")
        internal = feature / "_kapelle"
        internal.mkdir()
        source = root / "src" / "feature.txt"
        source.parent.mkdir()
        source.write_text("implemented behavior\n")
        (internal / "surface-plan.json").write_text(
            json.dumps(
                {
                    "slug": "readable-feature",
                    "aspects": [
                        {
                            "id": "core",
                            "intent": "status",
                            "modules": [],
                            "entrypoints": [],
                            "depends_on": [],
                        }
                    ],
                    "contracts": [],
                    "integration_checks": [],
                }
            )
        )
        (internal / "task-plan.json").write_text(
            json.dumps(
                {
                    "slug": "readable-feature",
                    "decomposition_depth": "standard",
                    "architecture_guidance_path": "_kapelle/architecture-guidance/tasks.json",
                    "workstreams": [
                        {
                            "id": "WS",
                            "title": "Delivery",
                            "intent": "Deliver readable state",
                            "aspects": ["core"],
                            "depends_on": [],
                            "completion_task_id": "T01",
                            "completion_signal": "Status is visible",
                        }
                    ],
                    "tasks": [
                        {
                            "id": "T01",
                            "title": "Build status",
                            "intent": "Build status",
                            "workstream_id": "WS",
                            "deps": [],
                            "acs": ["AC-01"],
                            "dod": "Status is visible",
                            "module_hint": None,
                            "primary_aspect": "core",
                            "aspects": ["core"],
                            "entrypoint_hint": None,
                            "provides_contracts": [],
                            "consumes_contracts": [],
                            "integration_checks": [],
                            "validation": [
                                {
                                    "kind": "inspection",
                                    "procedure": "Inspect status",
                                    "expected": "Status is visible",
                                }
                            ],
                            "risk": "low",
                            "parallel_candidate": False,
                            "ownership_status": "known",
                            "files_hint": ["src/feature.txt"],
                            "status": "implemented-unverified" if checked else "pending",
                        }
                    ],
                    "split_recommendations": [],
                }
            )
        )
        return feature

    def write_pass_validation(self, feature: Path, task_id: str = "T01") -> Path:
        path = feature / "_kapelle" / "validation" / f"{task_id}.json"
        path.parent.mkdir(exist_ok=True)
        implementation = feature.parent.parent.parent / "src" / "feature.txt"
        path.write_text(
            json.dumps(
                {
                    "task_id": task_id,
                    "policy": "allow",
                    "decision": "run-all",
                    "commands": [
                        {
                            "command": "project-test",
                            "kind": "tests",
                            "scope": "feature",
                            "required": True,
                            "status": "passed",
                        }
                    ],
                    "input_fingerprints": input_fingerprints(feature),
                    "implementation_fingerprints": {
                        "src/feature.txt": file_fingerprint(implementation)
                    },
                }
            )
        )
        return path

    def write_deferred_validation(
        self, feature: Path, task_id: str = "T01"
    ) -> Path:
        path = feature / "_kapelle" / "validation" / f"{task_id}.json"
        path.parent.mkdir(exist_ok=True)
        implementation = feature.parent.parent.parent / "src" / "feature.txt"
        path.write_text(
            json.dumps(
                {
                    "task_id": task_id,
                    "policy": "skip",
                    "decision": "skip-all",
                    "commands": [
                        {
                            "command": "project-test",
                            "kind": "tests",
                            "scope": "feature",
                            "required": True,
                            "status": "skipped",
                            "reason": "Developer ran verification outside Kapelle",
                        }
                    ],
                    "input_fingerprints": input_fingerprints(feature),
                    "implementation_fingerprints": {
                        "src/feature.txt": file_fingerprint(implementation)
                    },
                }
            )
        )
        return path

    def write_approval(
        self, feature: Path, gate: str, fingerprints: dict[str, str]
    ) -> None:
        path = feature / "_kapelle" / "approvals" / f"{gate}.json"
        path.parent.mkdir(exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "gate": gate,
                    "status": "approved",
                    "confirmation": f"Developer approved {gate}",
                    "artifact_fingerprints": fingerprints,
                }
            )
        )

    def make_reconstruction(self, root: Path) -> Path:
        feature = root / "docs" / "features" / "existing-flow"
        feature.mkdir(parents=True)
        (feature / "proposal.md").write_text(
            "<!-- kapelle-workflow: reconstruction-v1 -->\n"
            "# Existing flow\n\n## Summary\n\nDocument current behavior.\n"
        )
        context = feature / "_context"
        context.mkdir()
        (context / "evidence-index.md").write_text(
            "# Evidence index\n\n- RC-001 — observed in `src/flow.txt:1`.\n"
        )
        internal = feature / "_kapelle"
        internal.mkdir()
        (internal / "workflow.json").write_text(
            json.dumps(
                {
                    "workflow": "reconstruction",
                    "version": 1,
                    "created_from": "existing-code",
                }
            )
        )
        (internal / "reconstruction.json").write_text(
            json.dumps(
                {
                    "slug": "existing-flow",
                    "scope": "Current existing flow",
                    "aspects": ["backend"],
                    "entrypoints": ["src/flow.txt"],
                    "exclusions": [],
                    "unknowns": [],
                }
            )
        )
        source = root / "src" / "flow.txt"
        source.parent.mkdir()
        source.write_text("current behavior\n")
        return feature

    def test_reconstruction_routes_only_documentation_gates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            feature = self.make_reconstruction(root)
            internal = feature / "_kapelle"
            _, state = initialize_feature_state(feature)
            self.assertEqual("reconstruct-scope", state["current_stage"])
            self.assertEqual(
                "/kapelle:reconstruct existing-flow --approve",
                state["next_command"],
            )

            self.write_approval(
                feature,
                "reconstruction-scope",
                {
                    "proposal.md": file_fingerprint(feature / "proposal.md"),
                    "_kapelle/reconstruction.json": file_fingerprint(
                        internal / "reconstruction.json"
                    ),
                },
            )
            _, state, _ = refresh_feature_status(feature)
            self.assertEqual("reconstruct-spec", state["current_stage"])

            (feature / "spec.md").write_text(
                "# Product specification\n\n- **AC-01** Current behavior occurs. RC-001\n"
            )
            (feature / "specs").mkdir()
            (feature / "specs" / "behavior.md").write_text(
                "# Behavior\n\nRC-001 is observed.\n"
            )
            self.write_approval(
                feature,
                "reconstruction-spec",
                {
                    "spec.md": file_fingerprint(feature / "spec.md"),
                    "specs": document_fingerprints(feature)["specs"],
                },
            )
            _, state, _ = refresh_feature_status(feature)
            self.assertEqual("reconstruct-design", state["current_stage"])

            (feature / "design.md").write_text(self.valid_design())
            (feature / "design").mkdir()
            (feature / "design" / "backend.md").write_text(
                "# Backend\n\nAs-built behavior is RC-001.\n"
            )
            guidance = internal / "architecture-guidance"
            guidance.mkdir()
            (guidance / "reconstruction.json").write_text(
                json.dumps(self.valid_guidance(["backend"]))
            )
            (internal / "surface-plan.json").write_text(
                json.dumps(
                    {
                        "slug": "existing-flow",
                        "aspects": [
                            {
                                "id": "backend",
                                "intent": "Document existing flow",
                                "modules": ["src"],
                                "entrypoints": ["src/flow.txt"],
                                "depends_on": [],
                            }
                        ],
                        "contracts": [],
                        "integration_checks": [],
                    }
                )
            )
            self.write_approval(
                feature,
                "reconstruction-design",
                {
                    "spec.md": file_fingerprint(feature / "spec.md"),
                    "specs": document_fingerprints(feature)["specs"],
                    "design.md": file_fingerprint(feature / "design.md"),
                    "design": document_fingerprints(feature)["design"],
                    "_kapelle/surface-plan.json": file_fingerprint(
                        internal / "surface-plan.json"
                    ),
                    "_kapelle/architecture-guidance": (
                        relative_fingerprint(
                            feature, "_kapelle/architecture-guidance"
                        )
                    ),
                },
            )
            _, state, _ = refresh_feature_status(feature)
            self.assertEqual("reconstruct-review", state["current_stage"])
            self.assertEqual(
                "/kapelle:reconstruct existing-flow --review",
                state["next_command"],
            )

            source = root / "src" / "flow.txt"
            (internal / "reconstruction-coverage.json").write_text(
                json.dumps(
                    {
                        "slug": "existing-flow",
                        "status": "PASS",
                        "claims": [
                            {
                                "id": "RC-001",
                                "classification": "observed",
                                "statement": "The current flow executes.",
                                "artifact": "specs/behavior.md",
                                "sources": [
                                    {
                                        "path": "src/flow.txt",
                                        "line_start": 1,
                                        "line_end": 1,
                                    }
                                ],
                                "confidence": "high",
                            }
                        ],
                        "gaps": [],
                        "artifact_fingerprints": {
                            "proposal.md": file_fingerprint(feature / "proposal.md"),
                            "spec.md": file_fingerprint(feature / "spec.md"),
                            "specs": document_fingerprints(feature)["specs"],
                            "design.md": file_fingerprint(feature / "design.md"),
                            "design": document_fingerprints(feature)["design"],
                            "_context/evidence-index.md": file_fingerprint(
                                feature / "_context" / "evidence-index.md"
                            ),
                            "_kapelle/surface-plan.json": file_fingerprint(
                                internal / "surface-plan.json"
                            ),
                        },
                        "source_fingerprints": {
                            "src/flow.txt": file_fingerprint(source)
                        },
                    }
                )
            )
            _, state, _ = refresh_feature_status(feature)
            self.assertTrue(state["review_ready"])
            self.assertFalse(state["ship_ready"])
            self.assertEqual(
                "/kapelle:reconstruct existing-flow --approve",
                state["next_command"],
            )

            self.write_approval(
                feature,
                "reconstruction",
                {
                    "_kapelle/reconstruction-coverage.json": file_fingerprint(
                        internal / "reconstruction-coverage.json"
                    )
                },
            )
            _, state, _ = refresh_feature_status(feature)
            self.assertEqual("documented", state["current_stage"])
            self.assertEqual("documented", state["feature_state"])
            self.assertFalse(state["ship_ready"])
            self.assertEqual("/kapelle:status existing-flow", state["next_command"])
            self.assertEqual([], validate(feature))

            source.write_text("changed behavior\n")
            _, state, _ = refresh_feature_status(feature)
            self.assertEqual("reconstruct-review", state["current_stage"])
            self.assertEqual(
                "/kapelle:reconstruct existing-flow --review",
                state["next_command"],
            )

    def test_reconstruction_marker_recovers_workflow_without_delivery(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_reconstruction(Path(tmp))
            (feature / "_kapelle" / "workflow.json").unlink()
            (feature / "_kapelle" / "reconstruction.json").unlink()
            _, state, _ = rebuild_feature_state(feature)
            workflow = json.loads(
                (feature / "_kapelle" / "workflow.json").read_text()
            )
            self.assertEqual("reconstruction", workflow["workflow"])
            self.assertTrue(
                (feature / "_kapelle" / "reconstruction.json").is_file()
            )
            self.assertEqual("reconstruct-scope", state["current_stage"])
            self.assertNotIn("plan", state["next_command"])
            self.assertNotIn("implement", state["next_command"])
            self.assertEqual([], validate(feature))

    def test_recovery_never_treats_checked_task_as_validated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_feature(Path(tmp), checked=True)
            _, state, report = rebuild_feature_state(feature)
            self.assertEqual("implemented-unverified", state["tasks"]["T01"])
            self.assertEqual(
                "implemented-unverified", report["task_dispositions"]["T01"]
            )
            self.assertFalse(state["ship_ready"])
            self.assertTrue(state["evidence_gaps"])
            self.assertEqual([], validate(feature))

    def test_new_feature_initialization_does_not_claim_recovery_loss(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_feature(Path(tmp))
            _, state = initialize_feature_state(feature)
            self.assertEqual("native", state["recovery_status"])
            self.assertEqual([], state["evidence_gaps"])
            self.assertFalse((feature / "_kapelle" / "recovery.json").exists())
            self.assertEqual([], validate(feature))

    def test_current_validation_evidence_completes_task(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_feature(Path(tmp), checked=True)
            rebuild_feature_state(feature)
            self.write_pass_validation(feature)
            _, state, recovered = refresh_feature_status(feature)
            self.assertFalse(recovered)
            self.assertEqual("completed", state["tasks"]["T01"])
            self.assertFalse(state["review_ready"])
            self.assertEqual("migrate", state["current_stage"])
            self.assertEqual([], validate(feature))

    def test_ad_hoc_validation_pass_is_not_completion_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_feature(Path(tmp), checked=True)
            rebuild_feature_state(feature)
            validation_dir = feature / "_kapelle" / "validation"
            validation_dir.mkdir()
            (validation_dir / "T01.json").write_text(
                json.dumps(
                    {
                        "task_id": "T01",
                        "status": "PASS",
                        "document_fingerprints": document_fingerprints(feature),
                    }
                )
            )
            _, state, _ = refresh_feature_status(feature)
            self.assertEqual("implemented-unverified", state["tasks"]["T01"])
            self.assertFalse(state["review_ready"])

    def test_validation_must_cover_task_file_hints(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            feature = self.make_feature(root, checked=True)
            rebuild_feature_state(feature)
            unrelated = root / "other.txt"
            unrelated.write_text("not task implementation\n")
            evidence_path = self.write_pass_validation(feature)
            evidence = json.loads(evidence_path.read_text())
            evidence["implementation_fingerprints"] = {
                "other.txt": file_fingerprint(unrelated)
            }
            evidence_path.write_text(json.dumps(evidence))
            _, state, _ = refresh_feature_status(feature)
            self.assertEqual("implemented-unverified", state["tasks"]["T01"])

    def test_directory_file_hint_requires_every_current_descendant(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            feature = self.make_feature(root, checked=True)
            task_plan_path = feature / "_kapelle" / "task-plan.json"
            task_plan = json.loads(task_plan_path.read_text())
            task_plan["tasks"][0]["files_hint"] = ["src"]
            task_plan_path.write_text(json.dumps(task_plan))
            (root / "src" / "second.txt").write_text("second changed file\n")
            rebuild_feature_state(feature)
            evidence_path = self.write_pass_validation(feature)
            _, incomplete_state, _ = refresh_feature_status(feature)
            self.assertEqual(
                "implemented-unverified", incomplete_state["tasks"]["T01"]
            )
            evidence = json.loads(evidence_path.read_text())
            evidence["implementation_fingerprints"]["src/second.txt"] = (
                file_fingerprint(root / "src" / "second.txt")
            )
            evidence_path.write_text(json.dumps(evidence))
            _, complete_state, _ = refresh_feature_status(feature)
            self.assertEqual("completed", complete_state["tasks"]["T01"])
            (root / "src" / "second.txt").write_text("drifted\n")
            _, drifted_state, _ = refresh_feature_status(feature)
            self.assertEqual(
                "implemented-unverified", drifted_state["tasks"]["T01"]
            )

    def test_directory_file_hint_symlink_escape_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside_tmp:
            root = Path(tmp)
            feature = self.make_feature(root, checked=True)
            outside = Path(outside_tmp)
            (outside / "outside.txt").write_text("outside\n")
            (root / "linked-src").symlink_to(outside, target_is_directory=True)
            task_plan_path = feature / "_kapelle" / "task-plan.json"
            task_plan = json.loads(task_plan_path.read_text())
            task_plan["tasks"][0]["files_hint"] = ["linked-src"]
            task_plan_path.write_text(json.dumps(task_plan))
            rebuild_feature_state(feature)
            self.write_pass_validation(feature)
            _, state, _ = refresh_feature_status(feature)
            self.assertEqual("implemented-unverified", state["tasks"]["T01"])
            self.assertFalse(state["ship_ready"])

    def test_legacy_review_evidence_never_bypasses_migration(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_feature(Path(tmp), checked=True)
            rebuild_feature_state(feature)
            validation_path = self.write_pass_validation(feature)
            fingerprints = input_fingerprints(feature)
            implementation = feature.parent.parent.parent / "src" / "feature.txt"
            reviews = feature / "_kapelle" / "reviews"
            reviews.mkdir()
            (reviews / "documentation-convergence.json").write_text(
                json.dumps(
                    {
                        "status": "PASS",
                        "revision": None,
                        "input_fingerprints": fingerprints,
                        "implementation_fingerprints": {
                            "src/feature.txt": file_fingerprint(implementation)
                        },
                        "requirement_mismatches": [],
                        "design_mismatches": [],
                        "contract_mismatches": [],
                        "undocumented_decisions": [],
                        "unresolved_deferrals": [],
                    }
                )
            )
            (reviews / "feature-review.json").write_text(
                json.dumps(
                    {
                        "status": "PASS",
                        "summary": "Historical review passed.",
                        "input_fingerprints": fingerprints,
                        "validation_files": [str(validation_path.relative_to(feature))],
                        "reviewed_aspects": ["core"],
                        "findings": [],
                    }
                )
            )
            _, state, _ = refresh_feature_status(feature)
            self.assertEqual("migrate", state["current_stage"])
            self.assertEqual(
                f"/kapelle:migrate {feature.name}", state["next_command"]
            )
            self.assertFalse(state["review_ready"])
            self.assertFalse(state["ship_ready"])

    def test_corrupt_coordination_routes_to_producing_stage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_feature(Path(tmp))
            initialize_feature_state(feature)
            (feature / "_kapelle" / "task-plan.json").write_text("{broken")
            _, state, _ = refresh_feature_status(feature)
            self.assertEqual("migrate", state["current_stage"])
            self.assertTrue(
                any("task-plan" in error for error in validate(feature))
            )
            (feature / "_kapelle" / "surface-plan.json").write_text("{broken")
            _, state, _ = refresh_feature_status(feature)
            self.assertEqual("migrate", state["current_stage"])

    def test_wrapped_task_metadata_and_ac_ranges_are_parsed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tasks = Path(tmp) / "tasks.md"
            tasks.write_text(
                "# Tasks\n\n## Delivery\n\n"
                "- [x] **T08 Implement behavior**\n"
                "  - covers AC-02–AC-06\n"
                "  - depends on T01, T02\n"
            )
            parsed = parse_tasks(tasks)
            self.assertEqual(
                ["AC-02", "AC-03", "AC-04", "AC-05", "AC-06"],
                parsed[0]["acs"],
            )
            self.assertEqual(["T01", "T02"], parsed[0]["declared_deps"])

    def test_task_execution_annotations_do_not_invalidate_slice_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tasks_path = Path(tmp) / "tasks.md"
            tasks_path.write_text(
                "# Tasks\n\n## Slice 1\n\n- [ ] **W1 Deliver base flow**\n"
            )
            planned = normalized_tasks_fingerprint(tasks_path)
            tasks_path.write_text(
                "# Tasks\n\n## Slice 1\n\n"
                "- [x] **W1 Deliver base flow**\n"
                "  Result: The base flow works end to end.\n"
                "  Deferred validation: Full static analysis waits for verify.\n"
            )
            self.assertEqual(planned, normalized_tasks_fingerprint(tasks_path))
            tasks_path.write_text(
                tasks_path.read_text()
                + "\n## Slice 2\n\n- [ ] **W2 Add requested business rule**\n"
            )
            self.assertNotEqual(planned, normalized_tasks_fingerprint(tasks_path))

    def test_symlink_escape_is_refused_before_runtime_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            feature = self.make_feature(root)
            outside = root / "outside"
            outside.mkdir()
            (feature / "_kapelle" / "escape").symlink_to(outside, target_is_directory=True)
            with self.assertRaises(FeatureStateError):
                refresh_feature_status(feature)
            self.assertEqual([], list(outside.iterdir()))

    def test_status_drift_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_feature(Path(tmp))
            rebuild_feature_state(feature)
            (feature / "STATUS.md").write_text("manual edit\n")
            self.assertTrue(
                any("STATUS.md drift" in error for error in validate(feature))
            )

    def test_deleted_internal_state_rebuilds_conservative_graphs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_feature(Path(tmp), checked=True)
            for path in sorted(
                (feature / "_kapelle").rglob("*"), reverse=True
            ):
                if path.is_file():
                    path.unlink()
                else:
                    path.rmdir()
            (feature / "_kapelle").rmdir()
            _, state, report = rebuild_feature_state(feature)
            self.assertTrue((feature / "_kapelle" / "surface-plan.json").is_file())
            self.assertTrue((feature / "_kapelle" / "task-plan.json").is_file())
            self.assertEqual("implemented-unverified", state["tasks"]["T01"])
            self.assertEqual("/kapelle:migrate readable-feature", report["next_command"])
            self.assertIn(
                "current scoped architecture guidance",
                report["evidence_unavailable"],
            )
            self.assertEqual(
                [],
                validate_task_plan(
                    feature / "_kapelle" / "task-plan.json",
                    feature / "_kapelle" / "surface-plan.json",
                    feature / "spec.md",
                ),
            )
            self.assertEqual([], validate(feature))

    def test_recovered_pending_work_requires_decomposition_before_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_feature(Path(tmp), checked=False)
            for path in sorted((feature / "_kapelle").rglob("*"), reverse=True):
                if path.is_file():
                    path.unlink()
                else:
                    path.rmdir()
            (feature / "_kapelle").rmdir()
            _, state, _ = rebuild_feature_state(feature)
            self.assertEqual("pending", state["tasks"]["T01"])
            self.assertEqual("migrate", state["current_stage"])
            self.assertEqual(
                "/kapelle:migrate readable-feature", state["next_command"]
            )

    def test_missing_downstream_human_artifacts_selects_minimal_stage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_feature(Path(tmp))
            (feature / "design.md").unlink()
            (feature / "tasks.md").unlink()
            (feature / "test-plan.md").unlink()
            _, state, _ = rebuild_feature_state(feature)
            self.assertEqual("migrate", state["current_stage"])
            self.assertEqual(
                "/kapelle:migrate readable-feature", state["next_command"]
            )
            self.assertEqual([], validate(feature))

    def test_runtime_machine_artifacts_are_schema_validated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_feature(Path(tmp))
            initialize_feature_state(feature)
            internal = feature / "_kapelle"
            task_runs = internal / "task-runs"
            task_runs.mkdir()
            (task_runs / "T01.json").write_text(
                json.dumps({"plan": {"task_id": "T01"}})
            )
            telemetry = internal / "telemetry"
            telemetry.mkdir()
            (telemetry / "execution.jsonl").write_text(
                json.dumps(
                    {
                        "run_id": "run-1",
                        "slug": feature.name,
                        "task_id": "T01",
                        "event": "not-an-event",
                        "status": "invalid",
                        "agent_runs": 1,
                        "edit_attempts": 1,
                    }
                )
                + "\n"
            )
            change = internal / "changes" / "change-1"
            change.mkdir(parents=True)
            (change / "request.json").write_text(json.dumps({"change_id": "change-1"}))

            errors = validate(feature)
            self.assertTrue(any("T01.json#plan schema" in item for item in errors))
            self.assertTrue(any("execution.jsonl schema" in item for item in errors))
            self.assertTrue(any("request.json schema" in item for item in errors))

    def test_legacy_human_controlled_workflow_requires_migration(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            feature = self.make_feature(root)
            internal = feature / "_kapelle"
            (internal / "workflow.json").write_text(
                json.dumps(
                    {
                        "workflow": "human-controlled",
                        "version": 1,
                        "created_from": "raw-task",
                        "lane": "standard",
                    }
                )
            )
            (feature / "proposal.md").write_text(
                "<!-- kapelle-workflow: human-controlled-v1; lane: standard -->\n"
                + (feature / "proposal.md").read_text()
            )
            (feature / "specs").mkdir()
            (feature / "specs" / "scenarios.md").write_text("# Scenarios\n")
            docs = document_fingerprints(feature)
            self.write_approval(
                feature,
                "outline",
                {
                    "proposal.md": docs["proposal.md"],
                    "_context/architecture.md": file_fingerprint(
                        feature / "_context" / "architecture.md"
                    ),
                },
            )
            self.write_approval(
                feature,
                "business-spec",
                {
                    "proposal.md": docs["proposal.md"],
                    "spec.md": docs["spec.md"],
                    "specs": docs["specs"],
                },
            )
            (feature / "design").mkdir()
            (feature / "design" / "components.md").write_text("# Components\n")
            (feature / "contracts").mkdir()
            (feature / "contracts" / "README.md").write_text("# Contracts\n\nNone.\n")
            guidance = internal / "architecture-guidance"
            guidance.mkdir()
            (guidance / "design.json").write_text(
                json.dumps(self.valid_guidance(["core"]))
            )
            docs = document_fingerprints(feature)
            self.write_approval(
                feature,
                "architecture",
                {
                    "spec.md": docs["spec.md"],
                    "specs": docs["specs"],
                    "design.md": docs["design.md"],
                    "design": docs["design"],
                    "contracts": docs["contracts"],
                    "_kapelle/surface-plan.json": file_fingerprint(
                        internal / "surface-plan.json"
                    ),
                    "_kapelle/architecture-guidance/design.json": file_fingerprint(
                        guidance / "design.json"
                    ),
                },
            )
            self.write_approval(
                feature,
                "delivery-plan",
                {
                    "tasks.md#structural": normalized_tasks_fingerprint(
                        feature / "tasks.md"
                    ),
                    "test-plan.md": file_fingerprint(feature / "test-plan.md"),
                    "_kapelle/task-plan.json#structural": (
                        normalized_task_plan_fingerprint(
                            internal / "task-plan.json"
                        )
                    ),
                },
            )
            _, state = initialize_feature_state(feature)
            self.assertEqual("migrate", state["current_stage"])
            self.assertEqual(
                f"/kapelle:migrate {feature.name}",
                state["next_command"],
            )
            return

            phase_inputs = {
                "spec.md": file_fingerprint(feature / "spec.md"),
                "specs": document_fingerprints(feature)["specs"],
                "contracts": document_fingerprints(feature)["contracts"],
                "test-plan.md": file_fingerprint(feature / "test-plan.md"),
                "tasks.md#structural": normalized_tasks_fingerprint(
                    feature / "tasks.md"
                ),
                "_kapelle/task-plan.json#structural": (
                    normalized_task_plan_fingerprint(internal / "task-plan.json")
                ),
            }
            (internal / "base-functional-tests.json").write_text(
                json.dumps(
                    {
                        "status": "READY",
                        "scope": ["endpoint"],
                        "test_files": ["tests/functional.txt"],
                        "covered_contracts": [],
                        "input_fingerprints": phase_inputs,
                    }
                )
            )
            _, state, _ = refresh_feature_status(feature)
            self.assertEqual("implement", state["current_stage"])

            (feature / "tasks.md").write_text(
                (feature / "tasks.md").read_text().replace("- [ ]", "- [x]")
            )
            task_plan = json.loads((internal / "task-plan.json").read_text())
            task_plan["tasks"][0]["status"] = "implemented-unverified"
            (internal / "task-plan.json").write_text(json.dumps(task_plan))
            _, state, _ = refresh_feature_status(feature)
            self.assertEqual("unit-tests", state["current_stage"])

            implementation_fingerprints = {
                "src/feature.txt": file_fingerprint(root / "src" / "feature.txt")
            }
            post_implementation_inputs = {
                "spec.md": file_fingerprint(feature / "spec.md"),
                "tasks.md#structural": normalized_tasks_fingerprint(
                    feature / "tasks.md"
                ),
                "_kapelle/task-plan.json#structural": (
                    normalized_task_plan_fingerprint(internal / "task-plan.json")
                ),
            }
            (internal / "unit-tests.json").write_text(
                json.dumps(
                    {
                        "status": "PASS",
                        "planned_units": ["feature unit"],
                        "test_files": ["tests/unit.txt"],
                        "commands": ["unit-test"],
                        "input_fingerprints": post_implementation_inputs,
                        "implementation_fingerprints": implementation_fingerprints,
                    }
                )
            )
            _, state, _ = refresh_feature_status(feature)
            self.assertEqual("verify", state["current_stage"])

            (internal / "verification.json").write_text(
                json.dumps({"status": "PASS"})
            )
            _, state, _ = refresh_feature_status(feature)
            self.assertEqual("verify", state["current_stage"])

            (internal / "verification.json").write_text(
                json.dumps(
                    {
                        "status": "PASS",
                        "categories": ["functional", "unit", "lint"],
                        "commands": ["test-all", "lint"],
                        "input_fingerprints": post_implementation_inputs,
                        "implementation_fingerprints": implementation_fingerprints,
                    }
                )
            )
            self.write_pass_validation(feature)
            _, state, _ = refresh_feature_status(feature)
            self.assertEqual("finalize", state["current_stage"])
            self.assertTrue(state["review_ready"])

            (feature / "diagrams").mkdir()
            diagrams = [
                "diagrams/feature-flow.mmd",
                "diagrams/architecture.mmd",
            ]
            for relative in diagrams:
                (feature / relative).write_text("flowchart LR\n  A --> B\n")
            self.write_approval(
                feature,
                "final",
                {
                    "diagrams": document_fingerprints(feature)["diagrams"],
                    "_kapelle/verification.json": file_fingerprint(
                        internal / "verification.json"
                    ),
                },
            )
            release_docs = {
                name: digest
                for name, digest in document_fingerprints(feature).items()
                if digest is not None
            }
            (internal / "release.json").write_text(
                json.dumps(
                    {
                        "status": "completed",
                        "version": "1.0",
                        "developer_confirmation": "Manual testing complete",
                        "document_fingerprints": release_docs,
                        "implementation_fingerprints": implementation_fingerprints,
                        "diagrams": diagrams,
                    }
                )
            )
            _, state, _ = refresh_feature_status(feature)
            self.assertEqual("completed", state["current_stage"])
            self.assertEqual("completed", state["feature_state"])
            self.assertTrue(state["ship_ready"])
            self.assertEqual([], validate(feature))

            for path in sorted(internal.rglob("*"), reverse=True):
                if path.is_file():
                    path.unlink()
                else:
                    path.rmdir()
            internal.rmdir()
            _, recovered_state, _ = rebuild_feature_state(feature)
            self.assertTrue((internal / "workflow.json").is_file())
            self.assertEqual("spec", recovered_state["current_stage"])
            self.assertEqual(
                f"/kapelle:spec {feature.name}",
                recovered_state["next_command"],
            )
            self.assertEqual([], validate(feature))

    def test_legacy_fast_lane_requires_migration(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_feature(Path(tmp))
            internal = feature / "_kapelle"
            (feature / "test-plan.md").unlink()
            (internal / "workflow.json").write_text(
                json.dumps(
                    {
                        "workflow": "human-controlled",
                        "version": 1,
                        "created_from": "raw-task",
                        "lane": "fast",
                    }
                )
            )
            (feature / "proposal.md").write_text(
                "<!-- kapelle-workflow: human-controlled-v1; lane: fast -->\n"
                + (feature / "proposal.md").read_text()
            )
            self.write_approval(
                feature,
                "feature-plan",
                {
                    "proposal.md": file_fingerprint(feature / "proposal.md"),
                    "spec.md": file_fingerprint(feature / "spec.md"),
                    "design.md": file_fingerprint(feature / "design.md"),
                    "tasks.md#structural": normalized_tasks_fingerprint(
                        feature / "tasks.md"
                    ),
                    "_kapelle/surface-plan.json": file_fingerprint(
                        internal / "surface-plan.json"
                    ),
                    "_kapelle/task-plan.json#structural": (
                        normalized_task_plan_fingerprint(internal / "task-plan.json")
                    ),
                },
            )
            _, state = initialize_feature_state(feature)
            self.assertEqual("migrate", state["current_stage"])
            self.assertEqual(
                f"/kapelle:migrate {feature.name}",
                state["next_command"],
            )
            self.assertEqual([], validate(feature))

    def test_legacy_fast_lane_size_no_longer_routes_old_stages(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_feature(Path(tmp))
            internal = feature / "_kapelle"
            (internal / "workflow.json").write_text(
                json.dumps(
                    {
                        "workflow": "human-controlled",
                        "version": 1,
                        "created_from": "raw-task",
                        "lane": "fast",
                    }
                )
            )
            (feature / "proposal.md").write_text(
                "<!-- kapelle-workflow: human-controlled-v1; lane: fast -->\n"
                + (feature / "proposal.md").read_text()
            )
            task_plan = json.loads((internal / "task-plan.json").read_text())
            base = task_plan["tasks"][0]
            task_plan["workstreams"][0]["completion_task_id"] = "T04"
            task_plan["tasks"] = []
            human_tasks = ["# Tasks", "", "## Delivery", ""]
            for index in range(1, 5):
                task = json.loads(json.dumps(base))
                task["id"] = f"T0{index}"
                task["title"] = f"Task {index}"
                task["intent"] = f"Task {index}"
                task["deps"] = [] if index == 1 else [f"T0{index - 1}"]
                task["acs"] = ["AC-01"] if index == 1 else []
                task["files_hint"] = [f"src/feature-{index}.txt"]
                task_plan["tasks"].append(task)
                human_tasks.append(f"- [ ] **T0{index} Task {index}**")
            (internal / "task-plan.json").write_text(json.dumps(task_plan))
            (feature / "tasks.md").write_text("\n".join(human_tasks) + "\n")
            _, state = initialize_feature_state(feature)
            self.assertEqual("migrate", state["current_stage"])
            self.assertEqual(
                f"/kapelle:migrate {feature.name}",
                state["next_command"],
            )

    def test_lightweight_workflow_routes_start_implement_verify_complete(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            feature = self.make_feature(root)
            internal = feature / "_kapelle"
            (feature / "spec.md").write_text(
                f"{WORKFLOW_MARKER}\n{ARTIFACT_MARKER}\n"
                + self.progressive_document("# Feature specification", SPEC_HEADINGS)
            )
            (feature / "design.md").write_text(
                self.progressive_document(
                    "# System design", PROGRESSIVE_DESIGN_HEADINGS
                )
            )
            (internal / "workflow.json").write_text(
                json.dumps(
                    {
                        "workflow": "human-controlled",
                        "version": 2,
                        "created_from": "raw-task",
                        "profile": "lightweight",
                    }
                )
            )
            guidance = internal / "architecture-guidance"
            guidance.mkdir()
            (guidance / "design.json").write_text(
                json.dumps(self.valid_guidance(["core"]))
            )
            self.write_approval(
                feature,
                "plan",
                {
                    "spec.md": file_fingerprint(feature / "spec.md"),
                    "design.md": file_fingerprint(feature / "design.md"),
                    "tasks.md#structural": normalized_tasks_fingerprint(
                        feature / "tasks.md"
                    ),
                    "_kapelle/architecture-guidance/design.json": file_fingerprint(
                        guidance / "design.json"
                    ),
                },
            )
            _, state = initialize_feature_state(feature)
            self.assertEqual("implement", state["current_stage"])

            (feature / "tasks.md").write_text(
                (feature / "tasks.md").read_text().replace("- [ ]", "- [x]")
            )
            _, state, _ = refresh_feature_status(feature)
            self.assertEqual("verify", state["current_stage"])
            status_text = (feature / "STATUS.md").read_text()
            self.assertIn("## Scope decision", status_text)
            self.assertIn(
                f'/kapelle:amend {feature.name} "<next requirement>"',
                status_text,
            )

            implementation = root / "src" / "feature.txt"
            (internal / "verification.json").write_text(
                json.dumps(
                    {
                        "status": "PASS",
                        "categories": ["functional", "unit"],
                        "commands": ["project-test"],
                        "input_fingerprints": {
                            "spec.md": file_fingerprint(feature / "spec.md"),
                            "design.md": file_fingerprint(feature / "design.md"),
                            "tasks.md#structural": normalized_tasks_fingerprint(
                                feature / "tasks.md"
                            ),
                        },
                        "implementation_fingerprints": {
                            "src/feature.txt": file_fingerprint(implementation)
                        },
                    }
                )
            )
            _, state, _ = refresh_feature_status(feature)
            self.assertEqual("verify", state["current_stage"])
            self.assertEqual(
                f"/kapelle:verify {feature.name} --approve",
                state["next_command"],
            )
            self.assertEqual("completed", state["tasks"]["T01"])

            self.write_approval(
                feature,
                "final",
                {
                    "spec.md": file_fingerprint(feature / "spec.md"),
                    "design.md": file_fingerprint(feature / "design.md"),
                    "tasks.md#structural": normalized_tasks_fingerprint(
                        feature / "tasks.md"
                    ),
                    "_kapelle/verification.json": file_fingerprint(
                        internal / "verification.json"
                    ),
                },
            )
            _, state, _ = refresh_feature_status(feature)
            self.assertEqual("completed", state["current_stage"])
            self.assertTrue(state["ship_ready"])
            self.assertEqual([], validate(feature))

    def test_developer_attested_pass_supersedes_deferred_lightweight_validation(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            feature = self.make_feature(root, checked=True)
            internal = feature / "_kapelle"
            (feature / "spec.md").write_text(
                f"{WORKFLOW_MARKER}\n{ARTIFACT_MARKER}\n"
                + self.progressive_document("# Feature specification", SPEC_HEADINGS)
            )
            (feature / "design.md").write_text(
                self.progressive_document(
                    "# System design", PROGRESSIVE_DESIGN_HEADINGS
                )
            )
            guidance = internal / "architecture-guidance"
            guidance.mkdir()
            (guidance / "design.json").write_text(
                json.dumps(self.valid_guidance(["core"]))
            )
            self.write_deferred_validation(feature)
            _, deferred_state, _ = refresh_feature_status(feature)
            self.assertEqual(
                "validation-deferred", deferred_state["tasks"]["T01"]
            )

            implementation = root / "src" / "feature.txt"
            (internal / "verification.json").write_text(
                json.dumps(
                    {
                        "status": "PASS",
                        "evidence_source": "developer-attested",
                        "developer_confirmation": (
                            "I manually tested and verified the complete planned batch; "
                            "all checks pass."
                        ),
                        "categories": ["functional", "unit", "lint"],
                        "commands": [
                            "Developer completed the complete planned verification batch"
                        ],
                        "input_fingerprints": input_fingerprints(feature),
                        "implementation_fingerprints": {
                            "src/feature.txt": file_fingerprint(implementation)
                        },
                    }
                )
            )
            self.assertTrue(
                phase_evidence_current(feature, "verification.json", {"PASS"})
            )
            _, verified_state, _ = refresh_feature_status(feature)
            self.assertEqual("completed", verified_state["tasks"]["T01"])
            self.assertEqual(
                f"/kapelle:verify {feature.name} --approve",
                verified_state["next_command"],
            )
            self.assertIn(
                "developer-confirmed; command output not captured by Kapelle",
                (feature / "STATUS.md").read_text(),
            )

    def test_lightweight_recovery_needs_no_machine_coordination_graph(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_feature(Path(tmp))
            (feature / "spec.md").write_text(
                "<!-- kapelle-workflow: lightweight-v1 -->\n"
                + (feature / "spec.md").read_text()
            )
            internal = feature / "_kapelle"
            for path in sorted(internal.rglob("*"), reverse=True):
                if path.is_file():
                    path.unlink()
                else:
                    path.rmdir()
            internal.rmdir()

            _, state, _ = rebuild_feature_state(feature)
            workflow = json.loads((internal / "workflow.json").read_text())
            self.assertEqual(2, workflow["version"])
            self.assertFalse((internal / "surface-plan.json").exists())
            self.assertFalse((internal / "task-plan.json").exists())
            self.assertEqual("start", state["current_stage"])
            self.assertEqual([], validate(feature))

    def test_legacy_migration_is_planned_applied_and_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = Path(tmp) / "legacy-feature"
            feature.mkdir()
            (feature / "spec.md").write_text("# Legacy spec\n\n**AC-01** Preserve behavior.\n")
            (feature / "sad.md").write_text("# Legacy design\n")
            (feature / "test-plan.md").write_text("# Tests\n")
            (feature / "surface-plan.json").write_text(
                json.dumps(
                    {
                        "slug": "legacy-feature",
                        "aspects": [
                            {
                                "id": "core",
                                "intent": "Preserve behavior",
                                "modules": [],
                                "entrypoints": [],
                                "depends_on": [],
                            }
                        ],
                        "contracts": [],
                        "integration_checks": [],
                    }
                )
            )
            (feature / "tasks.json").write_text(
                json.dumps(
                    {
                        "slug": "legacy-feature",
                        "decomposition_depth": "standard",
                        "architecture_guidance_path": "_context/architecture.md",
                        "workstreams": [
                            {
                                "id": "WS",
                                "title": "Legacy delivery",
                                "intent": "Preserve legacy behavior",
                                "aspects": ["core"],
                                "depends_on": [],
                                "completion_task_id": "T1",
                                "completion_signal": "Behavior is preserved",
                            }
                        ],
                        "tasks": [
                            {
                                "id": "T1",
                                "title": "Preserve task",
                                "intent": "Preserve task",
                                "workstream_id": "WS",
                                "deps": [],
                                "status": "completed",
                                "acs": ["AC-01"],
                                "dod": "Behavior is preserved",
                                "module_hint": None,
                                "primary_aspect": "core",
                                "aspects": ["core"],
                                "entrypoint_hint": None,
                                "provides_contracts": [],
                                "consumes_contracts": [],
                                "integration_checks": [],
                                "validation": [
                                    {
                                        "kind": "inspection",
                                        "procedure": "Inspect preserved behavior",
                                        "expected": "Behavior is unchanged",
                                    }
                                ],
                                "risk": "low",
                                "parallel_candidate": False,
                                "ownership_status": "known",
                                "files_hint": [],
                            }
                        ],
                        "split_recommendations": [],
                    }
                )
            )
            audit = feature / "_audit"
            audit.mkdir()
            (audit / "evidence.txt").write_text("historical")
            (feature / ".size").write_text("Size: M\nExecution depth: standard\n")
            change = feature / "changes" / "active-change"
            change.mkdir(parents=True)
            (change / "active-state.json").write_text(
                json.dumps({"state": "running", "revision": "r001"})
            )

            dry_run = migration_plan(feature)
            self.assertEqual("ready", dry_run["status"])
            self.assertTrue((feature / "sad.md").exists())
            apply_migration(feature, dry_run)
            self.assertTrue((feature / "design.md").exists())
            self.assertTrue((feature / "proposal.md").exists())
            self.assertTrue((feature / "tasks.md").exists())
            self.assertTrue((feature / "_kapelle" / "task-plan.json").exists())
            self.assertTrue(
                (feature / "_kapelle" / "history" / "legacy" / "audit" / "evidence.txt").exists()
            )
            self.assertEqual(
                "M",
                json.loads((feature / "_kapelle" / "size.json").read_text())["size"],
            )
            self.assertTrue(
                (feature / "_kapelle" / "changes" / "active-change" / "state.json").exists()
            )
            migrated_state = json.loads(
                (
                    feature
                    / "_kapelle"
                    / "changes"
                    / "active-change"
                    / "state.json"
                ).read_text()
            )
            self.assertEqual("active-change", migrated_state["change_id"])
            self.assertEqual(1, migrated_state["current_revision"])
            self.assertIsNone(migrated_state["paused_task"])
            self.assertEqual("already-migrated", migration_plan(feature)["status"])

    def test_migration_refuses_malformed_or_duplicate_tasks_before_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = Path(tmp) / "legacy"
            feature.mkdir()
            (feature / "spec.md").write_text("# Spec\n\n**AC-01** Behavior.\n")
            (feature / "surface-plan.json").write_text(
                json.dumps(
                    {
                        "slug": "legacy",
                        "aspects": [],
                        "contracts": [],
                        "integration_checks": [],
                    }
                )
            )
            (feature / "tasks.json").write_text("{broken")
            with self.assertRaises(FeatureStateError):
                migration_plan(feature)
            self.assertFalse((feature / "_kapelle").exists())

            (feature / "tasks.json").write_text(
                json.dumps(
                    {
                        "slug": "legacy",
                        "workstreams": [],
                        "tasks": [{"id": "T1"}, {"id": "T1"}],
                    }
                )
            )
            with self.assertRaises(FeatureStateError):
                apply_migration(feature, {"status": "ready", "collisions": []})
            self.assertTrue((feature / "tasks.json").exists())
            self.assertFalse(
                (feature / "_kapelle" / "history" / "migration-v2.json").exists()
            )

    def test_malformed_or_inconsistent_migration_marker_never_suppresses_work(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = Path(tmp) / "legacy"
            marker = feature / "_kapelle" / "history" / "migration-v2.json"
            marker.parent.mkdir(parents=True)
            marker.write_text("{broken")
            (feature / "sad.md").write_text("# Legacy design\n")
            with self.assertRaises(FeatureStateError):
                migration_plan(feature)
            self.assertTrue((feature / "sad.md").exists())

            marker.write_text(
                json.dumps(
                    {
                        "layout_version": 2,
                        "status": "migrated",
                        "actions": [],
                        "warnings": [],
                    }
                )
            )
            with self.assertRaises(FeatureStateError):
                migration_plan(feature)

    def test_migration_preflight_rejects_malformed_canonical_change_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = Path(tmp) / "legacy"
            state_path = feature / "changes" / "change-a" / "state.json"
            state_path.parent.mkdir(parents=True)
            state_path.write_text("{broken")
            with self.assertRaises(FeatureStateError):
                migration_plan(feature)
            self.assertTrue(state_path.exists())
            self.assertFalse((feature / "_kapelle").exists())

    def test_indented_checkboxes_stay_inside_their_workstream_block(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tasks = Path(tmp) / "tasks.md"
            tasks.write_text(
                "# Implementation tasks\n\n"
                "- [ ] **W1 Deliver the outcome** — covers AC-01\n"
                "  - [ ] Nested implementation note.\n"
                "  - Changes: affected behavior.\n"
                "  - Done when: observable result exists.\n"
                "  - Verify: focused behavior check passes.\n"
            )
            parsed = parse_tasks(tasks)
            self.assertEqual(["W1"], [task["id"] for task in parsed])
            self.assertEqual(["AC-01"], parsed[0]["acs"])


if __name__ == "__main__":
    unittest.main()
