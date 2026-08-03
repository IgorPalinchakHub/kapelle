#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from feature_state import FeatureStateError, phase_evidence_current
from record_verification import build_verification


class RecordVerificationTests(unittest.TestCase):
    def make_feature(self, root: Path) -> Path:
        feature = root / "docs" / "features" / "manual-verification"
        feature.mkdir(parents=True)
        (feature / "spec.md").write_text("# Spec\n")
        (feature / "design.md").write_text("# Design\n")
        (feature / "tasks.md").write_text(
            "# Tasks\n\n## Delivery\n\n- [x] **W1 Deliver behavior**\n"
        )
        source = root / "src" / "feature.php"
        source.parent.mkdir()
        source.write_text("<?php\n")
        return feature

    def test_developer_attestation_requires_explicit_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_feature(Path(tmp))
            with self.assertRaises(FeatureStateError):
                build_verification(
                    feature,
                    status="PASS",
                    evidence_source="developer-attested",
                    categories=["functional"],
                    checks=["Complete manual feature verification"],
                    implementation_files=["src/feature.php"],
                    developer_confirmation=None,
                )

    def test_developer_attestation_is_current_pass_without_captured_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_feature(Path(tmp))
            payload = build_verification(
                feature,
                status="PASS",
                evidence_source="developer-attested",
                categories=["functional", "unit", "lint"],
                checks=["Developer completed the full planned verification batch"],
                implementation_files=["src/feature.php"],
                developer_confirmation=(
                    "I manually tested and verified everything; all planned checks pass."
                ),
            )
            internal = feature / "_kapelle"
            internal.mkdir()
            import json

            (internal / "verification.json").write_text(json.dumps(payload))
            self.assertTrue(
                phase_evidence_current(feature, "verification.json", {"PASS"})
            )

            payload.pop("developer_confirmation")
            (internal / "verification.json").write_text(json.dumps(payload))
            self.assertFalse(
                phase_evidence_current(feature, "verification.json", {"PASS"})
            )


if __name__ == "__main__":
    unittest.main()
