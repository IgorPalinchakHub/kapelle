"""Read the durable, opt-in architecture review order (no generated graph)."""

import re
from pathlib import Path

MARKER = "<!-- kapelle-design: staged-v1 -->"
REVIEW = "design/architecture-review.md"
INTEGRATION = "design/integration.md"
PREFIX = "design-part-"


def enabled(root: Path) -> bool:
    design = root / "design.md"
    return (
        (design.is_file() and MARKER in design.read_text())
        or (root / REVIEW).exists()
        or any((root / "_kapelle/approvals").glob("design-*.json"))
    )


def safe_document(root: Path, value: str, prefix: str) -> str:
    if not re.fullmatch(r"[a-zA-Z0-9_./-]+\.md", value):
        raise ValueError(f"invalid architecture document path: {value}")
    path = Path(value)
    if not value.startswith(prefix + "/") or ".." in path.parts or path.is_absolute():
        raise ValueError(f"architecture document must be inside {prefix}/: {value}")
    if not (root / path).resolve().is_relative_to(root.resolve()):
        raise ValueError(f"architecture document escapes feature: {value}")
    return value


def parts(root: Path) -> dict[str, tuple[str, ...]]:
    """Parse only the explicit Review order table; future candidates stay outside it."""
    path = root / REVIEW
    safe_document(root, REVIEW, "design")
    if not path.is_file():
        raise ValueError(f"staged design requires {REVIEW}")
    text = path.read_text()
    sections = re.split(r"(?m)^## Review order\s*$", text)
    if len(sections) != 2:
        raise ValueError("architecture review requires exactly one ## Review order section")
    section = re.split(r"(?m)^## ", sections[1])[0]
    rows = [line.strip() for line in section.splitlines() if line.strip()]
    if len(rows) < 3 or rows[0] != "| Part | Design | Contracts |" or not re.fullmatch(
        r"\|\s*-+\s*\|\s*-+\s*\|\s*-+\s*\|", rows[1]
    ):
        raise ValueError("review order requires a Part | Design | Contracts table")
    result = {}
    documents = set()
    for row in rows[2:]:
        cells = [cell.strip() for cell in row.split("|")]
        if len(cells) != 5 or cells[0] or cells[-1]:
            raise ValueError("invalid architecture review table row")
        key, document, contracts = cells[1:4]
        if not re.fullmatch(r"[a-z][a-z0-9-]{0,63}", key) or key in result:
            raise ValueError(f"invalid or duplicate architecture part: {key}")
        document = safe_document(root, document, "design")
        if document in {REVIEW, INTEGRATION} or document in documents:
            raise ValueError(f"architecture part requires a unique detail document: {document}")
        documents.add(document)
        inputs = [] if contracts == "-" else [
            safe_document(root, value.strip(), "contracts") for value in contracts.split(",")
        ]
        result[key] = (document, *inputs)
    return result


def artifacts(root: Path, gate: str) -> tuple[str, ...]:
    mapping = parts(root)
    base = (REVIEW, "spec.md", "_kapelle/architecture-guidance/design.json")
    if gate == "design-vision":
        return base
    key = gate.removeprefix(PREFIX)
    if not gate.startswith(PREFIX) or key not in mapping:
        raise ValueError(f"unknown architecture part gate: {gate}")
    return (*base, *mapping[key])
