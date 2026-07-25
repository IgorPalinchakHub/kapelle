#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

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
            self.assertEqual("standard", result["lane"])
            self.assertFalse((feature / "_kapelle").exists())
            self.assertNotIn("kapelle-workflow", (feature / "proposal.md").read_text())
            self.assertEqual(
                ["_context/architecture.md"],
                result["missing_migration_prerequisites"],
            )

    def test_apply_adds_marker_and_routes_without_fabricated_approval(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_feature(Path(tmp))
            (feature / "_context").mkdir()
            (feature / "_context" / "architecture.md").write_text(
                "# Current architecture context\n"
            )
            result = apply(feature, "standard")
            workflow = json.loads(
                (feature / "_kapelle" / "workflow.json").read_text()
            )
            self.assertEqual("legacy-migration", workflow["created_from"])
            self.assertEqual("standard", workflow["lane"])
            self.assertIn("lane: standard", (feature / "proposal.md").read_text())
            self.assertEqual(f"/kapelle:spec {feature.name}", result["next_command"])
            self.assertFalse((feature / "_kapelle" / "approvals").exists())


if __name__ == "__main__":
    unittest.main()
