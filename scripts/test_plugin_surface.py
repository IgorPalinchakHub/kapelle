from pathlib import Path
import json
import re
import unittest
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent


class PluginSurfaceTests(unittest.TestCase):
    def test_old_feature_status_commands_refuse_without_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            feature = Path(tmp) / "old-feature"
            feature.mkdir()
            (feature / "spec.md").write_text("# Historical specification\n")
            (feature / "tasks.md").write_text("- [x] Historical completion\n")
            before = {p.name: p.read_bytes() for p in feature.iterdir()}
            for script in ("build_feature_status.py", "rebuild_feature_state.py"):
                result = subprocess.run(
                    [sys.executable, str(ROOT / "scripts" / script), str(feature)],
                    capture_output=True, text=True,
                )
                self.assertNotEqual(0, result.returncode)
                self.assertIn("new feature directory", result.stdout)
                self.assertEqual(before, {p.name: p.read_bytes() for p in feature.iterdir()})

    def test_migration_entrypoints_are_not_shipped(self):
        self.assertFalse((ROOT / "skills/migrate").exists())
        self.assertEqual([], list((ROOT / "scripts").glob("migrate_*.py")))

    def test_discoverable_skills_match_executable_profiles(self):
        profiles = json.loads((ROOT / "dispatcher/role-profiles.json").read_text())
        skills = {p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md")}
        self.assertEqual(set(profiles["stages"]), skills)
        for name in skills:
            self.assertNotIn("Deprecated compatibility wrapper", (ROOT / "skills" / name / "SKILL.md").read_text())

    def test_plain_references_have_no_provider_substitutions(self):
        for path in (ROOT / "references").glob("*.md"):
            with self.subTest(path=path.name):
                self.assertIsNone(re.search(r"\$\{CLAUDE_[A-Z_]+\}", path.read_text()))

    def test_drawio_graph_references_resolve_within_each_page(self):
        pages = ET.parse(ROOT / "docs/KAPELLE_CLAUDE_CODE_FLOW.drawio").getroot().findall("diagram")
        self.assertEqual(11, len(pages))
        for page in pages:
            with self.subTest(page=page.get("name")):
                cells = page.findall(".//mxCell")
                ids = [cell.get("id") for cell in cells]
                self.assertEqual(len(ids), len(set(ids)))
                for cell in cells:
                    for attribute in ("source", "target", "parent"):
                        if cell.get(attribute):
                            self.assertIn(cell.get(attribute), ids)
