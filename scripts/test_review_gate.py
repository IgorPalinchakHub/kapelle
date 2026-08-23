#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from feature_state import FeatureStateError, approval_current, choose_next_command
from review_gate import approve, build_gate, plan_readiness_errors
from validate_progressive_docs import (
    ARTIFACT_MARKER,
    DESIGN_HEADINGS,
    DOMAIN_HEADINGS,
    LIVING_CONTRACT_MARKER,
    SPEC_HEADINGS,
    USE_CASE_HEADINGS,
    WORKFLOW_MARKER,
)


class ReviewGateTests(unittest.TestCase):
    def structured_document(self, title: str, headings: list[str]) -> str:
        lines = [title, ""]
        for heading in headings:
            lines.extend([heading, "", "Concrete content.", ""])
        return "\n".join(lines)

    def make_feature(self, root: Path) -> Path:
        feature = root / "docs" / "features" / "gate-test"
        feature.mkdir(parents=True)
        (feature / "proposal.md").write_text("# Proposal\n")
        (feature / "spec.md").write_text("# Spec\n")
        (feature / "_context").mkdir()
        (feature / "_context" / "architecture.md").write_text("# Architecture context\n")
        (feature / "specs").mkdir()
        (feature / "specs" / "scenarios.md").write_text("# Scenarios\n")
        return feature

    def test_writer_uses_canonical_name_shape_and_full_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_feature(Path(tmp))
            approve(feature, "outline", "Developer accepted outline.", refresh=False)
            path = approve(
                feature,
                "business-spec",
                "Developer explicitly approved the business specification.",
                refresh=False,
            )
            self.assertEqual("business-spec.json", path.name)
            payload = json.loads(path.read_text())
            self.assertEqual(
                {
                    "gate",
                    "status",
                    "confirmation",
                    "artifact_fingerprints",
                },
                set(payload),
            )
            self.assertEqual(
                {"proposal.md", "spec.md", "specs"},
                set(payload["artifact_fingerprints"]),
            )
            self.assertTrue(
                all(
                    len(digest) == 64
                    for digest in payload["artifact_fingerprints"].values()
                )
            )
            self.assertTrue(approval_current(feature, "business-spec"))

    def test_writer_refuses_out_of_order_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_feature(Path(tmp))
            with self.assertRaises(FeatureStateError):
                approve(
                    feature,
                    "business-spec",
                    "Developer approved business specification.",
                    refresh=False,
                )

    def test_living_plan_reports_missing_tasks_once(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_feature(Path(tmp))
            (feature / "spec.md").write_text(
                f"{WORKFLOW_MARKER}\n{ARTIFACT_MARKER}\n{LIVING_CONTRACT_MARKER}\n"
                + self.structured_document("# Feature specification", SPEC_HEADINGS)
            )
            (feature / "design.md").write_text(
                self.structured_document("# System design", DESIGN_HEADINGS)
            )
            errors = plan_readiness_errors(feature)
            task_errors = [
                error
                for error in errors
                if "tasks.md" in error or "workstream task" in error
            ]
            self.assertEqual(1, len(task_errors))
            self.assertIn("missing document:", task_errors[0])

    def test_lightweight_plan_requires_ready_guidance_and_final_requires_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_feature(Path(tmp))
            (feature / "spec.md").write_text(
                "<!-- kapelle-workflow: lightweight-v1 -->\n# Spec\n"
            )
            (feature / "design.md").write_text("# Design\n")
            (feature / "tasks.md").write_text(
                "# Tasks\n\n## Delivery\n\n- [ ] **W1 Deliver behavior**\n"
            )
            guidance = feature / "_kapelle" / "architecture-guidance"
            guidance.mkdir(parents=True)
            (guidance / "design.json").write_text(
                json.dumps(
                    {
                        "status": "ARCHITECTURE_GUIDANCE_READY",
                        "capability": {
                            "name": "project-architecture-rules",
                            "kind": "project-subagent",
                        },
                        "scope": {
                            "aspects": ["feature"],
                            "modules": [],
                            "entrypoints": [],
                            "paths": [],
                        },
                        "rules": [],
                        "sources": [],
                        "gaps": [],
                    }
                )
            )
            approve(
                feature,
                "plan",
                "Developer explicitly approved the feature plan.",
                refresh=False,
            )
            self.assertTrue(approval_current(feature, "plan"))
            with self.assertRaises(FeatureStateError):
                approve(
                    feature,
                    "final",
                    "Developer explicitly approved the feature.",
                    refresh=False,
                )

    def test_new_raw_task_requires_progressive_docs_and_fingerprints_details(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_feature(Path(tmp))
            internal = feature / "_kapelle"
            internal.mkdir()
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
            (feature / "spec.md").write_text(
                f"{WORKFLOW_MARKER}\n# Incomplete specification\n"
            )
            (feature / "design.md").write_text("# Incomplete design\n")
            (feature / "tasks.md").write_text(
                "# Tasks\n\n## Delivery\n\n- [ ] **W1 Deliver behavior**\n"
            )
            guidance = internal / "architecture-guidance"
            guidance.mkdir()
            (guidance / "design.json").write_text(
                json.dumps(
                    {
                        "status": "ARCHITECTURE_GUIDANCE_READY",
                        "capability": {
                            "name": "project-architecture-rules",
                            "kind": "project-subagent",
                        },
                        "scope": {
                            "aspects": ["feature"],
                            "modules": [],
                            "entrypoints": [],
                            "paths": [],
                        },
                        "rules": [],
                        "sources": [],
                        "gaps": [],
                    }
                )
            )
            with self.assertRaises(FeatureStateError):
                approve(feature, "plan", "Developer approved.", refresh=False)

            (feature / "spec.md").write_text(
                f"{WORKFLOW_MARKER}\n{ARTIFACT_MARKER}\n"
                + self.structured_document("# Feature specification", SPEC_HEADINGS)
            )
            (feature / "design.md").write_text(
                self.structured_document("# System design", DESIGN_HEADINGS)
            )
            specs = feature / "specs"
            use_case = specs / "scenarios.md"
            use_case.write_text(
                self.structured_document("# Deliver", USE_CASE_HEADINGS)
            )
            detail = feature / "design"
            detail.mkdir()
            (detail / "domain-model.md").write_text(
                self.structured_document("# Domain model", DOMAIN_HEADINGS)
            )
            path = approve(feature, "plan", "Developer approved.", refresh=False)
            payload = json.loads(path.read_text())
            self.assertIn("specs", payload["artifact_fingerprints"])
            self.assertIn("design", payload["artifact_fingerprints"])
            self.assertTrue(approval_current(feature, "plan"))

            use_case.write_text("# Changed\n")
            self.assertFalse(approval_current(feature, "plan"))

    def test_outline_stays_current_when_spec_is_expanded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_feature(Path(tmp))
            approve(feature, "outline", "Developer accepted the outline.", refresh=False)
            (feature / "spec.md").write_text("# Expanded specification\n")
            self.assertTrue(approval_current(feature, "outline"))

    def test_alias_and_partial_gate_are_not_current(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_feature(Path(tmp))
            aliases = feature / "_kapelle" / "approvals"
            aliases.mkdir(parents=True)
            (aliases / "business-specification.json").write_text(
                json.dumps(
                    {
                        "gate": "business-specification",
                        "status": "accepted",
                        "fingerprints": {"spec.md": "short"},
                    }
                )
            )
            self.assertFalse(approval_current(feature, "business-spec"))
            partial = build_gate(
                feature,
                "business-spec",
                "Developer approved the business specification.",
            )
            partial["artifact_fingerprints"].pop("specs")
            (aliases / "business-spec.json").write_text(json.dumps(partial))
            self.assertFalse(approval_current(feature, "business-spec"))

    def test_aliases_route_status_back_to_spec_but_canonical_gates_advance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_feature(Path(tmp))
            internal = feature / "_kapelle"
            internal.mkdir()
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
            aliases = internal / "approvals"
            aliases.mkdir()
            for name, gate in [
                ("feature-outline.json", "feature-outline"),
                ("business-specification.json", "business-specification"),
            ]:
                (aliases / name).write_text(
                    json.dumps({"gate": gate, "status": "accepted"})
                )
            self.assertEqual(
                ("migrate", f"/kapelle:migrate {feature.name}"),
                choose_next_command(feature.name, feature, {}, False, False),
            )
            approve(feature, "outline", "Developer accepted outline.", refresh=False)
            approve(
                feature,
                "business-spec",
                "Developer approved business specification.",
                refresh=False,
            )
            self.assertEqual(
                ("migrate", f"/kapelle:migrate {feature.name}"),
                choose_next_command(feature.name, feature, {}, False, False),
            )


if __name__ == "__main__":
    unittest.main()
