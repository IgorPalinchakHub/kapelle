#!/usr/bin/env python3
"""Validate the compact progressive specification and design package."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ARTIFACT_MARKER = "<!-- kapelle-artifacts: progressive-map-v1 -->"
WORKFLOW_MARKER = "<!-- kapelle-workflow: lightweight-v1 -->"

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


def progressive_format(feature_dir: Path) -> bool:
    spec = feature_dir / "spec.md"
    if not spec.is_file():
        return False
    return ARTIFACT_MARKER in spec.read_text(errors="replace").splitlines()[:6]


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


def validate(feature_dir: Path, *, require_format: bool = True) -> list[str]:
    feature_dir = feature_dir.resolve()
    spec = feature_dir / "spec.md"
    design = feature_dir / "design.md"
    errors: list[str] = []

    if not spec.is_file():
        return [f"missing document: {spec}"]
    first_lines = spec.read_text(errors="replace").splitlines()[:6]
    if WORKFLOW_MARKER not in first_lines:
        errors.append("spec.md: missing lightweight workflow marker in first six lines")
    if require_format and ARTIFACT_MARKER not in first_lines:
        errors.append("spec.md: missing progressive artifact marker in first six lines")

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
