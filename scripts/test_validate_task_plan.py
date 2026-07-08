#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from validate_task_plan import validate

ROOT = Path(__file__).resolve().parent.parent


class ValidateTaskPlanTest(unittest.TestCase):
    def setUp(self) -> None:
        self.plan = json.loads((ROOT / "examples/task-plan.json").read_text())
        self.surface = json.loads((ROOT / "examples/surface-plan.json").read_text())
        self.spec = (ROOT / "examples/task-plan-spec.md").read_text()

    def validate_plan(self, plan: dict, spec: str | None = None) -> list[str]:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tasks_path = root / "tasks.json"
            surface_path = root / "surface-plan.json"
            spec_path = root / "spec.md"
            tasks_path.write_text(json.dumps(plan))
            surface_path.write_text(json.dumps(self.surface))
            spec_path.write_text(spec if spec is not None else self.spec)
            return validate(tasks_path, surface_path, spec_path)

    def test_valid_plan_passes(self) -> None:
        self.assertEqual([], self.validate_plan(self.plan))

    def test_dependency_cycle_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["tasks"][0]["deps"] = ["T4"]
        errors = self.validate_plan(plan)
        self.assertTrue(any("dependency cycle" in error for error in errors))

    def test_uncovered_acceptance_criterion_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        for task in plan["tasks"]:
            task["acs"] = ["AC-01"]
        errors = self.validate_plan(plan)
        self.assertIn("tasks: uncovered acceptance criteria ['AC-02']", errors)

    def test_contract_consumer_must_follow_provider(self) -> None:
        plan = copy.deepcopy(self.plan)
        consumer = next(task for task in plan["tasks"] if task["id"] == "T3")
        consumer["deps"] = []
        errors = self.validate_plan(plan)
        self.assertTrue(any("must depend on provider T1" in error for error in errors))

    def test_workstream_completion_covers_all_tasks(self) -> None:
        plan = copy.deepcopy(self.plan)
        completion = next(task for task in plan["tasks"] if task["id"] == "T2")
        completion["deps"] = []
        errors = self.validate_plan(plan)
        self.assertTrue(any("completion task does not depend on" in error for error in errors))

    def test_dependent_workstream_waits_for_completion(self) -> None:
        plan = copy.deepcopy(self.plan)
        consumer = next(task for task in plan["tasks"] if task["id"] == "T3")
        consumer["deps"] = ["T1"]
        errors = self.validate_plan(plan)
        self.assertTrue(any("must follow completion of workstream WS-PROVIDER" in error for error in errors))

    def test_integration_check_has_one_owner(self) -> None:
        plan = copy.deepcopy(self.plan)
        extra_owner = next(task for task in plan["tasks"] if task["id"] == "T3")
        extra_owner["integration_checks"] = ["feature-round-trip"]
        extra_owner["aspects"] = ["backend", "frontend"]
        errors = self.validate_plan(plan)
        self.assertTrue(any("expected exactly one owner task" in error for error in errors))

    def test_parallel_overlap_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        first = next(task for task in plan["tasks"] if task["id"] == "T2")
        first["parallel_candidate"] = True
        first["files_hint"] = ["src/shared"]
        parallel = copy.deepcopy(first)
        parallel["id"] = "T5"
        parallel["title"] = "Independent provider support"
        parallel["intent"] = "Add independently validated provider support."
        parallel["files_hint"] = ["src/shared/child"]
        plan["tasks"].append(parallel)
        errors = self.validate_plan(plan)
        self.assertTrue(any("overlapping files" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
