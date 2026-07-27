#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from feature_state import FeatureStateError
from migrate_workflow import apply, plan


class WorkflowMigrationTests(unittest.TestCase):
    def make_feature(self, root: Path) -> Path:
        feature = root / "docs" / "features" / "legacy"
        feature.mkdir(parents=True)
        (feature / "proposal.md").write_text("# Proposal\n\nExisting goal.\n")
        (feature / "spec.md").write_text("# Spec\n\n**AC-01** Existing behavior.\n")
        return feature

    def test_dry_run_does_not_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_feature(Path(tmp))
            result = plan(feature, "standard")
            self.assertEqual("lightweight", result["profile"])
            self.assertFalse((feature / "_kapelle").exists())
            self.assertNotIn("kapelle-workflow", (feature / "spec.md").read_text())
            self.assertEqual([], result["missing_migration_prerequisites"])

    def test_apply_adds_marker_and_routes_without_fabricated_approval(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_feature(Path(tmp))
            result = apply(feature, "standard")
            workflow = json.loads(
                (feature / "_kapelle" / "workflow.json").read_text()
            )
            self.assertEqual("legacy-migration", workflow["created_from"])
            self.assertEqual(2, workflow["version"])
            self.assertEqual("lightweight", workflow["profile"])
            self.assertIn("lightweight-v1", (feature / "spec.md").read_text())
            self.assertEqual(
                f'/kapelle:start {feature.name} "<raw task>"',
                result["next_command"],
            )
            self.assertFalse((feature / "_kapelle" / "approvals").exists())

    def test_apply_normalizes_and_archives_legacy_guidance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_feature(Path(tmp))
            (feature / "design.md").write_text("# Design\n")
            (feature / "tasks.md").write_text("# Tasks\n\n- [x] Existing work\n")
            guidance_path = feature / "_kapelle" / "architecture-guidance" / "design.json"
            guidance_path.parent.mkdir(parents=True)
            legacy = {
                "status": "ARCHITECTURE_GUIDANCE_READY",
                "capability": {
                    "name": "project-rules",
                    "kind": "project-subagent",
                    "description_evidence": "Legacy evidence",
                },
                "scope": {
                    "aspects": ["runtime"],
                    "modules": ["app"],
                    "entrypoints": ["endpoint"],
                    "paths": ["src"],
                },
                "rules": [
                    {
                        "id": "ARCH-01",
                        "summary": "Keep the boundary explicit.",
                        "source": "AGENTS.md",
                        "applies_to": ["runtime"],
                    }
                ],
                "gaps": [],
                "precedents": [
                    {"path": "src/example.py", "reason": "Existing precedent"}
                ],
            }
            guidance_path.write_text(json.dumps(legacy))

            result = apply(feature)

            normalized = json.loads(guidance_path.read_text())
            archived = json.loads(
                (
                    feature
                    / "_kapelle"
                    / "history"
                    / "legacy"
                    / "architecture-guidance"
                    / "design.json"
                ).read_text()
            )
            self.assertEqual("ARCH-01", normalized["rules"][0]["title"])
            self.assertEqual(["AGENTS.md", "src/example.py"], normalized["sources"])
            self.assertEqual(legacy, archived)
            self.assertEqual(
                f"/kapelle:start {feature.name} --approve",
                result["next_command"],
            )

    def test_apply_refuses_unconvertible_guidance_before_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_feature(Path(tmp))
            guidance_path = feature / "_kapelle" / "architecture-guidance" / "design.json"
            guidance_path.parent.mkdir(parents=True)
            guidance_path.write_text('{"status":"ARCHITECTURE_GUIDANCE_READY"}')

            with self.assertRaisesRegex(
                FeatureStateError, "architecture guidance cannot be migrated safely"
            ):
                apply(feature)

            self.assertNotIn("lightweight-v1", (feature / "spec.md").read_text())
            self.assertFalse((feature / "_kapelle" / "workflow.json").exists())


if __name__ == "__main__":
    unittest.main()
