#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from validate_progressive_docs import (
    ARTIFACT_MARKER,
    DESIGN_HEADINGS,
    DOMAIN_HEADINGS,
    SPEC_HEADINGS,
    USE_CASE_HEADINGS,
    WORKFLOW_MARKER,
    progressive_format,
    validate,
)


def document(title: str, headings: list[str]) -> str:
    lines = [title, ""]
    for heading in headings:
        lines.extend([heading, "", "Concrete content.", ""])
    return "\n".join(lines)


class ProgressiveDocsTests(unittest.TestCase):
    def make_feature(self, root: Path) -> Path:
        feature = root / "docs" / "features" / "progressive"
        feature.mkdir(parents=True)
        spec = document("# Feature specification", SPEC_HEADINGS)
        (feature / "spec.md").write_text(
            f"{WORKFLOW_MARKER}\n{ARTIFACT_MARKER}\n{spec}"
        )
        (feature / "design.md").write_text(
            document("# System design", DESIGN_HEADINGS)
        )
        return feature

    def test_valid_minimal_package(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_feature(Path(tmp))
            self.assertTrue(progressive_format(feature))
            self.assertEqual([], validate(feature))

    def test_missing_and_empty_sections_fail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_feature(Path(tmp))
            (feature / "design.md").write_text(
                "# System design\n\n"
                + "\n\n".join(DESIGN_HEADINGS[:-1])
            )
            errors = validate(feature)
            self.assertTrue(any("missing headings" in error for error in errors))
            self.assertTrue(any("empty section" in error for error in errors))

    def test_optional_detail_documents_are_checked_when_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_feature(Path(tmp))
            specs = feature / "specs"
            specs.mkdir()
            (specs / "post-invoices.md").write_text(
                document("# Post invoices", USE_CASE_HEADINGS)
            )
            design = feature / "design"
            design.mkdir()
            (design / "domain-model.md").write_text(
                document("# Domain model", DOMAIN_HEADINGS)
            )
            self.assertEqual([], validate(feature))

            (design / "domain-model.md").write_text("# Domain model\n")
            self.assertTrue(
                any("domain-model.md: missing headings" in error for error in validate(feature))
            )

    def test_compat_mode_accepts_older_lightweight_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_feature(Path(tmp))
            (feature / "spec.md").write_text(f"{WORKFLOW_MARKER}\n# Legacy spec\n")
            self.assertEqual([], validate(feature, require_format=False))
            self.assertTrue(validate(feature, require_format=True))


if __name__ == "__main__":
    unittest.main()
