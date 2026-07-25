#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from feature_state import (
    HUMAN_ARTIFACTS,
    LAYOUT_VERSION,
    choose_next_command,
    change_state_error,
    coordination_integrity,
    documentation_convergence_current,
    document_fingerprints,
    feature_review_current,
    human_controlled_workflow,
    reconstruction_review_current,
    reconstruction_workflow,
    parse_tasks,
    phase_evidence_current,
    read_json,
    release_current,
    render_status,
    resolve_feature_dir,
    schema_errors,
    validation_statuses,
)
from jsonschema_lite import validate_jsonl_file
from validate_design import validate as validate_design


def validate(feature_dir: Path) -> list[str]:
    errors: list[str] = []
    internal = feature_dir / "_kapelle"
    manifest = read_json(internal / "manifest.json")
    state = read_json(internal / "state.json")
    if not manifest:
        return ["missing or invalid _kapelle/manifest.json"]
    if not state:
        return ["missing or invalid _kapelle/state.json"]
    errors.extend(
        f"manifest schema: {item}"
        for item in schema_errors(manifest, "feature-manifest.schema.json")
    )
    errors.extend(
        f"state schema: {item}"
        for item in schema_errors(state, "feature-state.schema.json")
    )
    optional_artifacts = {
        "workflow.json": "workflow-state.schema.json",
        "size.json": "size.schema.json",
        "surface-plan.json": "surface-plan.schema.json",
        "task-plan.json": "task-plan.schema.json",
        "decomposition-review.json": "decomposition-review.schema.json",
        "reconstruction.json": "reconstruction.schema.json",
        "reconstruction-coverage.json": "reconstruction-coverage.schema.json",
        "base-functional-tests.json": "base-functional-tests.schema.json",
        "unit-tests.json": "unit-test-run.schema.json",
        "verification.json": "verification.schema.json",
        "release.json": "release.schema.json",
        "recovery.json": "recovery-report.schema.json",
    }
    for filename, schema_name in optional_artifacts.items():
        path = internal / filename
        if not path.is_file():
            continue
        value = read_json(path)
        if value is None:
            errors.append(f"{filename}: invalid JSON object")
            continue
        errors.extend(
            f"{filename} schema: {item}"
            for item in schema_errors(value, schema_name)
        )
    structured_patterns = {
        "architecture-guidance/*.json": "architecture-guidance.schema.json",
        "validation/*.json": "validation-decision.schema.json",
        "changes/*/request.json": "change-request.schema.json",
        "changes/*/reconciliation.json": "reconciliation.schema.json",
        "changes/*/revisions/*/revision.json": "change-revision.schema.json",
        "changes/*/artifacts/*.json": "artifact-state.schema.json",
    }
    for pattern, schema_name in structured_patterns.items():
        for path in sorted(internal.glob(pattern)):
            value = read_json(path)
            relative = path.relative_to(feature_dir)
            if value is None:
                errors.append(f"{relative}: invalid JSON object")
                continue
            errors.extend(
                f"{relative} schema: {item}"
                for item in schema_errors(value, schema_name)
            )
    task_run_components = {
        "task": "task-context.schema.json",
        "architecture_guidance": "architecture-guidance.schema.json",
        "plan": "implementation-plan.schema.json",
        "implementation": "execution-verdict.schema.json",
        "review": "execution-verdict.schema.json",
        "validation": "validation-decision.schema.json",
    }
    for path in sorted((internal / "task-runs").glob("*.json")):
        value = read_json(path)
        relative = path.relative_to(feature_dir)
        if value is None:
            errors.append(f"{relative}: invalid JSON object")
            continue
        for component, schema_name in task_run_components.items():
            if component not in value:
                continue
            errors.extend(
                f"{relative}#{component} schema: {item}"
                for item in schema_errors(value[component], schema_name)
            )
    telemetry = internal / "telemetry" / "execution.jsonl"
    if telemetry.is_file():
        errors.extend(
            f"{telemetry.relative_to(feature_dir)} schema: {item}"
            for item in validate_jsonl_file(
                telemetry,
                Path(__file__).resolve().parent.parent
                / "dispatcher"
                / "execution-telemetry.schema.json",
            )
        )
    approvals_dir = internal / "approvals"
    if approvals_dir.is_dir():
        for path in sorted(approvals_dir.glob("*.json")):
            value = read_json(path)
            if value is None:
                errors.append(f"{path.relative_to(feature_dir)}: invalid JSON object")
                continue
            errors.extend(
                f"{path.relative_to(feature_dir)} schema: {item}"
                for item in schema_errors(value, "review-gate.schema.json")
            )
    if manifest.get("layout_version") != LAYOUT_VERSION:
        errors.append("manifest: unsupported layout_version")
    if state.get("layout_version") != LAYOUT_VERSION:
        errors.append("state: unsupported layout_version")
    if manifest.get("slug") != feature_dir.name or state.get("slug") != feature_dir.name:
        errors.append("slug does not match feature directory")

    fingerprints = document_fingerprints(feature_dir)
    if (
        human_controlled_workflow(feature_dir) or reconstruction_workflow(feature_dir)
    ) and (feature_dir / "design.md").is_file():
        errors.extend(
            f"design structure: {error}"
            for error in validate_design(feature_dir / "design.md")
        )
    manifest_artifacts = manifest.get("human_artifacts", {})
    for name in HUMAN_ARTIFACTS:
        item = manifest_artifacts.get(name, {})
        if item.get("sha256") != fingerprints.get(name):
            errors.append(f"manifest fingerprint drift: {name}")
    if state.get("document_fingerprints") != fingerprints:
        errors.append("state document_fingerprints drift")
    for alias, canonical in {
        "feature-outline.json": "outline.json",
        "business-specification.json": "business-spec.json",
    }.items():
        if (internal / "approvals" / alias).is_file():
            errors.append(
                f"non-canonical approval alias {alias}; canonical path is {canonical}"
            )

    parsed_tasks = parse_tasks(feature_dir / "tasks.md")
    task_ids = [task["id"] for task in parsed_tasks]
    state_tasks = state.get("tasks", {})
    if set(task_ids) != set(state_tasks):
        errors.append("tasks.md and state task ids differ")
    task_plan = read_json(internal / "task-plan.json")
    if parsed_tasks and task_plan:
        plan_tasks = {
            task.get("id"): task
            for task in task_plan.get("tasks", [])
            if isinstance(task, dict) and isinstance(task.get("id"), str)
        }
        if set(plan_tasks) != set(task_ids):
            errors.append("tasks.md and _kapelle/task-plan.json task ids differ")
        workstream_titles = {
            item.get("id"): item.get("title")
            for item in task_plan.get("workstreams", [])
            if isinstance(item, dict)
        }
        for human_task in parsed_tasks:
            task_id = human_task["id"]
            planned = plan_tasks.get(task_id)
            if not planned:
                continue
            if planned.get("title") != human_task["title"]:
                errors.append(f"task {task_id}: title drift between tasks.md and task plan")
            expected_workstream = workstream_titles.get(planned.get("workstream_id"))
            if expected_workstream and expected_workstream != human_task["workstream"]:
                errors.append(
                    f"task {task_id}: workstream drift between tasks.md and task plan"
                )
            if planned.get("status") != state_tasks.get(task_id):
                errors.append(f"task {task_id}: state drift between task plan and feature state")
    surface_errors, task_plan_errors, provisional = coordination_integrity(feature_dir)
    if (feature_dir / "design.md").is_file():
        errors.extend(f"coordination: {error}" for error in surface_errors)
    if (
        not reconstruction_workflow(feature_dir)
        and (
            (feature_dir / "tasks.md").is_file()
            or (internal / "task-plan.json").is_file()
        )
        and task_plan_errors
        and not provisional
    ):
        errors.extend(f"coordination: {error}" for error in task_plan_errors)
    counts = Counter(state_tasks.values())
    expected_counts: dict[str, Any] = {"total": len(state_tasks)}
    expected_counts.update({key: counts[key] for key in sorted(counts)})
    if state.get("task_counts") != expected_counts:
        errors.append("task_counts do not match state tasks")

    validation = validation_statuses(feature_dir, fingerprints)
    for task_id, status in state_tasks.items():
        if status == "completed" and validation.get(task_id) != "completed":
            errors.append(f"task {task_id}: completed without current PASS evidence")

    if reconstruction_workflow(feature_dir):
        convergence_current = reconstruction_review_current(feature_dir)
        review_current = convergence_current
    else:
        convergence_current = documentation_convergence_current(feature_dir, state_tasks)
        review_current = feature_review_current(feature_dir, state_tasks)
    stage, next_command = choose_next_command(
        feature_dir.name, feature_dir, state_tasks, convergence_current, review_current
    )
    if state.get("current_stage") != stage:
        errors.append(f"current_stage drift: expected {stage}")
    if state.get("next_command") != next_command:
        errors.append(f"next_command drift: expected {next_command}")

    incomplete = {
        task_id
        for task_id, status in state_tasks.items()
        if status not in {"completed", "superseded"}
    }
    blockers = state.get("blockers", [])
    deferred = state.get("deferred_validation", [])
    if reconstruction_workflow(feature_dir):
        expected_review_ready = reconstruction_review_current(feature_dir)
    elif human_controlled_workflow(feature_dir):
        expected_review_ready = phase_evidence_current(
            feature_dir, "verification.json", {"PASS"}
        ) and not incomplete
    else:
        expected_review_ready = False
    if state.get("review_ready") != expected_review_ready:
        errors.append("review_ready is inconsistent with tasks/blockers/validation")
    if human_controlled_workflow(feature_dir):
        expected_ship_ready = (
            release_current(feature_dir)
            and not incomplete
            and not blockers
            and not deferred
            and state.get("active_change") is None
        )
    else:
        expected_ship_ready = False
    if state.get("ship_ready") != expected_ship_ready:
        errors.append("ship_ready is inconsistent with current evidence")
    expected_convergence = "current-pass" if convergence_current else "missing-or-stale"
    expected_review = "current-pass" if review_current else "missing-or-stale"
    if state.get("documentation_convergence") != expected_convergence:
        errors.append("documentation_convergence is inconsistent with current evidence")
    if state.get("feature_review") != expected_review:
        errors.append("feature_review is inconsistent with current evidence")
    if state.get("ship_ready") and state.get("active_change"):
        errors.append("active change and ship_ready cannot both be current")
    changes_dir = internal / "changes"
    if changes_dir.is_dir():
        for state_path in sorted(changes_dir.glob("*/state.json")):
            item = read_json(state_path)
            change_error = change_state_error(item, state_path.parent.name)
            if change_error:
                errors.append(
                    f"invalid change state {state_path.parent.name}: {change_error}"
                )

    if state.get("recovery_status", "").startswith("recovered"):
        report = read_json(internal / "recovery.json")
        if not report:
            errors.append("recovered state requires recovery.json")
        else:
            for task_id, disposition in report.get("task_dispositions", {}).items():
                if disposition == "validated" and validation.get(task_id) != "completed":
                    errors.append(
                        f"recovery report fabricates validation for task {task_id}"
                    )

    status_path = feature_dir / "STATUS.md"
    expected_status = render_status(feature_dir, state)
    if not status_path.is_file():
        errors.append("missing STATUS.md")
    elif status_path.read_text() != expected_status:
        errors.append("STATUS.md drift; rebuild with build_feature_status.py")

    forbidden_root = [
        path.name
        for path in feature_dir.iterdir()
        if path.is_file()
        and (
            path.suffix in {".json", ".jsonl"}
            or path.name in {".size", "ship.md", "sad.md"}
        )
    ]
    if forbidden_root:
        errors.append(f"legacy/internal files in feature root: {sorted(forbidden_root)}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Kapelle layout-v2 feature state")
    parser.add_argument("feature_dir")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    try:
        feature_dir = resolve_feature_dir(args.feature_dir)
        errors = validate(feature_dir)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        errors = [str(exc)]
    if args.as_json:
        print(json.dumps({"valid": not errors, "errors": errors}, indent=2))
    elif errors:
        print(f"FAILED: {len(errors)} feature-state error(s)")
        for error in errors:
            print(f"- {error}")
    else:
        print("PASSED: feature state is consistent")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
