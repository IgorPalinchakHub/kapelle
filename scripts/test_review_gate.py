#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from feature_state import FeatureStateError, approval_current, choose_next_command
from review_gate import approve, build_gate


class ReviewGateTests(unittest.TestCase):
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
                ("spec", f"/kapelle:spec {feature.name}"),
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
                ("design", f"/kapelle:design {feature.name}"),
                choose_next_command(feature.name, feature, {}, False, False),
            )


if __name__ == "__main__":
    unittest.main()
