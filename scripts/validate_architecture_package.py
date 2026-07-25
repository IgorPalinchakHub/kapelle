#!/usr/bin/env python3
"""Validate architecture-package readiness beyond structural JSON Schema checks."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from feature_state import approval_current, read_json, resolve_feature_dir
from jsonschema_lite import validate_instance
from validate_design import validate as validate_design

ROOT = Path(__file__).resolve().parent.parent
SURFACE_SCHEMA = ROOT / "dispatcher" / "surface-plan.schema.json"
GUIDANCE_SCHEMA = ROOT / "dispatcher" / "architecture-guidance.schema.json"


def _markdown_files(path: Path) -> list[Path]:
    return sorted(path.rglob("*.md")) if path.is_dir() else []


def _cycle_errors(aspects: list[dict[str, Any]]) -> list[str]:
    graph = {item["id"]: item["depends_on"] for item in aspects}
    errors: list[str] = []
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str, trail: list[str]) -> None:
        if node in visiting:
            start = trail.index(node)
            errors.append("surface aspect dependency cycle: " + " -> ".join(trail[start:] + [node]))
            return
        if node in visited:
            return
        visiting.add(node)
        for dependency in graph.get(node, []):
            if dependency in graph:
                visit(dependency, trail + [node])
        visiting.remove(node)
        visited.add(node)

    for aspect_id in graph:
        visit(aspect_id, [])
    return errors


def _surface_semantics(feature_dir: Path, surface: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if surface["slug"] != feature_dir.name:
        errors.append("_kapelle/surface-plan.json slug does not match feature directory")
    aspect_ids = {item["id"] for item in surface["aspects"]}
    for aspect in surface["aspects"]:
        unknown = set(aspect["depends_on"]) - aspect_ids
        if unknown:
            errors.append(
                f"surface aspect {aspect['id']!r} depends on unknown aspects: "
                + ", ".join(sorted(unknown))
            )
        if aspect["id"] in aspect["depends_on"]:
            errors.append(f"surface aspect {aspect['id']!r} depends on itself")
    errors.extend(_cycle_errors(surface["aspects"]))

    for contract in surface["contracts"]:
        participants = {
            contract["provider_aspect"],
            *contract["consumer_aspects"],
        }
        unknown = participants - aspect_ids
        if unknown:
            errors.append(
                f"surface contract {contract['id']!r} has unknown aspects: "
                + ", ".join(sorted(unknown))
            )
        artifact = contract["artifact"].split("#", 1)[0]
        artifact_path = (feature_dir / artifact).resolve()
        try:
            artifact_path.relative_to(feature_dir.resolve())
        except ValueError:
            errors.append(
                f"surface contract {contract['id']!r} artifact escapes feature directory"
            )
        else:
            if not artifact_path.is_file():
                errors.append(
                    f"surface contract {contract['id']!r} artifact does not exist: {artifact}"
                )
    for check in surface["integration_checks"]:
        unknown = set(check["aspects"]) - aspect_ids
        if unknown:
            errors.append(
                f"integration check {check['id']!r} has unknown aspects: "
                + ", ".join(sorted(unknown))
            )
    return errors


def _guidance_semantics(
    surface: dict[str, Any], guidance: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    if guidance["status"] != "ARCHITECTURE_GUIDANCE_READY":
        errors.append(
            "architecture guidance is structurally valid but not approval-ready: "
            f"status={guidance['status']}"
        )
    expected_aspects = {item["id"] for item in surface["aspects"]}
    if set(guidance["scope"]["aspects"]) != expected_aspects:
        errors.append(
            "architecture guidance scope.aspects must exactly match surface-plan aspects"
        )
    return errors


def validate(feature_dir: Path) -> list[str]:
    feature_dir = resolve_feature_dir(feature_dir)
    errors: list[str] = []
    if not approval_current(feature_dir, "business-spec"):
        errors.append("business-spec review gate is missing or stale")
    errors.extend(validate_design(feature_dir / "design.md"))
    if not _markdown_files(feature_dir / "design"):
        errors.append("detailed design package is missing under design/")
    if not _markdown_files(feature_dir / "contracts"):
        errors.append(
            "contracts package is missing; add changed contracts or an explicit no-contract document"
        )

    surface = read_json(feature_dir / "_kapelle" / "surface-plan.json")
    surface_structural: list[str] = []
    if surface is None:
        errors.append("missing or invalid _kapelle/surface-plan.json")
    else:
        surface_structural = validate_instance(surface, SURFACE_SCHEMA)
        errors.extend(f"surface-plan schema: {item}" for item in surface_structural)
        if not surface_structural:
            errors.extend(_surface_semantics(feature_dir, surface))

    guidance = read_json(
        feature_dir / "_kapelle" / "architecture-guidance" / "design.json"
    )
    if guidance is None:
        errors.append("missing or invalid _kapelle/architecture-guidance/design.json")
    else:
        structural = validate_instance(guidance, GUIDANCE_SCHEMA)
        errors.extend(f"architecture-guidance schema: {item}" for item in structural)
        if not structural and surface is not None and not surface_structural:
            errors.extend(_guidance_semantics(surface, guidance))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("feature_dir")
    args = parser.parse_args()
    try:
        errors = validate(Path(args.feature_dir))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors = [str(exc)]
    if errors:
        print(f"FAILED: {len(errors)} architecture-package error(s)")
        for error in errors:
            print(f"- {error}")
        print(
            "NEXT: /kapelle:design "
            f"{Path(args.feature_dir).name} --revise \"resolve the reported package errors\""
        )
        return 1
    print("PASSED: architecture package is approval-ready")
    return 0


if __name__ == "__main__":
    sys.exit(main())
