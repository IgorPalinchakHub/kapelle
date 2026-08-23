#!/usr/bin/env python3
"""Validate the compact progressive specification and design package."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from acceptance_criteria import expand_acceptance_criteria

ARTIFACT_MARKER = "<!-- kapelle-artifacts: progressive-map-v1 -->"
LIVING_CONTRACT_MARKER = "<!-- kapelle-artifact-contract: living-v1 -->"
WORKFLOW_MARKER = "<!-- kapelle-workflow: lightweight-v1 -->"
MARKER_SCAN_LINES = 8

SPEC_HEADINGS = [
    "## 1. Problem and intent",
    "## 2. Current behavior",
    "## 3. Committed behavior",
    "## 4. Use-case map",
    "## 5. Business rules and invariants",
    "## 6. Candidate capabilities",
    "## 7. Exclusions, assumptions, and open decisions",
]
DESIGN_HEADINGS = [
    "## 1. Context and constraints",
    "## 2. System boundaries and responsibilities",
    "## 3. End-to-end flow",
    "## 4. Domain and data",
    "## 5. Contracts and integrations",
    "## 6. Decisions, risks, and deferrals",
    "## 7. Current walking skeleton",
]
USE_CASE_HEADINGS = [
    "## Outcome",
    "## Trigger and actors",
    "## Preconditions",
    "## Main flow",
    "## Alternatives and failures",
    "## System reactions",
    "## Acceptance scenarios",
]
DOMAIN_HEADINGS = [
    "## Domain language",
    "## Aggregates and ownership",
    "## State and behavior",
    "## Invariants",
    "## Events and side effects",
    "## Persistence mapping",
]
COMMITTED_SUBHEADINGS = [
    "### Intended change",
    "### Resulting behavior",
    "### Preserved behavior",
    "### Acceptance scenarios",
]
DESIGN_DELTA_SUBHEADINGS = [
    "### Current architecture",
    "### Resulting architecture",
    "### Technical delta",
]
TASK_FIELD_LABELS = ["Changes", "Done when", "Verify"]
TASK_PATTERN = re.compile(r"^-\s+\[(?P<checked>[ xX])\]\s+")


def progressive_format(feature_dir: Path) -> bool:
    spec = feature_dir / "spec.md"
    if not spec.is_file():
        return False
    return ARTIFACT_MARKER in spec.read_text(errors="replace").splitlines()[:MARKER_SCAN_LINES]


def _validate_markdown(
    path: Path,
    required_headings: list[str],
    *,
    max_lines: int | None = None,
    max_words: int | None = None,
) -> list[str]:
    if not path.is_file():
        return [f"missing document: {path}"]
    text = path.read_text(errors="replace")
    lines = text.splitlines()
    headings = [
        line.strip()
        for line in lines
        if line.strip().startswith("## ")
    ]
    errors: list[str] = []
    relevant = [heading for heading in headings if heading in required_headings]
    missing = [heading for heading in required_headings if heading not in relevant]
    if missing:
        errors.append(f"{path.name}: missing headings: {missing}")
    elif relevant != required_headings:
        errors.append(f"{path.name}: required headings are out of order")

    positions = {
        line.strip(): index
        for index, line in enumerate(lines)
        if line.strip() in required_headings
    }
    for index, heading in enumerate(required_headings):
        if heading not in positions:
            continue
        start = positions[heading] + 1
        later_positions = [
            positions[item]
            for item in required_headings[index + 1 :]
            if item in positions
        ]
        end = min(later_positions) if later_positions else len(lines)
        if not any(line.strip() for line in lines[start:end]):
            errors.append(f"{path.name}: empty section: {heading}")

    if max_lines is not None and len(lines) > max_lines:
        errors.append(
            f"{path.name}: {len(lines)} lines exceeds the {max_lines}-line cap"
        )
    words = len(text.split())
    if max_words is not None and words > max_words:
        errors.append(
            f"{path.name}: {words} words exceeds the {max_words}-word cap"
        )
    return errors


def _validate_section_subheadings(
    path: Path,
    section_heading: str,
    next_heading: str,
    required_subheadings: list[str],
) -> list[str]:
    text = path.read_text(errors="replace")
    lines = text.splitlines()
    positions = {
        line.strip(): index
        for index, line in enumerate(lines)
        if line.strip() in {section_heading, next_heading}
    }
    if section_heading not in positions or next_heading not in positions:
        return []

    start = positions[section_heading] + 1
    end = positions[next_heading]
    section_lines = lines[start:end]
    found = [
        line.strip()
        for line in section_lines
        if line.strip().startswith("### ")
        and line.strip() in required_subheadings
    ]
    missing = [item for item in required_subheadings if item not in found]
    errors: list[str] = []
    if missing:
        errors.append(
            f"{path.name}: {section_heading} missing living-contract subheadings: {missing}"
        )
        return errors
    if found != required_subheadings:
        errors.append(
            f"{path.name}: {section_heading} living-contract subheadings are out of order"
        )

    local_positions = {
        line.strip(): index
        for index, line in enumerate(section_lines)
        if line.strip() in required_subheadings
    }
    for index, heading in enumerate(required_subheadings):
        content_start = local_positions[heading] + 1
        later = [
            local_positions[item]
            for item in required_subheadings[index + 1 :]
            if item in local_positions
        ]
        content_end = min(later) if later else len(section_lines)
        if not any(line.strip() for line in section_lines[content_start:content_end]):
            errors.append(f"{path.name}: empty living-contract subsection: {heading}")
    return errors


def _validate_living_tasks(path: Path) -> list[str]:
    if not path.is_file():
        return [f"missing document: {path}"]
    lines = path.read_text(errors="replace").splitlines()
    task_positions = [index for index, line in enumerate(lines) if TASK_PATTERN.match(line)]
    if not task_positions:
        return [f"{path.name}: living contract requires at least one workstream checkbox"]
    errors: list[str] = []
    active_positions = [
        index
        for index in task_positions
        if (match := TASK_PATTERN.match(lines[index]))
        and match.group("checked").lower() != "x"
    ]
    if len(active_positions) > 3:
        errors.append(
            f"{path.name}: living contract allows at most three active workstream checkboxes"
        )
    for task_index, start in enumerate(task_positions):
        match = TASK_PATTERN.match(lines[start])
        if match and match.group("checked").lower() == "x":
            continue
        end = task_positions[task_index + 1] if task_index + 1 < len(task_positions) else len(lines)
        block = lines[start + 1 : end]
        for label in TASK_FIELD_LABELS:
            prefix = f"- {label}:"
            matching = [line.strip() for line in block if line.strip().startswith(prefix)]
            if not matching:
                errors.append(
                    f"{path.name}: workstream {task_index + 1} missing field: {label}"
                )
            elif not matching[0][len(prefix) :].strip():
                errors.append(
                    f"{path.name}: workstream {task_index + 1} has empty field: {label}"
                )
    return errors


def _validate_mermaid_explanations(path: Path) -> list[str]:
    if not path.is_file():
        return []
    lines = path.read_text(errors="replace").splitlines()
    errors: list[str] = []
    index = 0
    diagram_number = 0
    while index < len(lines):
        if lines[index].strip() != "```mermaid":
            index += 1
            continue
        diagram_number += 1
        close = index + 1
        while close < len(lines) and lines[close].strip() != "```":
            close += 1
        if close >= len(lines):
            errors.append(
                f"{path.name}: Mermaid diagram {diagram_number} has no closing fence"
            )
            break
        if not any(line.strip() for line in lines[index + 1 : close]):
            errors.append(f"{path.name}: Mermaid diagram {diagram_number} is empty")

        explanation = close + 1
        has_explanation = False
        while explanation < len(lines):
            candidate = lines[explanation].strip()
            if candidate.startswith("#") or candidate.startswith("```"):
                break
            if (
                candidate
                and not candidate.startswith("<")
                and re.search(r"\w", candidate)
            ):
                has_explanation = True
                break
            explanation += 1
        if not has_explanation:
            errors.append(
                f"{path.name}: Mermaid diagram {diagram_number} needs nearby plain-language explanation"
            )
        index = close + 1
    return errors


def _extract_ac_ids(text: str) -> set[str]:
    return set(expand_acceptance_criteria(text, numeric_only=True))


def _validate_living_traceability(spec_path: Path, tasks_path: Path) -> list[str]:
    spec_lines = spec_path.read_text(errors="replace").splitlines()
    positions = {
        line.strip(): index
        for index, line in enumerate(spec_lines)
        if line.strip() in {"### Acceptance scenarios", "## 4. Use-case map"}
    }
    if "### Acceptance scenarios" not in positions or "## 4. Use-case map" not in positions:
        return []
    scenario_text = "\n".join(
        spec_lines[
            positions["### Acceptance scenarios"] + 1 : positions["## 4. Use-case map"]
        ]
    )
    scenario_ids = _extract_ac_ids(scenario_text)
    if not scenario_ids:
        return ["spec.md: living contract requires at least one AC-NN acceptance scenario"]

    task_lines = tasks_path.read_text(errors="replace").splitlines()
    task_positions = [
        index for index, line in enumerate(task_lines) if TASK_PATTERN.match(line)
    ]
    covered: set[str] = set()
    errors: list[str] = []
    for task_index, start in enumerate(task_positions):
        match = TASK_PATTERN.match(task_lines[start])
        end = (
            task_positions[task_index + 1]
            if task_index + 1 < len(task_positions)
            else len(task_lines)
        )
        task_text = "\n".join(task_lines[start:end])
        references = _extract_ac_ids(task_text)
        checked = bool(match and match.group("checked").lower() == "x")
        if not checked and not references:
            errors.append(
                f"tasks.md: active workstream {task_index + 1} must cover at least one AC-NN"
            )
        if not checked:
            unknown = sorted(references - scenario_ids)
            if unknown:
                errors.append(
                    f"tasks.md: active workstream {task_index + 1} references unknown scenarios: {unknown}"
                )
        if not checked:
            covered.update(references & scenario_ids)

    if not any(
        (match := TASK_PATTERN.match(task_lines[index]))
        and match.group("checked").lower() != "x"
        for index in task_positions
    ):
        for task_index, start in enumerate(task_positions):
            end = (
                task_positions[task_index + 1]
                if task_index + 1 < len(task_positions)
                else len(task_lines)
            )
            covered.update(_extract_ac_ids("\n".join(task_lines[start:end])) & scenario_ids)

    uncovered = sorted(scenario_ids - covered)
    if uncovered:
        errors.append(f"tasks.md: acceptance scenarios without workstream coverage: {uncovered}")
    return errors


def validate(feature_dir: Path, *, require_format: bool = True) -> list[str]:
    feature_dir = feature_dir.resolve()
    spec = feature_dir / "spec.md"
    design = feature_dir / "design.md"
    errors: list[str] = []

    if not spec.is_file():
        return [f"missing document: {spec}"]
    first_lines = spec.read_text(errors="replace").splitlines()[:MARKER_SCAN_LINES]
    if WORKFLOW_MARKER not in first_lines:
        errors.append("spec.md: missing lightweight workflow marker in first eight lines")
    if require_format and ARTIFACT_MARKER not in first_lines:
        errors.append("spec.md: missing progressive artifact marker in first eight lines")

    if not require_format and ARTIFACT_MARKER not in first_lines:
        return errors

    errors.extend(
        _validate_markdown(
            spec,
            SPEC_HEADINGS,
            max_lines=320,
            max_words=3200,
        )
    )
    errors.extend(
        _validate_markdown(
            design,
            DESIGN_HEADINGS,
            max_lines=240,
            max_words=2400,
        )
    )

    if LIVING_CONTRACT_MARKER in first_lines:
        errors.extend(
            _validate_section_subheadings(
                spec,
                "## 3. Committed behavior",
                "## 4. Use-case map",
                COMMITTED_SUBHEADINGS,
            )
        )
        errors.extend(
            _validate_section_subheadings(
                design,
                "## 2. System boundaries and responsibilities",
                "## 3. End-to-end flow",
                DESIGN_DELTA_SUBHEADINGS,
            )
        )
        tasks = feature_dir / "tasks.md"
        errors.extend(_validate_living_tasks(tasks))
        if tasks.is_file():
            errors.extend(_validate_living_traceability(spec, tasks))
        diagram_paths = [design]
        design_dir = feature_dir / "design"
        if design_dir.is_dir():
            diagram_paths.extend(sorted(design_dir.glob("*.md")))
        compatibility_sequences = feature_dir / "sequences.md"
        if compatibility_sequences.is_file():
            diagram_paths.append(compatibility_sequences)
        for path in diagram_paths:
            errors.extend(_validate_mermaid_explanations(path))

    specs_dir = feature_dir / "specs"
    if specs_dir.is_dir():
        for path in sorted(specs_dir.glob("*.md")):
            errors.extend(_validate_markdown(path, USE_CASE_HEADINGS))

    domain = feature_dir / "design" / "domain-model.md"
    if domain.is_file():
        errors.extend(_validate_markdown(domain, DOMAIN_HEADINGS))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("feature_dir")
    parser.add_argument(
        "--compat",
        action="store_true",
        help="Validate progressive structure only when its marker is already present.",
    )
    args = parser.parse_args()
    errors = validate(Path(args.feature_dir), require_format=not args.compat)
    if errors:
        print(f"FAILED: {len(errors)} progressive document error(s)")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASSED: progressive specification and design package")
    return 0


if __name__ == "__main__":
    sys.exit(main())
