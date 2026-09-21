import json
import tempfile
import unittest
from pathlib import Path

from feature_state import (FeatureStateError, approval_current,
                           choose_human_controlled_next_command, refresh_feature_status)
from review_gate import approve
from staged_design import MARKER, REVIEW, parts
from validate_progressive_docs import ARTIFACT_MARKER, SPEC_HEADINGS, DESIGN_HEADINGS


class StagedDesignTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        files = {
            "spec.md": "<!-- kapelle-workflow: lightweight-v1 -->\n" + ARTIFACT_MARKER
                       + "\n# Reservation\n" + "".join(h + "\nConcrete behavior.\n" for h in SPEC_HEADINGS),
            "design.md": MARKER + "\n# Architecture\n"
                         + "".join(h + "\nConcrete architecture.\n" for h in DESIGN_HEADINGS),
            "tasks.md": "# Tasks\n- [ ] W1 Complete checkout\n",
            REVIEW: "# Direction\nReserve then charge.\n\n## Review order\n"
                    "| Part | Design | Contracts |\n| --- | --- | --- |\n"
                    "| reservation | design/reservation.md | contracts/shared.md |\n"
                    "| payment | design/payment.md | contracts/shared.md |\n"
                    "| receipt | design/receipt.md | - |\n",
            "design/reservation.md": "# Reservation\nHold stock until expiry.\n",
            "design/payment.md": "# Payment\nCharge idempotently.\n",
            "design/receipt.md": "# Receipt\nDisplay confirmation.\n",
            "contracts/shared.md": "# Reservation contract\nIdentifier and expiry.\n",
            "design/integration.md": "# Integration\nReserve, charge, confirm; release on failure.\n",
        }
        for relative, content in files.items():
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        guidance = self.root / "_kapelle/architecture-guidance/design.json"
        guidance.parent.mkdir(parents=True)
        guidance.write_text(json.dumps({
            "status": "ARCHITECTURE_GUIDANCE_READY",
            "capability": {"name": "rules", "kind": "project-skill"},
            "scope": {"aspects": ["checkout"], "modules": [], "entrypoints": [], "paths": []},
            "rules": [], "sources": [], "gaps": [],
        }))

    def approve(self, gate):
        approve(self.root, gate, "Explicit developer approval in test fixture", refresh=False)

    def approve_all(self):
        for gate in ["design-vision", "design-part-reservation", "design-part-payment",
                     "design-part-receipt", "plan"]:
            self.approve(gate)

    def test_order_and_integration_are_required_before_implementation(self):
        for gate in ["design-part-reservation", "plan"]:
            with self.assertRaises(FeatureStateError):
                self.approve(gate)
        self.approve("design-vision")
        with self.assertRaises(FeatureStateError):
            self.approve("design-part-payment")
        self.assertEqual(("start", "/kapelle:start checkout --part reservation"),
                         choose_human_controlled_next_command("checkout", self.root, {"W1": "pending"}))
        for part in parts(self.root):
            self.approve("design-part-" + part)
        (self.root / "design/integration.md").unlink()
        with self.assertRaises(FeatureStateError):
            self.approve("plan")
        (self.root / "design/integration.md").write_text("Integrated flow reviewed.")
        self.approve("plan")
        self.assertEqual("implement", choose_human_controlled_next_command(
            "checkout", self.root, {"W1": "pending"})[0])

    def test_private_detail_invalidates_only_its_part_and_slice(self):
        self.approve_all()
        (self.root / "design/payment.md").write_text("Revised payment retry strategy.")
        self.assertFalse(approval_current(self.root, "design-part-payment"))
        for gate in ["design-vision", "design-part-reservation", "design-part-receipt"]:
            self.assertTrue(approval_current(self.root, gate), gate)
        self.assertFalse(approval_current(self.root, "plan"))

    def test_shared_contract_invalidates_consumers_but_not_independent_part(self):
        self.approve_all()
        (self.root / "contracts/shared.md").write_text("New expiry semantics.")
        for gate in ["design-part-reservation", "design-part-payment", "plan"]:
            self.assertFalse(approval_current(self.root, gate), gate)
        self.assertTrue(approval_current(self.root, "design-part-receipt"))
        self.assertTrue(approval_current(self.root, "design-vision"))

    def test_lost_vision_approval_and_missing_table_fail_closed(self):
        self.approve_all()
        (self.root / "_kapelle/approvals/design-vision.json").unlink()
        self.assertFalse(approval_current(self.root, "design-part-payment"))
        self.assertFalse(approval_current(self.root, "plan"))
        self.assertEqual("/kapelle:start checkout --approve-vision",
                         choose_human_controlled_next_command("checkout", self.root, {})[1])
        (self.root / REVIEW).unlink()
        with self.assertRaises(FeatureStateError):
            self.approve("plan")
        self.assertFalse(approval_current(self.root, "plan"))

    def test_unsafe_duplicate_and_unknown_parts_are_rejected(self):
        original = (self.root / REVIEW).read_text()
        for invalid in [original.replace("design/payment.md", "design/../../outside.md"),
                        original.replace("| payment |", "| reservation |")]:
            (self.root / REVIEW).write_text(invalid)
            with self.assertRaises(ValueError):
                parts(self.root)
        (self.root / REVIEW).write_text(original)
        with self.assertRaises(FeatureStateError):
            self.approve("design-part-unknown")

    def test_status_recovery_preserves_review_route_without_fabricating_approval(self):
        refresh_feature_status(self.root)
        self.assertIn("--approve-vision", (self.root / "STATUS.md").read_text())
        self.assertFalse((self.root / "_kapelle/approvals/design-vision.json").exists())
        approve(self.root, "design-vision", "Explicit direction approval", refresh=True)
        self.assertIn("--part reservation", (self.root / "STATUS.md").read_text())
        self.approve_all()
        refresh_feature_status(self.root)
        self.assertIn("/kapelle:implement", (self.root / "STATUS.md").read_text())


if __name__ == "__main__":
    unittest.main()
