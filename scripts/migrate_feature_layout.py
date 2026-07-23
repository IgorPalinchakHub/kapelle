#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any

from feature_state import (
    FeatureStateError,
    atomic_write_json,
    atomic_write_text,
    change_state_error,
    read_json,
    rebuild_feature_state,
    resolve_feature_dir,
)
from validate_task_plan import validate as validate_task_plan

ARCHIVE_TARGETS = {
    "_audit": "_kapelle/history/legacy/audit",
    "_review": "_kapelle/history/legacy/review",
    ".size": "_kapelle/history/legacy/size.txt",
    "ship.md": "_kapelle/history/legacy/ship.md",
}


def task_markdown(plan: dict[str, Any]) -> str:
    workstreams = {item.get("id"): item for item in plan.get("workstreams", [])}
    grouped: dict[str, list[dict[str, Any]]] = {}
    for task in plan.get("tasks", []):
        grouped.setdefault(task.get("workstream_id", "UNASSIGNED"), []).append(task)
    lines = [
        "# Implementation tasks",
        "",
        "> Migrated from legacy `tasks.json`; validation evidence remains internal.",
        "",
    ]
    for workstream_id, tasks in grouped.items():
        title = workstreams.get(workstream_id, {}).get("title", workstream_id)
        lines.extend([f"## {title}", ""])
        for task in tasks:
            checked = "x" if task.get("status") == "completed" else " "
            acs = ", ".join(task.get("acs", []))
            suffix = f" — covers {acs}" if acs else ""
            lines.append(
                f"- [{checked}] **{task.get('id', 'UNKNOWN')} "
                f"{task.get('title', 'Untitled task')}**{suffix}"
            )
        lines.append("")
    return "\n".join(lines)


def strict_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text())
    except FileNotFoundError:
        raise FeatureStateError(f"missing {label}: {path.name}") from None
    except json.JSONDecodeError as exc:
        raise FeatureStateError(f"invalid {label}: {exc}") from None
    if not isinstance(value, dict):
        raise FeatureStateError(f"{label} must be a JSON object")
    return value


def preflight_legacy_inputs(feature_dir: Path) -> list[str]:
    """Validate all legacy semantics and future change-state collisions before writes."""
    warnings: list[str] = []
    tasks_path = feature_dir / "tasks.json"
    surface_path = feature_dir / "surface-plan.json"
    if tasks_path.is_file():
        plan = strict_json(tasks_path, "tasks.json")
        if not surface_path.is_file() or not (feature_dir / "spec.md").is_file():
            raise FeatureStateError(
                "tasks.json migration requires surface-plan.json and spec.md"
            )
        strict_json(surface_path, "surface-plan.json")
        task_ids = [
            item.get("id")
            for item in plan.get("tasks", [])
            if isinstance(item, dict)
        ]
        duplicates = sorted(
            task_id
            for task_id in set(task_ids)
            if task_id is not None and task_ids.count(task_id) > 1
        )
        if duplicates:
            raise FeatureStateError(f"duplicate legacy task ids: {duplicates}")
        try:
            semantic_errors = validate_task_plan(
                tasks_path, surface_path, feature_dir / "spec.md"
            )
        except (ValueError, OSError, json.JSONDecodeError) as exc:
            raise FeatureStateError(f"invalid legacy coordination: {exc}") from None
        if semantic_errors:
            raise FeatureStateError(
                "invalid legacy coordination: " + "; ".join(semantic_errors)
            )
    elif surface_path.is_file():
        strict_json(surface_path, "surface-plan.json")

    changes = feature_dir / "changes"
    if changes.is_dir():
        for state_path in sorted(changes.glob("*/state.json")):
            state = strict_json(
                state_path, str(state_path.relative_to(feature_dir))
            )
            error = change_state_error(state, state_path.parent.name)
            if error:
                raise FeatureStateError(
                    f"invalid {state_path.relative_to(feature_dir)}: {error}"
                )
        for active_state in sorted(changes.glob("*/active-state.json")):
            state = strict_json(active_state, str(active_state.relative_to(feature_dir)))
            if active_state.with_name("state.json").exists():
                raise FeatureStateError(
                    f"state collision in {active_state.parent.relative_to(feature_dir)}"
                )
            revision = state.get("current_revision", state.get("revision"))
            if isinstance(revision, str) and re.fullmatch(r"r\d+", revision):
                revision = int(revision[1:])
            if not isinstance(revision, int) or revision < 1:
                raise FeatureStateError(
                    f"invalid revision in {active_state.relative_to(feature_dir)}"
                )
            if state.get("state") not in {
                "running",
                "paused",
                "reconciling",
                "waiting-approval",
                "approved",
                "resumable",
                "blocked",
                "completed",
            }:
                raise FeatureStateError(
                    f"invalid state in {active_state.relative_to(feature_dir)}"
                )
    return warnings


def migration_plan(feature_dir: Path) -> dict[str, Any]:
    marker = feature_dir / "_kapelle" / "history" / "migration-v2.json"
    if marker.is_file():
        marker_value = strict_json(marker, "_kapelle/history/migration-v2.json")
        if (
            marker_value.get("layout_version") != 2
            or marker_value.get("status") != "migrated"
            or not isinstance(marker_value.get("actions"), list)
            or not isinstance(marker_value.get("warnings"), list)
        ):
            raise FeatureStateError("invalid layout-v2 migration marker")
        legacy_roots = [
            name
            for name in (
                "sad.md",
                "tasks.json",
                "surface-plan.json",
                "changes",
                "_audit",
                "_review",
                ".size",
                "ship.md",
            )
            if (feature_dir / name).exists()
        ]
        if legacy_roots:
            raise FeatureStateError(
                f"migration marker conflicts with legacy roots: {legacy_roots}"
            )
        return {"status": "already-migrated", "actions": [], "collisions": []}
    preflight_legacy_inputs(feature_dir)
    actions: list[dict[str, str]] = []
    collisions: list[str] = []
    warnings: list[str] = []

    if (feature_dir / "sad.md").is_file():
        if (feature_dir / "design.md").exists():
            collisions.append("design.md already exists while sad.md is present")
        else:
            actions.append({"action": "rename", "from": "sad.md", "to": "design.md"})
    if not (feature_dir / "proposal.md").is_file():
        actions.append({"action": "derive", "from": "spec.md", "to": "proposal.md"})
    if (feature_dir / "tasks.json").is_file():
        target = feature_dir / "_kapelle" / "task-plan.json"
        if target.exists():
            collisions.append("_kapelle/task-plan.json already exists while tasks.json is present")
        else:
            actions.append(
                {"action": "move", "from": "tasks.json", "to": "_kapelle/task-plan.json"}
            )
        if not (feature_dir / "tasks.md").is_file():
            actions.append({"action": "derive", "from": "tasks.json", "to": "tasks.md"})
    if (feature_dir / "surface-plan.json").is_file():
        target = feature_dir / "_kapelle" / "surface-plan.json"
        if target.exists():
            collisions.append(
                "_kapelle/surface-plan.json already exists while surface-plan.json is present"
            )
        else:
            actions.append(
                {
                    "action": "move",
                    "from": "surface-plan.json",
                    "to": "_kapelle/surface-plan.json",
                }
            )
    if (feature_dir / "changes").is_dir():
        if (feature_dir / "_kapelle" / "changes").exists():
            collisions.append("_kapelle/changes already exists while legacy changes is present")
        else:
            actions.append(
                {"action": "move", "from": "changes", "to": "_kapelle/changes"}
            )
            warnings.append(
                "Review migrated change requests/amendments and reflect current user-facing decisions in proposal.md, spec.md, design.md, or ADR."
            )
    if (feature_dir / ".size").is_file():
        if (feature_dir / "_kapelle" / "size.json").exists():
            collisions.append("_kapelle/size.json already exists while legacy .size is present")
        else:
            actions.append(
                {"action": "convert", "from": ".size", "to": "_kapelle/size.json"}
            )
    if (feature_dir / "ship.md").is_file():
        warnings.append(
            "Legacy ship.md is historical only and will not restore current ship readiness."
        )
    if (feature_dir / "data-model.md").is_file():
        warnings.append(
            "Review data-model.md and fold current data/schema decisions into design.md."
        )
    for name, target_name in ARCHIVE_TARGETS.items():
        if (feature_dir / name).exists():
            if (feature_dir / target_name).exists():
                collisions.append(
                    f"{target_name} already exists while legacy {name} is present"
                )
                continue
            actions.append(
                {
                    "action": "archive",
                    "from": name,
                    "to": target_name,
                }
            )
    return {
        "status": "blocked" if collisions else "ready",
        "actions": actions,
        "collisions": collisions,
        "warnings": warnings,
    }


def canonical_change_state(change_id: str, legacy: dict[str, Any]) -> dict[str, Any]:
    revision = legacy.get("current_revision", legacy.get("revision"))
    if isinstance(revision, str) and re.fullmatch(r"r\d+", revision):
        revision = int(revision[1:])
    result: dict[str, Any] = {
        "change_id": legacy.get("change_id") or change_id,
        "current_revision": revision,
        "state": legacy.get("state"),
        "paused_task": legacy.get("paused_task"),
        "reason": legacy.get("reason", "Migrated from legacy active-state.json"),
    }
    if isinstance(legacy.get("checkpoint_evidence"), list):
        result["checkpoint_evidence"] = legacy["checkpoint_evidence"]
    return result


def apply_migration(
    feature_dir: Path, supplied_plan: dict[str, Any] | None = None
) -> None:
    del supplied_plan  # a caller cannot bypass a fresh preflight with a stale plan
    plan = migration_plan(feature_dir)
    if plan["collisions"]:
        raise FeatureStateError("; ".join(plan["collisions"]))
    if plan["status"] == "already-migrated":
        return
    internal = feature_dir / "_kapelle"
    legacy = internal / "history" / "legacy"
    internal.mkdir(parents=True, exist_ok=True)

    legacy_tasks = (
        strict_json(feature_dir / "tasks.json", "tasks.json")
        if (feature_dir / "tasks.json").is_file()
        else None
    )
    legacy_change_states = {
        active_state.parent.name: strict_json(
            active_state, str(active_state.relative_to(feature_dir))
        )
        for active_state in sorted((feature_dir / "changes").glob("*/active-state.json"))
    } if (feature_dir / "changes").is_dir() else {}
    legacy_size = (
        (feature_dir / ".size").read_text(errors="replace")
        if (feature_dir / ".size").is_file()
        else None
    )
    if not (feature_dir / "proposal.md").is_file():
        atomic_write_text(
            feature_dir / "proposal.md",
            "# Feature proposal\n\n"
            "> Migrated from a legacy Kapelle feature. Confirm this summary before changing scope.\n\n"
            "## Summary\n\n"
            "See `spec.md` for the previously approved observable behavior.\n\n"
            "## Scope\n\n"
            "Preserve the scope recorded in `spec.md` until explicitly revised.\n",
        )
    if (feature_dir / "sad.md").is_file() and not (feature_dir / "design.md").exists():
        (feature_dir / "sad.md").replace(feature_dir / "design.md")
    if legacy_tasks and not (feature_dir / "tasks.md").is_file():
        atomic_write_text(feature_dir / "tasks.md", task_markdown(legacy_tasks))

    moves = [
        ("tasks.json", "_kapelle/task-plan.json"),
        ("surface-plan.json", "_kapelle/surface-plan.json"),
        ("changes", "_kapelle/changes"),
        ("_audit", "_kapelle/history/legacy/audit"),
        ("_review", "_kapelle/history/legacy/review"),
        (".size", "_kapelle/history/legacy/size.txt"),
        ("ship.md", "_kapelle/history/legacy/ship.md"),
    ]
    for source_name, target_name in moves:
        source = feature_dir / source_name
        target = feature_dir / target_name
        if not source.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(target))

    changes_dir = internal / "changes"
    for change_id, legacy_state in legacy_change_states.items():
        active_state = changes_dir / change_id / "active-state.json"
        state_path = active_state.with_name("state.json")
        atomic_write_json(
            state_path, canonical_change_state(change_id, legacy_state)
        )
        active_state.unlink()

    if legacy_size is not None:
        size_match = re.search(r"\b(XS|XL|S|M|L)\b", legacy_size, re.IGNORECASE)
        depth_match = re.search(r"\b(lean|standard|full)\b", legacy_size, re.IGNORECASE)
        atomic_write_json(
            internal / "size.json",
            {
                "size": size_match.group(1).upper() if size_match else "unknown",
                "execution_depth": depth_match.group(1).lower() if depth_match else None,
                "reason": (
                    "Migrated from legacy .size; reclassify if the extracted value is unknown."
                ),
                "legacy_text_sha256": hashlib.sha256(legacy_size.encode()).hexdigest(),
            },
        )

    marker = {
        "layout_version": 2,
        "status": "migrated",
        "legacy_preserved_at": "_kapelle/history/legacy",
        "actions": plan["actions"],
        "warnings": plan.get("warnings", []),
    }
    rebuild_feature_state(feature_dir, mode="migrated")
    from validate_feature_state import validate as validate_feature_state

    errors = validate_feature_state(feature_dir)
    if errors:
        raise FeatureStateError(
            "post-migration validation failed: " + "; ".join(errors)
        )
    atomic_write_json(internal / "history" / "migration-v2.json", marker)


def main() -> int:
    parser = argparse.ArgumentParser(description="Migrate a legacy Kapelle feature to layout-v2")
    parser.add_argument("feature_dir")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    try:
        feature_dir = resolve_feature_dir(args.feature_dir)
        plan = migration_plan(feature_dir)
        if args.apply:
            apply_migration(feature_dir, plan)
            result = {"status": "applied" if plan["status"] != "already-migrated" else "already-migrated"}
        else:
            result = plan
        print(json.dumps(result, indent=2, sort_keys=True))
        return 2 if plan.get("collisions") else 0
    except (FeatureStateError, OSError, json.JSONDecodeError) as exc:
        print(f"REFUSED: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
