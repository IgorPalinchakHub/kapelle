#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from validate_design import MAX_LINES, MAX_WORDS, REQUIRED_HEADINGS, validate


class DesignValidatorTests(unittest.TestCase):
    def write_design(self, root: Path, headings: list[str]) -> Path:
        path = root / "design.md"
        body = ["# Design", ""]
        for heading in headings:
            body.extend([heading, "", "Concise evidence or not-applicable reason.", ""])
        path.write_text("\n".join(body))
        return path

    def test_complete_template_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_design(Path(tmp), REQUIRED_HEADINGS)
            self.assertEqual([], validate(path))

    def test_missing_or_reordered_heading_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            reordered = list(REQUIRED_HEADINGS)
            reordered[3], reordered[4] = reordered[4], reordered[3]
            path = self.write_design(Path(tmp), reordered)
            self.assertTrue(validate(path))
            path = self.write_design(Path(tmp), REQUIRED_HEADINGS[:-1])
            self.assertTrue(
                any("missing headings" in error for error in validate(path))
            )

    def test_empty_section_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_design(Path(tmp), REQUIRED_HEADINGS)
            path.write_text(
                path.read_text().replace(
                    f"{REQUIRED_HEADINGS[0]}\n\nConcise evidence or not-applicable reason.",
                    f"{REQUIRED_HEADINGS[0]}\n",
                )
            )
            self.assertTrue(any("empty section" in error for error in validate(path)))

    def test_oversized_high_level_design_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_design(Path(tmp), REQUIRED_HEADINGS)
            path.write_text(path.read_text() + ("detail\n" * MAX_LINES))
            self.assertTrue(any("lines" in error for error in validate(path)))
            path = self.write_design(Path(tmp), REQUIRED_HEADINGS)
            path.write_text(path.read_text() + (("word " * (MAX_WORDS + 1)) + "\n"))
            self.assertTrue(any("words" in error for error in validate(path)))


if __name__ == "__main__":
    unittest.main()
