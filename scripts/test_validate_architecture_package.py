#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from feature_state import FeatureStateError, atomic_write_json
from jsonschema_lite import validate_instance
from review_gate import approve
from validate_architecture_package import validate
from validate_design import DESIGN_FORMAT_MARKER, REQUIRED_HEADINGS


class ArchitecturePackageValidatorTests(unittest.TestCase):
    def make_feature(self, root: Path) -> Path:
        feature = root / "docs" / "features" / "architecture-test"
        feature.mkdir(parents=True)
        (feature / "proposal.md").write_text("# Proposal\n")
        (feature / "spec.md").write_text("# Specification\n")
        (feature / "specs").mkdir()
        (feature / "specs" / "flows.md").write_text("# Flows\n")
        (feature / "_context").mkdir()
        (feature / "_context" / "architecture.md").write_text("# Context\n")
        approve(feature, "outline", "Developer accepted outline.", refresh=False)
        approve(
            feature,
            "business-spec",
            "Developer accepted business specification.",
            refresh=False,
        )

        design = [DESIGN_FORMAT_MARKER, "# Design", ""]
        for heading in REQUIRED_HEADINGS:
            design.extend([heading, "", "Concise decision.", ""])
        (feature / "design.md").write_text("\n".join(design))
        (feature / "design").mkdir()
        (feature / "design" / "backend.md").write_text("# Backend\n")
        (feature / "contracts").mkdir()
        (feature / "contracts" / "api.md").write_text("# API contract\n")
        internal = feature / "_kapelle"
        atomic_write_json(
            internal / "surface-plan.json",
            {
                "slug": feature.name,
                "aspects": [
                    {
                        "id": "backend",
                        "intent": "Serve the use case",
                        "modules": ["Application"],
                        "entrypoints": ["POST /feature"],
                        "depends_on": [],
                    }
                ],
                "contracts": [],
                "integration_checks": [],
            },
        )
        atomic_write_json(
            internal / "architecture-guidance" / "design.json",
            {
                "status": "ARCHITECTURE_GUIDANCE_READY",
                "capability": {
                    "name": "project architecture rules",
                    "kind": "project-subagent",
                },
                "scope": {
                    "aspects": ["backend"],
                    "modules": ["Application"],
                    "entrypoints": ["POST /feature"],
                    "paths": ["src/"],
                },
                "rules": [
                    {
                        "title": "Dependency direction",
                        "summary": "Application depends inward.",
                        "source": "docs/architecture.md",
                    }
                ],
                "sources": ["docs/architecture.md"],
                "gaps": [],
            },
        )
        return feature

    def test_complete_package_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_feature(Path(tmp))
            self.assertEqual([], validate(feature))
            approve(
                feature,
                "architecture",
                "Developer accepted architecture.",
                refresh=False,
            )

    def test_missing_detail_contract_and_guidance_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_feature(Path(tmp))
            (feature / "design" / "backend.md").unlink()
            (feature / "contracts" / "api.md").unlink()
            guidance = (
                feature / "_kapelle" / "architecture-guidance" / "design.json"
            )
            value = json.loads(guidance.read_text())
            value["status"] = "BLOCKED"
            value["gaps"] = ["Missing project rule"]
            guidance.write_text(json.dumps(value))
            self.assertEqual(
                [],
                validate_instance(
                    value,
                    Path(__file__).resolve().parent.parent
                    / "dispatcher"
                    / "architecture-guidance.schema.json",
                ),
            )
            errors = validate(feature)
            self.assertTrue(any("detailed design package" in item for item in errors))
            self.assertTrue(any("contracts package" in item for item in errors))
            self.assertTrue(any("not approval-ready" in item for item in errors))

    def test_surface_and_guidance_aspects_must_match(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_feature(Path(tmp))
            guidance = (
                feature / "_kapelle" / "architecture-guidance" / "design.json"
            )
            value = json.loads(guidance.read_text())
            value["scope"]["aspects"] = ["frontend"]
            guidance.write_text(json.dumps(value))
            self.assertTrue(
                any("exactly match" in item for item in validate(feature))
            )
            with self.assertRaises(FeatureStateError):
                approve(
                    feature,
                    "architecture",
                    "Developer accepted architecture.",
                    refresh=False,
                )

    def test_surface_dependency_cycle_is_semantic_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_feature(Path(tmp))
            surface_path = feature / "_kapelle" / "surface-plan.json"
            surface = json.loads(surface_path.read_text())
            surface["aspects"][0]["depends_on"] = ["frontend"]
            surface["aspects"].append(
                {
                    "id": "frontend",
                    "intent": "Call the use case",
                    "modules": ["UI"],
                    "entrypoints": ["feature screen"],
                    "depends_on": ["backend"],
                }
            )
            surface_path.write_text(json.dumps(surface))
            guidance_path = (
                feature / "_kapelle" / "architecture-guidance" / "design.json"
            )
            guidance = json.loads(guidance_path.read_text())
            guidance["scope"]["aspects"] = ["backend", "frontend"]
            guidance_path.write_text(json.dumps(guidance))
            self.assertTrue(
                any("dependency cycle" in item for item in validate(feature))
            )


if __name__ == "__main__":
    unittest.main()
