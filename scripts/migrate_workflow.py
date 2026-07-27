#!/usr/bin/env python3
"""Migrate a feature to the lightweight human-controlled workflow."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from feature_state import (
    FeatureStateError,
    atomic_write_json,
    atomic_write_text,
    read_json,
    refresh_feature_status,
    resolve_feature_dir,
    schema_errors,
)

MARKER_PATTERN = re.compile(
    r"<!--\s*kapelle-workflow:\s*lightweight-v1\s*-->"
)


def normalize_architecture_guidance(value: dict[str, object]) -> dict[str, object] | None:
    """Convert the pre-lightweight guidance shape without inventing new evidence."""
    if not schema_errors(value, "architecture-guidance.schema.json"):
        return value

    capability = value.get("capability")
    scope = value.get("scope")
    rules = value.get("rules")
    if not isinstance(capability, dict) or not isinstance(scope, dict):
        return None
    if not isinstance(rules, list):
        return None

    normalized_rules: list[dict[str, str]] = []
    sources: list[str] = []
    for rule in rules:
        if not isinstance(rule, dict):
            return None
        title = rule.get("title") or rule.get("id")
        summary = rule.get("summary")
        source = rule.get("source")
        if not all(isinstance(item, str) and item for item in (title, summary, source)):
            return None
        normalized_rules.append(
            {"title": title, "summary": summary, "source": source}
        )
        if source not in sources:
            sources.append(source)

    declared_sources = value.get("sources", [])
    if isinstance(declared_sources, list):
        for source in declared_sources:
            if isinstance(source, str) and source and source not in sources:
                sources.append(source)
    precedents = value.get("precedents", [])
    if isinstance(precedents, list):
        for precedent in precedents:
            if not isinstance(precedent, dict):
                continue
            source = precedent.get("path")
            if isinstance(source, str) and source and source not in sources:
                sources.append(source)

    normalized: dict[str, object] = {
        "status": value.get("status"),
        "capability": {
            "name": capability.get("name"),
            "kind": capability.get("kind"),
        },
        "scope": {
            key: scope.get(key, [])
            for key in ("aspects", "modules", "entrypoints", "paths")
        },
        "rules": normalized_rules,
        "sources": sources,
        "gaps": value.get("gaps", []),
    }
    if schema_errors(normalized, "architecture-guidance.schema.json"):
        return None
    return normalized


def guidance_migration_plan(feature_dir: Path) -> tuple[list[str], list[str]]:
    normalized: list[str] = []
    blocked: list[str] = []
    guidance_dir = feature_dir / "_kapelle" / "architecture-guidance"
    if not guidance_dir.is_dir():
        return normalized, blocked
    for path in sorted(guidance_dir.glob("*.json")):
        value = read_json(path)
        relative = str(path.relative_to(feature_dir))
        if value is None:
            blocked.append(relative)
        elif schema_errors(value, "architecture-guidance.schema.json"):
            if normalize_architecture_guidance(value) is None:
                blocked.append(relative)
            else:
                normalized.append(relative)
    return normalized, blocked


def plan(feature_dir: Path, lane: str | None = None) -> dict[str, object]:
    del lane
    preserved = [
        relative
        for relative in (
            "proposal.md",
            "spec.md",
            "specs",
            "design.md",
            "design",
            "contracts",
            "adr",
            "tasks.md",
            "test-plan.md",
        )
        if (feature_dir / relative).exists()
    ]
    missing = [
        relative
        for relative in ("spec.md", "design.md", "tasks.md")
        if not (feature_dir / relative).is_file()
    ]
    guidance = feature_dir / "_kapelle" / "architecture-guidance" / "design.json"
    normalized_guidance, blocked_guidance = guidance_migration_plan(feature_dir)
    missing.extend(blocked_guidance)
    next_command = (
        f"/kapelle:start {feature_dir.name} --approve"
        if not missing and guidance.is_file()
        else f'/kapelle:start {feature_dir.name} "<raw task or revision request>"'
    )
    return {
        "slug": feature_dir.name,
        "profile": "lightweight",
        "preserved": preserved,
        "missing_target_artifacts": missing,
        "normalized_architecture_guidance": normalized_guidance,
        "missing_migration_prerequisites": (
            [] if (feature_dir / "spec.md").is_file() else ["spec.md"]
        ),
        "evidence_not_recreated": [
            "approvals",
            "agent and review verdicts",
            "validation command output",
            "telemetry",
        ],
        "next_command": next_command,
    }


def apply(feature_dir: Path, lane: str | None = None) -> dict[str, object]:
    migration = plan(feature_dir, lane)
    missing_prerequisites = migration["missing_migration_prerequisites"]
    if missing_prerequisites:
        raise FeatureStateError(
            "migration requires a durable product specification: "
            + ", ".join(missing_prerequisites)
        )
    blocked_guidance = [
        item
        for item in migration["missing_target_artifacts"]
        if str(item).startswith("_kapelle/architecture-guidance/")
    ]
    if blocked_guidance:
        raise FeatureStateError(
            "architecture guidance cannot be migrated safely: "
            + ", ".join(blocked_guidance)
        )
    guidance_writes: list[
        tuple[Path, dict[str, object], Path, dict[str, object]]
    ] = []
    for relative in migration["normalized_architecture_guidance"]:
        path = feature_dir / relative
        value = read_json(path)
        if value is None:
            raise FeatureStateError(f"invalid architecture guidance: {relative}")
        normalized = normalize_architecture_guidance(value)
        if normalized is None:
            raise FeatureStateError(
                f"architecture guidance cannot be normalized: {relative}"
            )
        archive = (
            feature_dir
            / "_kapelle"
            / "history"
            / "legacy"
            / "architecture-guidance"
            / path.name
        )
        if archive.is_file() and read_json(archive) != value:
            raise FeatureStateError(
                f"legacy guidance archive collision: {archive.relative_to(feature_dir)}"
            )
        guidance_writes.append((path, normalized, archive, value))
    for path, normalized, archive, value in guidance_writes:
        if not archive.is_file():
            atomic_write_json(archive, value)
        atomic_write_json(path, normalized)
    spec = feature_dir / "spec.md"
    text = spec.read_text(errors="replace")
    marker = "<!-- kapelle-workflow: lightweight-v1 -->"
    if MARKER_PATTERN.search(text):
        text = MARKER_PATTERN.sub(marker, text, count=1)
    else:
        text = f"{marker}\n{text}"
    atomic_write_text(spec, text)
    atomic_write_json(
        feature_dir / "_kapelle" / "workflow.json",
        {
            "workflow": "human-controlled",
            "version": 2,
            "created_from": "legacy-migration",
            "profile": "lightweight",
        },
    )
    _, state, _ = refresh_feature_status(feature_dir)
    migration["next_command"] = state["next_command"]
    migration["status"] = "migrated"
    return migration


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("feature_dir")
    parser.add_argument(
        "--lane",
        choices=["fast", "standard"],
        help="Deprecated compatibility option; lightweight migration has no lane.",
    )
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    try:
        feature_dir = resolve_feature_dir(args.feature_dir)
        result = apply(feature_dir, args.lane) if args.apply else plan(feature_dir, args.lane)
    except (FeatureStateError, OSError, ValueError) as exc:
        print(f"REFUSED: {exc}")
        return 1
    result.setdefault("status", "dry-run")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
