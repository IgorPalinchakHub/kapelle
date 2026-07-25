#!/usr/bin/env python3
"""Validate the stable human-readable high-level design structure."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REQUIRED_HEADINGS = [
    "## 1. Context and goal",
    "## 2. Scope and constraints",
    "## 3. Architecture rules applied",
    "## 4. Building blocks and responsibilities",
    "## 5. Runtime flows",
    "## 6. Data and domain impact",
    "## 7. Contracts and integrations",
    "## 8. Cross-cutting concerns",
    "## 9. Decisions and trade-offs",
    "## 10. Validation and rollout",
    "## 11. Open questions",
]
MAX_LINES = 280
MAX_WORDS = 2800


def validate(path: Path) -> list[str]:
    if not path.is_file():
        return [f"missing design file: {path}"]
    lines = path.read_text(errors="replace").splitlines()
    headings = [
        line.strip()
        for line in lines
        if re.match(r"^##\s+\d+\.\s+", line.strip())
    ]
    errors: list[str] = []
    if len(lines) > MAX_LINES:
        errors.append(
            f"high-level design has {len(lines)} lines; maximum is {MAX_LINES}; "
            "move boundary details under design/"
        )
    word_count = len(path.read_text(errors="replace").split())
    if word_count > MAX_WORDS:
        errors.append(
            f"high-level design has {word_count} words; maximum is {MAX_WORDS}; "
            "move boundary details under design/"
        )
    if headings != REQUIRED_HEADINGS:
        missing = [heading for heading in REQUIRED_HEADINGS if heading not in headings]
        unexpected = [heading for heading in headings if heading not in REQUIRED_HEADINGS]
        if missing:
            errors.append(f"missing headings: {missing}")
        if unexpected:
            errors.append(f"unexpected numbered headings: {unexpected}")
        if not missing and not unexpected:
            errors.append("design headings are out of order")

    positions = {
        line.strip(): index
        for index, line in enumerate(lines)
        if line.strip() in REQUIRED_HEADINGS
    }
    for index, heading in enumerate(REQUIRED_HEADINGS):
        if heading not in positions:
            continue
        start = positions[heading] + 1
        end = (
            positions[REQUIRED_HEADINGS[index + 1]]
            if index + 1 < len(REQUIRED_HEADINGS)
            and REQUIRED_HEADINGS[index + 1] in positions
            else len(lines)
        )
        if not any(line.strip() for line in lines[start:end]):
            errors.append(f"empty section: {heading}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("design")
    args = parser.parse_args()
    errors = validate(Path(args.design))
    if errors:
        print(f"FAILED: {len(errors)} design error(s)")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASSED: design structure and high-level size are valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
