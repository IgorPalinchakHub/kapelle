#!/usr/bin/env python3
"""Deterministic layout-v2 state, recovery, and STATUS.md helpers."""

from __future__ import annotations

import hashlib
import json
import re
import tempfile
from collections import Counter, OrderedDict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from validate_task_plan import validate as validate_task_plan

LAYOUT_VERSION = 2
SCHEMA_VERSION = "1.0"
HUMAN_ARTIFACTS = (
    "proposal.md",
    "spec.md",
    "design.md",
    "tasks.md",
    "test-plan.md",
)
EVIDENCE_LOSS = (
    "previous explicit approvals",
    "previous agent and review verdicts",
    "historical validation command output",
    "token and cost telemetry",
)
TASK_PATTERN = re.compile(
    r"^\s*-\s+\[(?P<checked>[ xX])\]\s+(?:\*\*)?(?P<id>[A-Za-z][A-Za-z0-9._-]*)"
    r"(?:\s+(?P<title>.*?))?(?:\*\*)?\s*$"
)
AC_PATTERN = re.compile(r"\bAC-[A-Za-z0-9][A-Za-z0-9._-]*\b")
AC_RANGE_PATTERN = re.compile(r"\bAC-(\d+)\s*[–—-]\s*AC-(\d+)\b")
TASK_ID_PATTERN = re.compile(r"\b[A-Z][A-Z0-9._-]*\d[A-Z0-9._-]*\b")


class FeatureStateError(ValueError):
    """Raised when a feature directory cannot be handled safely."""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def resolve_feature_dir(value: str | Path) -> Path:
    feature_dir = Path(value).expanduser().resolve()
    if not feature_dir.is_dir():
        raise FeatureStateError(f"feature directory does not exist: {feature_dir}")
    ensure_no_symlink_escape(feature_dir)
    return feature_dir


def ensure_no_symlink_escape(feature_dir: Path) -> None:
    """Refuse a feature tree whose symlink redirects runtime writes outside it."""
    root = feature_dir.resolve()
    for path in root.rglob("*"):
        if not path.is_symlink():
            continue
        try:
            path.resolve(strict=False).relative_to(root)
        except (OSError, ValueError):
            raise FeatureStateError(
                f"symlink escapes feature directory: {path.relative_to(root)}"
            ) from None


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None
    return value if isinstance(value, dict) else None


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        delete=False,
    ) as handle:
        handle.write(content)
        temporary = Path(handle.name)
    temporary.replace(path)


def atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    atomic_write_text(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


def file_fingerprint(path: Path) -> str | None:
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def document_fingerprints(feature_dir: Path) -> dict[str, str | None]:
    paths = list(HUMAN_ARTIFACTS) + ["contracts", "adr"]
    result: dict[str, str | None] = {}
    for relative in paths:
        path = feature_dir / relative
        if path.is_dir():
            digest = hashlib.sha256()
            files = sorted(item for item in path.rglob("*") if item.is_file())
            for item in files:
                digest.update(str(item.relative_to(path)).encode())
                digest.update(b"\0")
                digest.update(item.read_bytes())
                digest.update(b"\0")
            result[relative] = digest.hexdigest() if files else None
        else:
            result[relative] = file_fingerprint(path)
    return result


def normalized_task_plan_fingerprint(path: Path) -> str | None:
    plan = read_json(path)
    if plan is None:
        return None
    normalized = json.loads(json.dumps(plan))
    for task in normalized.get("tasks", []):
        if isinstance(task, dict):
            task.pop("status", None)
    payload = json.dumps(normalized, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def input_fingerprints(feature_dir: Path) -> dict[str, str]:
    result = {
        name: digest
        for name, digest in document_fingerprints(feature_dir).items()
        if digest is not None
    }
    surface = file_fingerprint(feature_dir / "_kapelle" / "surface-plan.json")
    task_plan = normalized_task_plan_fingerprint(
        feature_dir / "_kapelle" / "task-plan.json"
    )
    if surface:
        result["_kapelle/surface-plan.json"] = surface
    if task_plan:
        result["_kapelle/task-plan.json#structural"] = task_plan
    return result


def artifact_manifest(feature_dir: Path, fingerprints: dict[str, str | None]) -> dict[str, Any]:
    return {
        name: {
            "path": name,
            "exists": (feature_dir / name).exists(),
            "sha256": fingerprints.get(name),
        }
        for name in HUMAN_ARTIFACTS
    }


def expand_acceptance_criteria(text: str) -> list[str]:
    found = set(AC_PATTERN.findall(text))
    for match in AC_RANGE_PATTERN.finditer(text):
        start_text, end_text = match.groups()
        start, end = int(start_text), int(end_text)
        if start <= end and end - start <= 100:
            width = max(len(start_text), len(end_text))
            found.update(f"AC-{item:0{width}d}" for item in range(start, end + 1))
    return sorted(found)


def parse_tasks(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    workstream = "Unassigned"
    tasks: list[dict[str, Any]] = []
    seen: set[str] = set()
    lines = path.read_text(errors="replace").splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.startswith("## "):
            workstream = line[3:].strip()
            index += 1
            continue
        match = TASK_PATTERN.match(line)
        if not match:
            index += 1
            continue
        block = [line]
        cursor = index + 1
        while cursor < len(lines):
            candidate = lines[cursor]
            if candidate.startswith("## ") or TASK_PATTERN.match(candidate):
                break
            block.append(candidate)
            cursor += 1
        block_text = "\n".join(block)
        task_id = match.group("id")
        if task_id in seen:
            raise FeatureStateError(f"duplicate task id in tasks.md: {task_id}")
        seen.add(task_id)
        title = (match.group("title") or "").strip()
        title = title.split(" — ", 1)[0].strip().strip("*").strip()
        dependency_text = (
            block_text.split("depends on", 1)[1]
            if "depends on" in block_text
            else ""
        )
        tasks.append(
            {
                "id": task_id,
                "title": title or task_id,
                "checked": match.group("checked").lower() == "x",
                "workstream": workstream,
                "acs": expand_acceptance_criteria(block_text),
                "declared_deps": sorted(
                    item
                    for item in set(TASK_ID_PATTERN.findall(dependency_text))
                    if not item.startswith("AC-")
                ),
            }
        )
        index = cursor
    return tasks


def _recovery_workstream_id(index: int) -> str:
    return f"WS-RECOVERED-{index:02d}"


def rebuild_coordination_skeleton(feature_dir: Path) -> list[str]:
    """Rebuild conservative graphs from human docs when `_kapelle/` was deleted."""
    internal = feature_dir / "_kapelle"
    internal.mkdir(parents=True, exist_ok=True)
    gaps: list[str] = []
    surface_path = internal / "surface-plan.json"
    task_plan_path = internal / "task-plan.json"

    if (feature_dir / "design.md").is_file() and not surface_path.is_file():
        atomic_write_json(
            surface_path,
            {
                "slug": feature_dir.name,
                "aspects": [
                    {
                        "id": "recovered-scope",
                        "intent": "Conservative scope recovered from design.md; refresh with project architecture guidance before implementation",
                        "modules": [],
                        "entrypoints": [],
                        "depends_on": [],
                    }
                ],
                "contracts": [],
                "integration_checks": [],
            },
        )
        gaps.append("exact aspect, contract, and integration topology")

    parsed = parse_tasks(feature_dir / "tasks.md")
    if parsed and surface_path.is_file() and not task_plan_path.is_file():
        grouped: OrderedDict[str, list[dict[str, Any]]] = OrderedDict()
        for task in parsed:
            grouped.setdefault(task["workstream"], []).append(task)
        known_ids = {task["id"] for task in parsed}
        workstreams: list[dict[str, Any]] = []
        tasks: list[dict[str, Any]] = []
        previous_completion: str | None = None
        for index, (title, grouped_tasks) in enumerate(grouped.items(), 1):
            workstream_id = _recovery_workstream_id(index)
            completion = grouped_tasks[-1]["id"]
            workstreams.append(
                {
                    "id": workstream_id,
                    "title": title,
                    "intent": f"Recover the documented outcome for {title}",
                    "aspects": ["recovered-scope"],
                    "depends_on": (
                        [_recovery_workstream_id(index - 1)] if index > 1 else []
                    ),
                    "completion_task_id": completion,
                    "completion_signal": f"All documented tasks in {title} are reconciled and validated",
                }
            )
            group_ids = [task["id"] for task in grouped_tasks]
            for task in grouped_tasks:
                deps = [
                    item
                    for item in task["declared_deps"]
                    if item in known_ids and item != task["id"]
                ]
                if previous_completion and previous_completion not in deps:
                    deps.append(previous_completion)
                if task["id"] == completion:
                    deps.extend(
                        item for item in group_ids if item != completion and item not in deps
                    )
                status = "implemented-unverified" if task["checked"] else "pending"
                tasks.append(
                    {
                        "id": task["id"],
                        "title": task["title"],
                        "intent": task["title"],
                        "workstream_id": workstream_id,
                        "deps": deps,
                        "acs": task["acs"],
                        "dod": "Reconcile the documented outcome with current code and obtain required validation",
                        "module_hint": None,
                        "primary_aspect": "recovered-scope",
                        "aspects": ["recovered-scope"],
                        "entrypoint_hint": None,
                        "provides_contracts": [],
                        "consumes_contracts": [],
                        "integration_checks": [],
                        "validation": [
                            {
                                "kind": "inspection",
                                "procedure": "Reconcile current implementation and run project-defined validation",
                                "expected": "Documented behavior and current implementation agree",
                            }
                        ],
                        "risk": "medium",
                        "parallel_candidate": False,
                        "ownership_status": "unknown",
                        "files_hint": [],
                        "status": status,
                    }
                )
            previous_completion = completion

        spec_acs = set(AC_PATTERN.findall((feature_dir / "spec.md").read_text()))
        covered = {ac for task in tasks for ac in task["acs"]}
        if tasks and spec_acs - covered:
            gaps.append("exact acceptance-criterion ownership")
        atomic_write_json(
            task_plan_path,
            {
                "slug": feature_dir.name,
                "decomposition_depth": "standard",
                "architecture_guidance_path": "_kapelle/architecture-guidance/recovery.json",
                "workstreams": workstreams,
                "tasks": tasks,
                "split_recommendations": [],
                "recovery": {
                    "status": "recovered-with-gaps",
                    "requires_architecture_refresh": True,
                },
            },
        )
        gaps.extend(
            [
                "exact task dependency and file-ownership topology",
                "current scoped architecture guidance",
            ]
        )
    return sorted(set(gaps))


def _fingerprints_match(
    claimed: Any,
    current: dict[str, str | None],
) -> bool:
    if not isinstance(claimed, dict) or not claimed:
        return False
    for name, digest in claimed.items():
        if name not in current or digest is None or current[name] != digest:
            return False
    return True


def _project_root(feature_dir: Path) -> Path:
    if (
        feature_dir.parent.name == "features"
        and feature_dir.parent.parent.name == "docs"
    ):
        return feature_dir.parent.parent.parent
    return feature_dir


def _implementation_fingerprints_match(feature_dir: Path, claimed: Any) -> bool:
    if not isinstance(claimed, dict) or not claimed:
        return False
    root = _project_root(feature_dir).resolve()
    for relative, digest in claimed.items():
        if not isinstance(relative, str) or not isinstance(digest, str):
            return False
        path = (root / relative).resolve()
        try:
            path.relative_to(root)
        except ValueError:
            return False
        if file_fingerprint(path) != digest:
            return False
    return True


def _exact_keys(value: dict[str, Any], required: set[str]) -> bool:
    return set(value) == required


def validation_evidence_status(feature_dir: Path, evidence: Any) -> str | None:
    required_keys = {
        "task_id",
        "policy",
        "decision",
        "commands",
        "input_fingerprints",
        "implementation_fingerprints",
    }
    if not isinstance(evidence, dict) or not _exact_keys(evidence, required_keys):
        return None
    if not isinstance(evidence.get("task_id"), str) or not evidence["task_id"]:
        return None
    if evidence.get("policy") not in {"ask", "allow", "skip"}:
        return None
    if evidence.get("decision") not in {
        "run-all",
        "run-selected",
        "skip-all",
        "cancelled",
    }:
        return None
    commands = evidence.get("commands")
    if not isinstance(commands, list) or not commands:
        return None
    allowed_command_keys = {
        "command",
        "kind",
        "scope",
        "required",
        "status",
        "reason",
    }
    for command in commands:
        if (
            not isinstance(command, dict)
            or not {"command", "kind", "scope", "required", "status"}.issubset(
                command
            )
            or not set(command).issubset(allowed_command_keys)
            or command.get("kind")
            not in {"tests", "static-analysis", "lint", "build", "other"}
            or command.get("status")
            not in {"passed", "failed", "skipped", "cancelled"}
            or not isinstance(command.get("required"), bool)
        ):
            return None
        if command["status"] in {"skipped", "cancelled"} and not command.get(
            "reason"
        ):
            return None

    current_inputs = input_fingerprints(feature_dir)
    claimed_inputs = evidence.get("input_fingerprints")
    implementation_fingerprints = evidence.get("implementation_fingerprints")
    if (
        not isinstance(claimed_inputs, dict)
        or set(claimed_inputs) != set(current_inputs)
        or not _fingerprints_match(claimed_inputs, current_inputs)
        or not _implementation_fingerprints_match(
            feature_dir, implementation_fingerprints
        )
    ):
        return None
    task_plan = read_json(feature_dir / "_kapelle" / "task-plan.json")
    planned_task = next(
        (
            item
            for item in (task_plan or {}).get("tasks", [])
            if isinstance(item, dict) and item.get("id") == evidence["task_id"]
        ),
        None,
    )
    if not planned_task:
        return None
    claimed_paths = {
        str(Path(path).as_posix()).removeprefix("./").rstrip("/")
        for path in implementation_fingerprints
    }
    root = _project_root(feature_dir).resolve()
    for hint in planned_task.get("files_hint", []):
        hint_value = Path(hint)
        if hint_value.is_absolute() or ".." in hint_value.parts:
            return None
        normalized = str(hint_value.as_posix()).removeprefix("./").rstrip("/")
        hinted_path = (root / normalized).resolve()
        try:
            hinted_path.relative_to(root)
        except ValueError:
            return None
        if hinted_path.is_dir():
            required_paths = set()
            for path in hinted_path.rglob("*"):
                if not path.is_file():
                    continue
                resolved = path.resolve()
                try:
                    required_paths.add(str(resolved.relative_to(root).as_posix()))
                except ValueError:
                    return None
        else:
            required_paths = {normalized}
        if not required_paths or not required_paths.issubset(claimed_paths):
            return None

    required_commands = [item for item in commands if item["required"]]
    if any(item["status"] == "failed" for item in required_commands):
        return "blocked"
    if any(
        item["status"] in {"skipped", "cancelled"} for item in required_commands
    ):
        return "validation-deferred"
    if required_commands and all(
        item["status"] == "passed" for item in required_commands
    ):
        return "completed"
    return None


def validation_statuses(
    feature_dir: Path,
    fingerprints: dict[str, str | None],
) -> dict[str, str]:
    del fingerprints  # retained for the public helper signature
    statuses: dict[str, str] = {}
    validation_dir = feature_dir / "_kapelle" / "validation"
    if not validation_dir.is_dir():
        return statuses
    for path in sorted(validation_dir.glob("*.json")):
        evidence = read_json(path)
        status = validation_evidence_status(feature_dir, evidence)
        if status and isinstance(evidence.get("task_id"), str):
            statuses[evidence["task_id"]] = status
    return statuses


def _review_inputs_current(feature_dir: Path, evidence: dict[str, Any]) -> bool:
    current = input_fingerprints(feature_dir)
    claimed = evidence.get("input_fingerprints")
    return bool(
        isinstance(claimed, dict)
        and set(claimed) == set(current)
        and _fingerprints_match(claimed, current)
    )


def documentation_convergence_current(
    feature_dir: Path, task_states: dict[str, str] | None = None
) -> bool:
    evidence = read_json(
        feature_dir / "_kapelle" / "reviews" / "documentation-convergence.json"
    )
    required = {
        "status",
        "revision",
        "input_fingerprints",
        "implementation_fingerprints",
        "requirement_mismatches",
        "design_mismatches",
        "contract_mismatches",
        "undocumented_decisions",
        "unresolved_deferrals",
    }
    mismatch_fields = (
        "requirement_mismatches",
        "design_mismatches",
        "contract_mismatches",
        "undocumented_decisions",
        "unresolved_deferrals",
    )
    if not (
        evidence
        and _exact_keys(evidence, required)
        and evidence.get("status") == "PASS"
        and _review_inputs_current(feature_dir, evidence)
        and _implementation_fingerprints_match(
            feature_dir, evidence.get("implementation_fingerprints")
        )
        and all(evidence.get(field) == [] for field in mismatch_fields)
    ):
        return False
    expected_tasks = {
        task_id
        for task_id, status in (task_states or {}).items()
        if status == "completed"
    }
    validation_inventory: dict[str, str] = {}
    validated_tasks: set[str] = set()
    validation_dir = feature_dir / "_kapelle" / "validation"
    for path in sorted(validation_dir.glob("*.json")):
        item = read_json(path)
        if validation_evidence_status(feature_dir, item) != "completed":
            continue
        validated_tasks.add(item["task_id"])
        for implementation_path, digest in item["implementation_fingerprints"].items():
            previous = validation_inventory.get(implementation_path)
            if previous is not None and previous != digest:
                return False
            validation_inventory[implementation_path] = digest
    return bool(
        validation_inventory
        and (not task_states or validated_tasks == expected_tasks)
        and evidence["implementation_fingerprints"] == validation_inventory
    )


def feature_review_current(
    feature_dir: Path, task_states: dict[str, str]
) -> bool:
    evidence = read_json(feature_dir / "_kapelle" / "reviews" / "feature-review.json")
    required = {
        "status",
        "summary",
        "input_fingerprints",
        "validation_files",
        "reviewed_aspects",
        "findings",
    }
    if not (
        evidence
        and _exact_keys(evidence, required)
        and evidence.get("status") == "PASS"
        and isinstance(evidence.get("summary"), str)
        and evidence["summary"].strip()
        and _review_inputs_current(feature_dir, evidence)
        and isinstance(evidence.get("reviewed_aspects"), list)
        and evidence["reviewed_aspects"]
        and evidence.get("findings") == []
    ):
        return False
    surface = read_json(feature_dir / "_kapelle" / "surface-plan.json")
    expected_aspects = {
        item.get("id")
        for item in (surface or {}).get("aspects", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    if set(evidence["reviewed_aspects"]) != expected_aspects:
        return False
    validation_files = evidence.get("validation_files")
    if not isinstance(validation_files, list) or len(validation_files) != len(
        set(validation_files)
    ):
        return False
    expected = {
        task_id for task_id, status in task_states.items() if status == "completed"
    }
    reviewed: set[str] = set()
    for relative in validation_files:
        if not isinstance(relative, str):
            return False
        path = (feature_dir / relative).resolve()
        try:
            path.relative_to(feature_dir.resolve())
        except ValueError:
            return False
        item = read_json(path)
        if validation_evidence_status(feature_dir, item) != "completed":
            return False
        reviewed.add(item["task_id"])
    return reviewed == expected


def change_state_error(value: Any, change_id: str) -> str | None:
    required = {
        "change_id",
        "current_revision",
        "state",
        "paused_task",
        "reason",
    }
    allowed = required | {"checkpoint_evidence"}
    if not isinstance(value, dict):
        return "invalid JSON object"
    if not required.issubset(value) or not set(value).issubset(allowed):
        return "invalid fields"
    if value.get("change_id") != change_id:
        return "change_id mismatch"
    if (
        not isinstance(value.get("current_revision"), int)
        or value["current_revision"] < 1
    ):
        return "invalid current_revision"
    if value.get("state") not in {
        "running",
        "paused",
        "reconciling",
        "waiting-approval",
        "approved",
        "resumable",
        "blocked",
        "completed",
    }:
        return "invalid state"
    if value.get("paused_task") is not None and not isinstance(
        value.get("paused_task"), str
    ):
        return "invalid paused_task"
    if not isinstance(value.get("reason"), str):
        return "invalid reason"
    checkpoint = value.get("checkpoint_evidence", [])
    if not isinstance(checkpoint, list) or not all(
        isinstance(item, str) and item for item in checkpoint
    ):
        return "invalid checkpoint_evidence"
    return None


def find_active_change(feature_dir: Path) -> tuple[str | None, str | None]:
    changes = feature_dir / "_kapelle" / "changes"
    if not changes.is_dir():
        return None, None
    for state_path in sorted(changes.glob("*/state.json")):
        state = read_json(state_path)
        if change_state_error(state, state_path.parent.name):
            return state_path.parent.name, None
        if state.get("state") == "completed":
            continue
        revision = state.get("current_revision")
        rendered = f"r{revision:03d}" if isinstance(revision, int) else None
        return state_path.parent.name, rendered
    return None, None


def choose_next_command(
    slug: str,
    feature_dir: Path,
    task_states: dict[str, str],
    convergence_current: bool,
    review_current: bool,
) -> tuple[str, str]:
    if not (feature_dir / "proposal.md").is_file() or not (feature_dir / "spec.md").is_file():
        return "specify", f"/kapelle:specify {slug}"
    if not (feature_dir / "design.md").is_file():
        return "design", f"/kapelle:design {slug}"
    surface_errors, task_plan_errors, provisional = coordination_integrity(feature_dir)
    if surface_errors:
        return "design", f"/kapelle:design {slug}"
    if (
        not (feature_dir / "tasks.md").is_file()
        or (task_plan_errors and not provisional)
    ):
        return "decompose", f"/kapelle:decompose {slug}"
    if not (feature_dir / "test-plan.md").is_file():
        return "plan-tests", f"/kapelle:plan-tests {slug}"

    states = set(task_states.values())
    if provisional and states & {
        "pending",
        "in-progress",
        "blocked",
        "needs-rework",
        "stale",
        "unknown",
    }:
        return "decompose", f"/kapelle:decompose {slug}"
    if states & {"pending", "in-progress", "blocked", "needs-rework", "stale", "unknown"}:
        return "implement", f"/kapelle:implement {slug}"
    if states & {"implemented-unverified", "validation-deferred"}:
        return "validation", f"/kapelle:implement {slug} --validation=ask"
    if provisional:
        return "decompose", f"/kapelle:decompose {slug}"
    if not convergence_current or not review_current:
        return "feature-review", f"/kapelle:feature-review {slug}"
    return "ship", f"/kapelle:ship {slug}"


def coordination_integrity(feature_dir: Path) -> tuple[list[str], list[str], bool]:
    surface_path = feature_dir / "_kapelle" / "surface-plan.json"
    task_path = feature_dir / "_kapelle" / "task-plan.json"
    surface = read_json(surface_path)
    task_plan = read_json(task_path)
    surface_errors: list[str] = []
    task_errors: list[str] = []
    if not surface:
        surface_errors.append("missing or invalid _kapelle/surface-plan.json")
    else:
        if surface.get("slug") != feature_dir.name:
            surface_errors.append("surface plan slug mismatch")
        for field in ("aspects", "contracts", "integration_checks"):
            if not isinstance(surface.get(field), list):
                surface_errors.append(f"surface plan {field} must be an array")
        aspects = surface.get("aspects")
        if isinstance(aspects, list):
            if not aspects:
                surface_errors.append("surface plan aspects must be non-empty")
            aspect_ids = [
                item.get("id")
                for item in aspects
                if isinstance(item, dict) and isinstance(item.get("id"), str)
            ]
            if len(aspect_ids) != len(aspects):
                surface_errors.append("surface plan aspect has missing id")
            elif len(aspect_ids) != len(set(aspect_ids)):
                surface_errors.append("surface plan has duplicate aspect ids")
    if not task_plan:
        task_errors.append("missing or invalid _kapelle/task-plan.json")
    elif not surface_errors and (feature_dir / "spec.md").is_file():
        try:
            task_errors.extend(
                validate_task_plan(task_path, surface_path, feature_dir / "spec.md")
            )
        except (ValueError, OSError, json.JSONDecodeError) as exc:
            task_errors.append(str(exc))
    provisional = bool(
        task_plan
        and isinstance(task_plan.get("recovery"), dict)
        and task_plan["recovery"].get("requires_architecture_refresh") is True
    )
    return surface_errors, task_errors, provisional


def derive_state(
    feature_dir: Path,
    *,
    recovery_status: str,
    previous_state: dict[str, Any] | None = None,
    evidence_gaps: list[str] | None = None,
) -> dict[str, Any]:
    slug = feature_dir.name
    fingerprints = document_fingerprints(feature_dir)
    parsed_tasks = parse_tasks(feature_dir / "tasks.md")
    evidence = validation_statuses(feature_dir, fingerprints)
    previous_tasks = (previous_state or {}).get("tasks", {})
    previous_fingerprints = (previous_state or {}).get("document_fingerprints", {})
    preserve_previous = previous_fingerprints.get("tasks.md") == fingerprints.get("tasks.md")

    task_states: OrderedDict[str, str] = OrderedDict()
    for task in parsed_tasks:
        task_id = task["id"]
        if task_id in evidence:
            status = evidence[task_id]
        elif preserve_previous and previous_tasks.get(task_id) in {
            "in-progress",
            "blocked",
            "validation-deferred",
            "stale",
            "needs-rework",
            "superseded",
            "unknown",
        }:
            status = previous_tasks[task_id]
        elif task["checked"]:
            status = "implemented-unverified"
        else:
            status = "pending"
        task_states[task_id] = status

    counts = Counter(task_states.values())
    task_counts = {"total": len(task_states)}
    task_counts.update({key: counts[key] for key in sorted(counts)})
    deferred = sorted(
        task_id for task_id, status in task_states.items() if status == "validation-deferred"
    )
    blockers = sorted(
        task_id
        for task_id, status in task_states.items()
        if status in {"blocked", "needs-rework", "stale", "unknown"}
    )

    convergence_current = documentation_convergence_current(feature_dir, task_states)
    review_current = feature_review_current(feature_dir, task_states)

    current_stage, next_command = choose_next_command(
        slug, feature_dir, task_states, convergence_current, review_current
    )
    incomplete = {
        task_id
        for task_id, status in task_states.items()
        if status not in {"completed", "superseded"}
    }
    complete_human_package = all((feature_dir / name).is_file() for name in HUMAN_ARTIFACTS)
    review_ready = (
        bool(task_states)
        and complete_human_package
        and not incomplete
        and not blockers
        and not deferred
    )
    active_change, revision = find_active_change(feature_dir)
    ship_ready = (
        review_ready
        and convergence_current
        and review_current
        and active_change is None
    )

    gaps = sorted(set(evidence_gaps or (previous_state or {}).get("evidence_gaps", [])))
    if blockers:
        feature_state = "blocked"
    elif deferred:
        feature_state = "validation-deferred"
    elif any(status == "implemented-unverified" for status in task_states.values()):
        feature_state = "externally-implemented-unverified"
    elif ship_ready:
        feature_state = "ship-ready"
    elif review_ready:
        feature_state = "review-ready"
    elif recovery_status == "recovered-with-gaps":
        feature_state = "recovered-with-gaps"
    elif recovery_status == "recovered":
        feature_state = "recovered"
    elif task_states:
        feature_state = "implementation"
    else:
        feature_state = "planning"

    return {
        "layout_version": LAYOUT_VERSION,
        "slug": slug,
        "feature_state": feature_state,
        "current_stage": current_stage,
        "active_change": active_change,
        "revision": revision,
        "task_counts": task_counts,
        "tasks": dict(task_states),
        "blockers": blockers,
        "deferred_validation": deferred,
        "evidence_gaps": gaps,
        "review_ready": review_ready,
        "ship_ready": ship_ready,
        "documentation_convergence": (
            "current-pass" if convergence_current else "missing-or-stale"
        ),
        "feature_review": "current-pass" if review_current else "missing-or-stale",
        "next_command": next_command,
        "document_fingerprints": fingerprints,
        "recovery_status": recovery_status,
    }


def build_manifest(
    feature_dir: Path,
    state: dict[str, Any],
    *,
    mode: str,
    evidence_loss: list[str],
) -> dict[str, Any]:
    return {
        "layout_version": LAYOUT_VERSION,
        "schema_version": SCHEMA_VERSION,
        "slug": feature_dir.name,
        "human_artifacts": artifact_manifest(
            feature_dir, state["document_fingerprints"]
        ),
        "recovery": {
            "mode": mode,
            "evidence_loss": sorted(set(evidence_loss)),
        },
        "state_built_at": utc_now(),
    }


def sync_task_plan_statuses(feature_dir: Path, state: dict[str, Any]) -> None:
    task_plan_path = feature_dir / "_kapelle" / "task-plan.json"
    task_plan = read_json(task_plan_path)
    if not task_plan or not isinstance(task_plan.get("tasks"), list):
        return
    changed = False
    for task in task_plan["tasks"]:
        task_id = task.get("id")
        expected = state.get("tasks", {}).get(task_id)
        if expected and task.get("status") != expected:
            task["status"] = expected
            changed = True
    if changed:
        atomic_write_json(task_plan_path, task_plan)


def extract_section(path: Path, heading: str) -> str | None:
    if not path.is_file():
        return None
    lines = path.read_text(errors="replace").splitlines()
    target = f"## {heading}".lower()
    capture: list[str] = []
    active = False
    for line in lines:
        if line.lower() == target:
            active = True
            continue
        if active and line.startswith("## "):
            break
        if active and line.strip():
            capture.append(line.strip())
    return " ".join(capture[:3]) if capture else None


def feature_title(feature_dir: Path) -> str:
    for name in ("proposal.md", "spec.md", "design.md"):
        path = feature_dir / name
        if not path.is_file():
            continue
        for line in path.read_text(errors="replace").splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    return feature_dir.name.replace("-", " ").title()


def render_status(feature_dir: Path, state: dict[str, Any]) -> str:
    tasks = parse_tasks(feature_dir / "tasks.md")
    groups: OrderedDict[str, list[dict[str, Any]]] = OrderedDict()
    for task in tasks:
        groups.setdefault(task["workstream"], []).append(task)
    labels = {
        "planning": "Planning",
        "implementation": "Implementation",
        "validation-deferred": "Validation deferred",
        "review-ready": "Ready for feature review",
        "ship-ready": "Ready to ship",
        "recovered": "Recovered",
        "recovered-with-gaps": "Recovered with gaps",
        "external-development": "External development",
        "externally-implemented-unverified": "Implemented, validation required",
        "blocked": "Blocked",
        "shipped": "Shipped",
    }
    counts = state.get("task_counts", {})
    lines = [
        "<!-- generated by Kapelle; do not edit -->",
        f"# {feature_title(feature_dir)}",
        "",
        f"Status: {labels.get(state.get('feature_state'), state.get('feature_state', 'Unknown'))}",
        f"Current stage: {state.get('current_stage', 'unknown')}",
        (
            f"Progress: {counts.get('completed', 0)}/{counts.get('total', 0)} validated; "
            f"{counts.get('implemented-unverified', 0)} implemented-unverified"
        ),
        f"Ready for review: {'Yes' if state.get('review_ready') else 'No'}",
        f"Ready to ship: {'Yes' if state.get('ship_ready') else 'No'}",
    ]
    if state.get("active_change"):
        lines.append(
            f"Active change: {state['active_change']}"
            + (f", revision {state['revision']}" if state.get("revision") else "")
        )
    summary = extract_section(feature_dir / "proposal.md", "Summary")
    if summary:
        lines.extend(["", "## Scope", "", summary])
    if groups:
        lines.extend(
            [
                "",
                "## Workstreams",
                "",
                "| Workstream | Validated | Unverified | Remaining |",
                "|---|---:|---:|---:|",
            ]
        )
        state_tasks = state.get("tasks", {})
        for workstream, grouped in groups.items():
            statuses = [state_tasks.get(item["id"], "unknown") for item in grouped]
            validated = statuses.count("completed")
            unverified = statuses.count("implemented-unverified")
            remaining = len(statuses) - validated - unverified - statuses.count("superseded")
            lines.append(f"| {workstream} | {validated} | {unverified} | {remaining} |")
    if state.get("blockers"):
        lines.extend(["", "## Blockers", ""])
        titles = {task["id"]: task["title"] for task in tasks}
        lines.extend(
            f"- {item} — {titles[item]}" if item in titles else f"- {item}"
            for item in state["blockers"]
        )
    if state.get("deferred_validation"):
        lines.extend(["", "## Deferred validation", ""])
        titles = {task["id"]: task["title"] for task in tasks}
        lines.extend(
            f"- {item} — {titles[item]}" if item in titles else f"- {item}"
            for item in state["deferred_validation"]
        )
    if state.get("evidence_gaps"):
        lines.extend(["", "## Evidence unavailable", ""])
        lines.extend(f"- {item}" for item in state["evidence_gaps"])
    lines.extend(
        [
            "",
            "## Documentation readiness",
            "",
            "- Product specification: Current"
            if (feature_dir / "spec.md").is_file()
            else "- Product specification: Missing",
            "- Technical specification: Current"
            if (feature_dir / "design.md").is_file()
            else "- Technical specification: Missing",
            (
                "- As-built convergence: PASS"
                if state.get("documentation_convergence") == "current-pass"
                else "- As-built convergence: Missing or stale"
            ),
            (
                "- Feature review: PASS"
                if state.get("feature_review") == "current-pass"
                else "- Feature review: Missing or stale"
            ),
        ]
    )
    lines.extend(
        [
            "",
            "## Review now",
            "",
            "- proposal.md",
            "- spec.md",
            "- design.md",
            "- tasks.md",
            "- test-plan.md",
            "",
            "## Next action",
            "",
            state.get("next_command", f"/kapelle:status {feature_dir.name}"),
            "",
        ]
    )
    return "\n".join(lines)


def rebuild_feature_state(
    feature_dir: Path,
    *,
    mode: str = "recovered",
    evidence_loss: list[str] | None = None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    feature_dir = resolve_feature_dir(feature_dir)
    coordination_gaps = rebuild_coordination_skeleton(feature_dir)
    gaps = list(evidence_loss if evidence_loss is not None else EVIDENCE_LOSS)
    gaps.extend(coordination_gaps)
    recovery_status = (
        "migrated"
        if mode == "migrated"
        else "recovered-with-gaps"
        if gaps
        else "recovered"
    )
    state = derive_state(
        feature_dir,
        recovery_status=recovery_status,
        evidence_gaps=gaps,
    )
    manifest = build_manifest(feature_dir, state, mode=mode, evidence_loss=gaps)
    sync_task_plan_statuses(feature_dir, state)
    dispositions = {
        task_id: (
            "not-started"
            if status == "pending"
            else "validated"
            if status == "completed"
            else status
            if status
            in {
                "implemented-unverified",
                "needs-rework",
                "superseded",
                "unknown",
            }
            else "unknown"
        )
        for task_id, status in state["tasks"].items()
    }
    recovered = [
        name for name in HUMAN_ARTIFACTS if (feature_dir / name).is_file()
    ]
    report = {
        "layout_version": LAYOUT_VERSION,
        "slug": feature_dir.name,
        "status": "recovered-with-gaps" if gaps else "recovered",
        "recovered": recovered,
        "evidence_unavailable": gaps,
        "task_dispositions": dispositions,
        "next_command": state["next_command"],
    }
    internal = feature_dir / "_kapelle"
    atomic_write_json(internal / "manifest.json", manifest)
    atomic_write_json(internal / "state.json", state)
    atomic_write_json(internal / "recovery.json", report)
    atomic_write_text(feature_dir / "STATUS.md", render_status(feature_dir, state))
    return manifest, state, report


def initialize_feature_state(
    feature_dir: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Initialize a new feature without claiming an evidence-loss recovery."""
    feature_dir = resolve_feature_dir(feature_dir)
    state = derive_state(
        feature_dir,
        recovery_status="native",
        evidence_gaps=[],
    )
    manifest = build_manifest(feature_dir, state, mode="native", evidence_loss=[])
    sync_task_plan_statuses(feature_dir, state)
    internal = feature_dir / "_kapelle"
    atomic_write_json(internal / "manifest.json", manifest)
    atomic_write_json(internal / "state.json", state)
    recovery_path = internal / "recovery.json"
    if recovery_path.exists():
        recovery_path.unlink()
    atomic_write_text(feature_dir / "STATUS.md", render_status(feature_dir, state))
    return manifest, state


def refresh_feature_status(feature_dir: Path) -> tuple[dict[str, Any], dict[str, Any], bool]:
    feature_dir = resolve_feature_dir(feature_dir)
    internal = feature_dir / "_kapelle"
    manifest = read_json(internal / "manifest.json")
    previous_state = read_json(internal / "state.json")
    valid = bool(
        manifest
        and previous_state
        and manifest.get("layout_version") == LAYOUT_VERSION
        and manifest.get("slug") == feature_dir.name
    )
    if not valid:
        rebuilt_manifest, rebuilt_state, _ = rebuild_feature_state(feature_dir)
        return rebuilt_manifest, rebuilt_state, True

    mode = manifest.get("recovery", {}).get("mode", "native")
    gaps = manifest.get("recovery", {}).get("evidence_loss", [])
    recovery_status = previous_state.get("recovery_status", "native")
    state = derive_state(
        feature_dir,
        recovery_status=recovery_status,
        previous_state=previous_state,
        evidence_gaps=gaps,
    )
    refreshed_manifest = build_manifest(feature_dir, state, mode=mode, evidence_loss=gaps)
    sync_task_plan_statuses(feature_dir, state)
    atomic_write_json(internal / "manifest.json", refreshed_manifest)
    atomic_write_json(internal / "state.json", state)
    atomic_write_text(feature_dir / "STATUS.md", render_status(feature_dir, state))
    return refreshed_manifest, state, False
