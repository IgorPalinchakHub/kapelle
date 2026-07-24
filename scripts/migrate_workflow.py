#!/usr/bin/env python3
"""Migrate a feature to the single human-controlled workflow marker and routing."""

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
)

MARKER_PATTERN = re.compile(
    r"<!--\s*kapelle-workflow:\s*human-controlled-v1(?:;\s*lane:\s*(fast|standard))?\s*-->"
)


def plan(feature_dir: Path, lane: str) -> dict[str, object]:
    proposal = feature_dir / "proposal.md"
    if not proposal.is_file():
        raise FeatureStateError(
            "proposal.md is required; create a factual proposal from existing documents first"
        )
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
    next_command = (
        f"/kapelle:start {feature_dir.name} --approve"
        if lane == "fast" and not missing
        else f"/kapelle:spec {feature_dir.name}"
        if (feature_dir / "spec.md").is_file()
        else f'/kapelle:start {feature_dir.name} "<raw task>"'
    )
    return {
        "slug": feature_dir.name,
        "lane": lane,
        "preserved": preserved,
        "missing_target_artifacts": missing,
        "evidence_not_recreated": [
            "approvals",
            "agent and review verdicts",
            "validation command output",
            "telemetry",
        ],
        "next_command": next_command,
    }


def apply(feature_dir: Path, lane: str) -> dict[str, object]:
    migration = plan(feature_dir, lane)
    proposal = feature_dir / "proposal.md"
    text = proposal.read_text(errors="replace")
    marker = f"<!-- kapelle-workflow: human-controlled-v1; lane: {lane} -->"
    if MARKER_PATTERN.search(text):
        text = MARKER_PATTERN.sub(marker, text, count=1)
    else:
        text = f"{marker}\n{text}"
    atomic_write_text(proposal, text)
    atomic_write_json(
        feature_dir / "_kapelle" / "workflow.json",
        {
            "workflow": "human-controlled",
            "version": 1,
            "created_from": "legacy-migration",
            "lane": lane,
        },
    )
    size_path = feature_dir / "_kapelle" / "size.json"
    size = read_json(size_path)
    if size:
        value = size.get("size", "unknown")
        size["lane"] = lane
        size["interview_depth"] = (
            "lean" if value in {"XS", "S"} else "standard" if value == "M" else "deep"
        )
        atomic_write_json(size_path, size)
    _, state, _ = refresh_feature_status(feature_dir)
    migration["next_command"] = state["next_command"]
    migration["status"] = "migrated"
    return migration


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("feature_dir")
    parser.add_argument("--lane", choices=["fast", "standard"], default="standard")
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
