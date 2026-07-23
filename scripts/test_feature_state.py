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
    parse_tasks,
    rebuild_feature_state,
    refresh_feature_status,
)
from migrate_feature_layout import apply_migration, migration_plan
from validate_feature_state import validate
from validate_task_plan import validate as validate_task_plan


class FeatureStateTests(unittest.TestCase):
    def make_feature(self, root: Path, *, checked: bool = False) -> Path:
        feature = root / "docs" / "features" / "readable-feature"
        feature.mkdir(parents=True)
        (feature / "proposal.md").write_text(
            "# Readable feature\n\n## Summary\n\nMake feature state readable.\n"
        )
        (feature / "spec.md").write_text(
            "# Specification\n\n- **AC-01** Status is visible.\n"
        )
        (feature / "design.md").write_text("# Design\n\nNo data schema change.\n")
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
            self.assertTrue(state["review_ready"])
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

    def test_ship_requires_strict_fresh_review_and_implementation_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_feature(Path(tmp), checked=True)
            rebuild_feature_state(feature)
            validation_path = self.write_pass_validation(feature)
            refresh_feature_status(feature)
            fingerprints = input_fingerprints(feature)
            implementation = feature.parent.parent.parent / "src" / "feature.txt"
            implementation_fingerprints = {
                "src/feature.txt": file_fingerprint(implementation)
            }
            reviews = feature / "_kapelle" / "reviews"
            reviews.mkdir()
            (reviews / "documentation-convergence.json").write_text(
                json.dumps(
                    {
                        "status": "PASS",
                        "revision": None,
                        "input_fingerprints": fingerprints,
                        "implementation_fingerprints": implementation_fingerprints,
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
                        "summary": "Independent review passed.",
                        "input_fingerprints": fingerprints,
                        "validation_files": [
                            str(validation_path.relative_to(feature))
                        ],
                        "reviewed_aspects": ["core"],
                        "findings": [],
                    }
                )
            )
            _, state, _ = refresh_feature_status(feature)
            self.assertTrue(state["ship_ready"])
            convergence_path = reviews / "documentation-convergence.json"
            original_convergence = convergence_path.read_text()
            convergence = json.loads(original_convergence)
            extra = feature.parent.parent.parent / "src" / "extra.txt"
            extra.write_text("not in task validation inventory\n")
            convergence["implementation_fingerprints"]["src/extra.txt"] = (
                file_fingerprint(extra)
            )
            convergence_path.write_text(json.dumps(convergence))
            _, mismatched_inventory_state, _ = refresh_feature_status(feature)
            self.assertFalse(mismatched_inventory_state["ship_ready"])
            convergence_path.write_text(original_convergence)
            _, restored_inventory_state, _ = refresh_feature_status(feature)
            self.assertTrue(restored_inventory_state["ship_ready"])
            invalid_change = (
                feature / "_kapelle" / "changes" / "corrupt" / "state.json"
            )
            invalid_change.parent.mkdir(parents=True)
            invalid_change.write_text("{broken")
            _, invalid_change_state, _ = refresh_feature_status(feature)
            self.assertFalse(invalid_change_state["ship_ready"])
            self.assertTrue(
                any("invalid change state" in error for error in validate(feature))
            )
            invalid_change.unlink()
            invalid_change.parent.rmdir()
            _, restored_change_state, _ = refresh_feature_status(feature)
            self.assertTrue(restored_change_state["ship_ready"])
            surface_path = feature / "_kapelle" / "surface-plan.json"
            original_surface = surface_path.read_text()
            surface = json.loads(original_surface)
            surface["aspects"].append(
                {
                    "id": "secondary",
                    "intent": "Secondary behavior",
                    "modules": [],
                    "entrypoints": [],
                    "depends_on": [],
                }
            )
            surface_path.write_text(json.dumps(surface))
            _, partial_review_state, _ = refresh_feature_status(feature)
            self.assertFalse(partial_review_state["ship_ready"])
            surface_path.write_text(original_surface)
            _, restored_state, _ = refresh_feature_status(feature)
            self.assertTrue(restored_state["ship_ready"])
            implementation.write_text("changed after review\n")
            _, stale_state, _ = refresh_feature_status(feature)
            self.assertFalse(stale_state["ship_ready"])
            self.assertEqual("missing-or-stale", stale_state["documentation_convergence"])

    def test_corrupt_coordination_routes_to_producing_stage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_feature(Path(tmp))
            initialize_feature_state(feature)
            (feature / "_kapelle" / "task-plan.json").write_text("{broken")
            _, state, _ = refresh_feature_status(feature)
            self.assertEqual("decompose", state["current_stage"])
            self.assertTrue(
                any("task-plan" in error for error in validate(feature))
            )
            (feature / "_kapelle" / "surface-plan.json").write_text("{broken")
            _, state, _ = refresh_feature_status(feature)
            self.assertEqual("design", state["current_stage"])

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
            self.assertEqual(
                "/kapelle:implement readable-feature --validation=ask",
                report["next_command"],
            )
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
            self.assertEqual("decompose", state["current_stage"])
            self.assertEqual(
                "/kapelle:decompose readable-feature", state["next_command"]
            )

    def test_missing_downstream_human_artifacts_selects_minimal_stage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_feature(Path(tmp))
            (feature / "design.md").unlink()
            (feature / "tasks.md").unlink()
            (feature / "test-plan.md").unlink()
            _, state, _ = rebuild_feature_state(feature)
            self.assertEqual("design", state["current_stage"])
            self.assertEqual(
                "/kapelle:design readable-feature", state["next_command"]
            )
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


if __name__ == "__main__":
    unittest.main()
