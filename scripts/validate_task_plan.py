#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

AC_PATTERN = re.compile(r"\bAC-[A-Za-z0-9][A-Za-z0-9._-]*\b")


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text())
    except FileNotFoundError:
        raise ValueError(f"missing file: {path}") from None
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from None
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object: {path}")
    return data


def index_unique(items: list[dict[str, Any]], label: str, errors: list[str]) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for item in items:
        item_id = item.get("id")
        if not isinstance(item_id, str) or not item_id:
            errors.append(f"{label}: item has missing id")
            continue
        if item_id in indexed:
            errors.append(f"{label}: duplicate id {item_id}")
            continue
        indexed[item_id] = item
    return indexed


def validate_graph(
    nodes: dict[str, dict[str, Any]],
    dependency_field: str,
    label: str,
    errors: list[str],
) -> None:
    for node_id, node in nodes.items():
        dependencies = node.get(dependency_field, [])
        if not isinstance(dependencies, list):
            errors.append(f"{label} {node_id}: {dependency_field} must be an array")
            continue
        for dependency in dependencies:
            if dependency not in nodes:
                errors.append(f"{label} {node_id}: unknown dependency {dependency}")
            if dependency == node_id:
                errors.append(f"{label} {node_id}: self dependency")

    state: dict[str, int] = {}

    def visit(node_id: str, path: list[str]) -> None:
        if state.get(node_id) == 1:
            errors.append(f"{label}: dependency cycle {' -> '.join(path + [node_id])}")
            return
        if state.get(node_id) == 2:
            return
        state[node_id] = 1
        for dependency in nodes[node_id].get(dependency_field, []):
            if dependency in nodes:
                visit(dependency, path + [node_id])
        state[node_id] = 2

    for node_id in nodes:
        visit(node_id, [])


def transitive_dependencies(
    node_id: str,
    nodes: dict[str, dict[str, Any]],
    dependency_field: str,
) -> set[str]:
    found: set[str] = set()
    stack = list(nodes.get(node_id, {}).get(dependency_field, []))
    while stack:
        dependency = stack.pop()
        if dependency in found or dependency not in nodes:
            continue
        found.add(dependency)
        stack.extend(nodes[dependency].get(dependency_field, []))
    return found


def paths_overlap(left: str, right: str) -> bool:
    left_path = left.replace("\\", "/").strip().removeprefix("./").rstrip("/")
    right_path = right.replace("\\", "/").strip().removeprefix("./").rstrip("/")
    return (
        left_path == right_path
        or left_path.startswith(right_path + "/")
        or right_path.startswith(left_path + "/")
    )


def validate(tasks_path: Path, surface_path: Path, spec_path: Path) -> list[str]:
    errors: list[str] = []
    plan = load_json(tasks_path)
    surface = load_json(surface_path)
    spec_text = spec_path.read_text()

    required_plan_fields = {
        "slug",
        "decomposition_depth",
        "architecture_guidance_path",
        "workstreams",
        "tasks",
    }
    for field in sorted(required_plan_fields - set(plan)):
        errors.append(f"task plan: missing field {field}")

    workstreams_raw = plan.get("workstreams", [])
    tasks_raw = plan.get("tasks", [])
    if not isinstance(workstreams_raw, list) or not workstreams_raw:
        errors.append("task plan: workstreams must be a non-empty array")
        workstreams_raw = []
    if not isinstance(tasks_raw, list) or not tasks_raw:
        errors.append("task plan: tasks must be a non-empty array")
        tasks_raw = []

    workstreams = index_unique(workstreams_raw, "workstream", errors)
    tasks = index_unique(tasks_raw, "task", errors)
    aspects = index_unique(surface.get("aspects", []), "surface aspect", errors)
    contracts = index_unique(surface.get("contracts", []), "surface contract", errors)
    integrations = index_unique(surface.get("integration_checks", []), "integration check", errors)

    validate_graph(workstreams, "depends_on", "workstream", errors)
    validate_graph(tasks, "deps", "task", errors)

    for workstream_id, workstream in workstreams.items():
        workstream_aspects = set(workstream.get("aspects", []))
        unknown_aspects = workstream_aspects - set(aspects)
        if unknown_aspects:
            errors.append(
                f"workstream {workstream_id}: unknown aspects {sorted(unknown_aspects)}"
            )
        if not workstream.get("completion_task_id"):
            errors.append(f"workstream {workstream_id}: missing completion_task_id")
        if not workstream.get("completion_signal"):
            errors.append(f"workstream {workstream_id}: missing completion_signal")

    required_task_fields = {
        "workstream_id",
        "intent",
        "acs",
        "dod",
        "primary_aspect",
        "aspects",
        "provides_contracts",
        "consumes_contracts",
        "integration_checks",
        "validation",
        "risk",
        "parallel_candidate",
        "ownership_status",
        "files_hint",
        "status",
    }

    for task_id, task in tasks.items():
        for field in sorted(required_task_fields - set(task)):
            errors.append(f"task {task_id}: missing field {field}")

        workstream_id = task.get("workstream_id")
        if workstream_id not in workstreams:
            errors.append(f"task {task_id}: unknown workstream {workstream_id}")

        task_aspects = set(task.get("aspects", []))
        unknown_aspects = task_aspects - set(aspects)
        if unknown_aspects:
            errors.append(f"task {task_id}: unknown aspects {sorted(unknown_aspects)}")
        if task.get("primary_aspect") not in task_aspects:
            errors.append(f"task {task_id}: primary_aspect must be included in aspects")
        if workstream_id in workstreams:
            outside_workstream = task_aspects - set(workstreams[workstream_id].get("aspects", []))
            if outside_workstream:
                errors.append(
                    f"task {task_id}: aspects outside workstream {sorted(outside_workstream)}"
                )

        validation = task.get("validation", [])
        if not isinstance(validation, list) or not validation:
            errors.append(f"task {task_id}: validation must be non-empty")

        provides = set(task.get("provides_contracts", []))
        consumes = set(task.get("consumes_contracts", []))
        unknown_contracts = (provides | consumes) - set(contracts)
        if unknown_contracts:
            errors.append(f"task {task_id}: unknown contracts {sorted(unknown_contracts)}")
        if provides & consumes:
            errors.append(f"task {task_id}: cannot both provide and consume the same contract")

        task_integrations = set(task.get("integration_checks", []))
        unknown_integrations = task_integrations - set(integrations)
        if unknown_integrations:
            errors.append(f"task {task_id}: unknown integration checks {sorted(unknown_integrations)}")

        if task.get("parallel_candidate"):
            if task.get("ownership_status") != "known":
                errors.append(f"task {task_id}: parallel candidate requires known ownership")
            if not task.get("files_hint"):
                errors.append(f"task {task_id}: parallel candidate requires files_hint")
            for path in task.get("files_hint", []):
                if any(character in path for character in "*?["):
                    errors.append(
                        f"task {task_id}: parallel candidate requires concrete ownership paths"
                    )

    workstream_ancestors = {
        workstream_id: transitive_dependencies(workstream_id, workstreams, "depends_on")
        for workstream_id in workstreams
    }
    for task_id, task in tasks.items():
        source_workstream = task.get("workstream_id")
        allowed_workstreams = {source_workstream} | workstream_ancestors.get(source_workstream, set())
        for dependency_id in task.get("deps", []):
            if dependency_id not in tasks:
                continue
            dependency_workstream = tasks[dependency_id].get("workstream_id")
            if dependency_workstream not in allowed_workstreams:
                errors.append(
                    f"task {task_id}: dependency {dependency_id} contradicts workstream ordering"
                )

    providers: dict[str, list[str]] = {contract_id: [] for contract_id in contracts}
    consumers: dict[str, list[str]] = {contract_id: [] for contract_id in contracts}
    for task_id, task in tasks.items():
        for contract_id in task.get("provides_contracts", []):
            providers.setdefault(contract_id, []).append(task_id)
        for contract_id in task.get("consumes_contracts", []):
            consumers.setdefault(contract_id, []).append(task_id)

    task_ancestors = {
        task_id: transitive_dependencies(task_id, tasks, "deps")
        for task_id in tasks
    }
    tasks_by_workstream: dict[str, set[str]] = {workstream_id: set() for workstream_id in workstreams}
    for task_id, task in tasks.items():
        tasks_by_workstream.setdefault(task.get("workstream_id"), set()).add(task_id)

    for workstream_id, workstream in workstreams.items():
        completion_task_id = workstream.get("completion_task_id")
        if completion_task_id not in tasks:
            errors.append(
                f"workstream {workstream_id}: unknown completion task {completion_task_id}"
            )
            continue
        if tasks[completion_task_id].get("workstream_id") != workstream_id:
            errors.append(
                f"workstream {workstream_id}: completion task belongs to another workstream"
            )
            continue
        other_tasks = tasks_by_workstream.get(workstream_id, set()) - {completion_task_id}
        missing_from_completion = other_tasks - task_ancestors.get(completion_task_id, set())
        if missing_from_completion:
            errors.append(
                f"workstream {workstream_id}: completion task does not depend on "
                f"{sorted(missing_from_completion)}"
            )

    for task_id, task in tasks.items():
        workstream_id = task.get("workstream_id")
        if workstream_id not in workstreams:
            continue
        for dependency_workstream_id in workstreams[workstream_id].get("depends_on", []):
            if dependency_workstream_id not in workstreams:
                continue
            dependency_completion = workstreams[dependency_workstream_id].get("completion_task_id")
            if dependency_completion not in task_ancestors.get(task_id, set()):
                errors.append(
                    f"task {task_id}: must follow completion of workstream "
                    f"{dependency_workstream_id}"
                )
    for contract_id, contract in contracts.items():
        contract_providers = providers.get(contract_id, [])
        contract_consumers = consumers.get(contract_id, [])
        if len(contract_providers) != 1:
            errors.append(
                f"contract {contract_id}: expected exactly one provider task, got {len(contract_providers)}"
            )
            continue
        if not contract_consumers:
            errors.append(f"contract {contract_id}: no consumer task")

        provider_id = contract_providers[0]
        provider_aspect = contract.get("provider_aspect")
        if provider_aspect not in set(tasks[provider_id].get("aspects", [])):
            errors.append(f"contract {contract_id}: provider task has wrong aspect")

        allowed_consumers = set(contract.get("consumer_aspects", []))
        for consumer_id in contract_consumers:
            if not (set(tasks[consumer_id].get("aspects", [])) & allowed_consumers):
                errors.append(f"contract {contract_id}: consumer task {consumer_id} has wrong aspect")
            if provider_id not in task_ancestors.get(consumer_id, set()):
                errors.append(
                    f"contract {contract_id}: consumer task {consumer_id} must depend on provider {provider_id}"
                )

    integration_owners: dict[str, list[str]] = {integration_id: [] for integration_id in integrations}
    for task_id, task in tasks.items():
        for integration_id in task.get("integration_checks", []):
            integration_owners.setdefault(integration_id, []).append(task_id)
    for integration_id, integration in integrations.items():
        owners = integration_owners.get(integration_id, [])
        if len(owners) != 1:
            errors.append(
                f"integration check {integration_id}: expected exactly one owner task, got {len(owners)}"
            )
            continue
        owner_aspects = set(tasks[owners[0]].get("aspects", []))
        required_aspects = set(integration.get("aspects", []))
        if not required_aspects.issubset(owner_aspects):
            errors.append(
                f"integration check {integration_id}: owner task does not include all aspects"
            )

    spec_acs = set(AC_PATTERN.findall(spec_text))
    task_acs = {
        ac
        for task in tasks.values()
        for ac in task.get("acs", [])
        if isinstance(ac, str)
    }
    if not spec_acs:
        errors.append("spec: no AC-* identifiers found")
    unknown_acs = task_acs - spec_acs
    missing_acs = spec_acs - task_acs
    if unknown_acs:
        errors.append(f"tasks: unknown acceptance criteria {sorted(unknown_acs)}")
    if missing_acs:
        errors.append(f"tasks: uncovered acceptance criteria {sorted(missing_acs)}")

    parallel_ids = [
        task_id for task_id, task in tasks.items() if task.get("parallel_candidate")
    ]
    for index, left_id in enumerate(parallel_ids):
        for right_id in parallel_ids[index + 1 :]:
            if left_id in task_ancestors.get(right_id, set()) or right_id in task_ancestors.get(left_id, set()):
                continue
            overlap = {
                f"{left_path} <> {right_path}"
                for left_path in tasks[left_id].get("files_hint", [])
                for right_path in tasks[right_id].get("files_hint", [])
                if paths_overlap(left_path, right_path)
            }
            if overlap:
                errors.append(
                    f"parallel tasks {left_id}/{right_id}: overlapping files {sorted(overlap)}"
                )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Kapelle task-plan semantics")
    parser.add_argument("--tasks", required=True, type=Path)
    parser.add_argument("--surface-plan", required=True, type=Path)
    parser.add_argument("--spec", required=True, type=Path)
    args = parser.parse_args()

    try:
        errors = validate(args.tasks, args.surface_plan, args.spec)
    except (OSError, ValueError) as exc:
        print(f"FAILED: {exc}")
        return 1

    if errors:
        print(f"FAILED: {len(errors)} task-plan error(s)")
        for error in errors:
            print(f"- {error}")
        return 1

    print("PASSED: task-plan semantic validation")
    return 0


if __name__ == "__main__":
    sys.exit(main())
