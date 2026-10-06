from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]
SKILL = REPOSITORY / "skills" / "ui-ux-skill-orchestrator"
sys.path.insert(0, str(SKILL / "scripts"))

from inventory_ui_skills import load_modules  # noqa: E402


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class DocumentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.modules = load_modules()

    def test_every_module_is_documented(self) -> None:
        documents = {
            "README.md": read(REPOSITORY / "README.md"),
            "capability-map.md": read(SKILL / "references" / "capability-map.md"),
        }
        for module in self.modules:
            for name, text in documents.items():
                self.assertIn(f"`{module.id}`", text, f"{module.id} is missing from {name}")

    def test_every_module_source_is_credited(self) -> None:
        notice = read(REPOSITORY / "NOTICE.md")
        for module in self.modules:
            self.assertIn(module.source_url, notice, module.id)

    def test_release_versions_match(self) -> None:
        skill_version = re.search(
            r'^\s+version:\s*"([^"]+)"',
            read(SKILL / "SKILL.md"),
            re.MULTILINE,
        )
        released = re.search(
            r"^## \[(\d+\.\d+\.\d+)\]",
            read(REPOSITORY / "CHANGELOG.md"),
            re.MULTILINE,
        )
        plugin = json.loads(read(REPOSITORY / ".claude-plugin" / "plugin.json"))
        self.assertIsNotNone(skill_version)
        self.assertIsNotNone(released)
        self.assertEqual(skill_version.group(1), plugin["version"])
        self.assertEqual(skill_version.group(1), released.group(1))

    def test_marketplace_publishes_this_plugin(self) -> None:
        marketplace = json.loads(read(REPOSITORY / ".claude-plugin" / "marketplace.json"))
        plugin = json.loads(read(REPOSITORY / ".claude-plugin" / "plugin.json"))
        entries = {entry["name"]: entry for entry in marketplace["plugins"]}
        self.assertEqual(entries[plugin["name"]]["source"], "./")
        self.assertTrue((REPOSITORY / "skills" / plugin["name"] / "SKILL.md").is_file())


if __name__ == "__main__":
    unittest.main()
