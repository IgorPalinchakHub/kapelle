#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from validate_progressive_docs import (
    ARTIFACT_MARKER,
    COMMITTED_SUBHEADINGS,
    DESIGN_HEADINGS,
    DESIGN_DELTA_SUBHEADINGS,
    DOMAIN_HEADINGS,
    LIVING_CONTRACT_MARKER,
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

    def make_living_feature(self, root: Path) -> Path:
        feature = root / "docs" / "features" / "living"
        feature.mkdir(parents=True)
        spec_lines = [
            WORKFLOW_MARKER,
            ARTIFACT_MARKER,
            LIVING_CONTRACT_MARKER,
            "# Feature specification",
            "",
        ]
        for heading in SPEC_HEADINGS:
            spec_lines.extend([heading, "", "Concrete content.", ""])
            if heading == "## 3. Committed behavior":
                for subheading in COMMITTED_SUBHEADINGS:
                    content = "- **AC-01** Observable result."
                    if subheading != "### Acceptance scenarios":
                        content = "Concrete living content."
                    spec_lines.extend([subheading, "", content, ""])
        (feature / "spec.md").write_text("\n".join(spec_lines))

        design_lines = ["# System design", ""]
        for heading in DESIGN_HEADINGS:
            design_lines.extend([heading, "", "Concrete content.", ""])
            if heading == "## 2. System boundaries and responsibilities":
                for subheading in DESIGN_DELTA_SUBHEADINGS:
                    design_lines.extend([subheading, "", "Concrete design content.", ""])
        (feature / "design.md").write_text("\n".join(design_lines))
        (feature / "tasks.md").write_text(
            "# Tasks\n\n"
            "- [ ] **W1 Deliver result** — covers AC-01\n"
            "  - Changes: affected behavior.\n"
            "  - Done when: observable result exists.\n"
            "  - Verify: focused behavior check passes.\n"
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

    def test_valid_living_package_checks_delta_tasks_trace_and_diagram(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_living_feature(Path(tmp))
            design = feature / "design.md"
            design.write_text(
                design.read_text()
                + "\n```mermaid\nflowchart LR\nA --> B\n```\n\n"
                + "The flow moves from A to B.\n"
            )
            self.assertEqual([], validate(feature))

    def test_living_package_requires_compact_subheadings_and_task_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_living_feature(Path(tmp))
            spec = feature / "spec.md"
            spec.write_text(spec.read_text().replace("### Preserved behavior", "### Missing"))
            tasks = feature / "tasks.md"
            tasks.write_text(tasks.read_text().replace("  - Verify:", "  - Evidence:"))
            errors = validate(feature)
            self.assertTrue(any("missing living-contract subheadings" in item for item in errors))
            self.assertTrue(any("missing field: Verify" in item for item in errors))

    def test_living_task_limit_and_fields_apply_only_to_active_top_level_work(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_living_feature(Path(tmp))
            tasks = feature / "tasks.md"
            tasks.write_text(
                "# Tasks\n\n"
                "- [x] **W0 Legacy base** — covers AC-90\n"
                "  - Result: shipped before the living contract.\n"
                "- [x] **W1 Earlier slice** — covers AC-91\n"
                "- [x] **W2 Earlier slice** — covers AC-92\n"
                "- [x] **W3 Earlier slice** — covers AC-93\n"
                "- [ ] **W4 Active slice** — covers AC-01\n"
                "  - [ ] Nested implementation note.\n"
                "  - Changes: affected behavior.\n"
                "  - Done when: observable result exists.\n"
                "  - Verify: focused behavior check passes.\n"
            )
            self.assertEqual([], validate(feature))

            active = ""
            for index in range(1, 5):
                active += (
                    f"- [ ] **W{index} Active slice** — covers AC-01\n"
                    "  - Changes: affected behavior.\n"
                    "  - Done when: observable result exists.\n"
                    "  - Verify: focused behavior check passes.\n"
                )
            tasks.write_text(f"# Tasks\n\n{active}")
            self.assertTrue(
                any("at most three active workstream" in item for item in validate(feature))
            )

    def test_active_slice_cannot_reuse_checked_historical_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_living_feature(Path(tmp))
            spec = feature / "spec.md"
            spec.write_text(
                spec.read_text().replace(
                    "- **AC-01** Observable result.",
                    "- **AC-01** First result.\n- **AC-02** Second result.",
                )
            )
            (feature / "tasks.md").write_text(
                "# Tasks\n\n"
                "- [x] **W0 Historical work** — covers AC-01\n"
                "- [ ] **W1 Active slice** — covers AC-02\n"
                "  - Changes: affected behavior.\n"
                "  - Done when: observable result exists.\n"
                "  - Verify: focused behavior check passes.\n"
            )
            self.assertTrue(
                any("without workstream coverage: ['AC-01']" in item for item in validate(feature))
            )

    def test_checked_work_covers_scenarios_when_no_slice_is_active(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_living_feature(Path(tmp))
            tasks = feature / "tasks.md"
            tasks.write_text("# Tasks\n\n- [x] **W1 Completed result** — covers AC-01\n")
            self.assertEqual([], validate(feature))

    def test_living_traceability_rejects_unknown_and_uncovered_scenarios(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_living_feature(Path(tmp))
            spec = feature / "spec.md"
            spec.write_text(
                spec.read_text().replace(
                    "- **AC-01** Observable result.",
                    "- **AC-01** First result.\n- **AC-02** Second result.",
                )
            )
            tasks = feature / "tasks.md"
            tasks.write_text(tasks.read_text().replace("covers AC-01", "covers AC-99"))
            errors = validate(feature)
            self.assertTrue(any("references unknown scenarios" in item for item in errors))
            self.assertTrue(any("without workstream coverage" in item for item in errors))

    def test_living_traceability_expands_compact_ranges(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_living_feature(Path(tmp))
            spec = feature / "spec.md"
            spec.write_text(
                spec.read_text().replace(
                    "- **AC-01** Observable result.",
                    "- **AC-01** First result.\n- **AC-02** Second result.\n"
                    "- **AC-03** Third result.",
                )
            )
            tasks = feature / "tasks.md"
            tasks.write_text(tasks.read_text().replace("covers AC-01", "covers AC-01–AC-03"))
            self.assertEqual([], validate(feature))

    def test_living_traceability_preserves_id_width_and_bounds_ranges(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_living_feature(Path(tmp))
            spec = feature / "spec.md"
            tasks = feature / "tasks.md"
            spec.write_text(spec.read_text().replace("AC-01", "AC-001"))
            errors = validate(feature)
            self.assertTrue(any("unknown scenarios: ['AC-01']" in item for item in errors))
            self.assertTrue(any("without workstream coverage: ['AC-001']" in item for item in errors))

            spec.write_text(
                spec.read_text().replace(
                    "- **AC-001** Observable result.",
                    "- **AC-01** First.\n- **AC-02** Middle.\n- **AC-102** Last.",
                )
            )
            tasks.write_text(tasks.read_text().replace("covers AC-01", "covers AC-01–AC-102"))
            self.assertTrue(
                any("without workstream coverage: ['AC-02']" in item for item in validate(feature))
            )

    def test_living_diagrams_require_closing_fence_and_explanation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_living_feature(Path(tmp))
            design = feature / "design.md"
            base = design.read_text()
            design.write_text(base + "\n```mermaid\nflowchart LR\nA --> B\n")
            self.assertTrue(any("no closing fence" in item for item in validate(feature)))

            design.write_text(base + "\n```mermaid\nflowchart LR\nA --> B\n```\n")
            self.assertTrue(
                any("needs nearby plain-language explanation" in item for item in validate(feature))
            )

            design.write_text(
                base
                + "\n```mermaid\nflowchart LR\nA --> B\n```\n\n"
                + "### Next section\n\nSection prose.\n"
            )
            self.assertTrue(
                any("needs nearby plain-language explanation" in item for item in validate(feature))
            )

    def test_missing_tasks_is_reported_without_traceability_crash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_living_feature(Path(tmp))
            (feature / "tasks.md").unlink()
            errors = validate(feature)
            self.assertEqual(1, len(errors))
            self.assertIn("missing document:", errors[0])

    def test_marker_errors_match_the_eight_line_scan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = self.make_feature(Path(tmp))
            spec = feature / "spec.md"
            spec.write_text(spec.read_text().replace(f"{WORKFLOW_MARKER}\n", ""))
            self.assertTrue(
                any("first eight lines" in item for item in validate(feature))
            )


if __name__ == "__main__":
    unittest.main()
