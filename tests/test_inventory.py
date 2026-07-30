from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPOSITORY = Path(__file__).resolve().parents[1]
SCRIPTS = REPOSITORY / "skills" / "ui-ux-skill-orchestrator" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import inventory_ui_skills as inventory  # noqa: E402


def write_skill(root: Path, folder: str, name: str, description: str) -> Path:
    path = root / folder
    path.mkdir(parents=True)
    (path / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: {description}\n---\n\n# {name}\n",
        encoding="utf-8",
    )
    return path


class InventoryTests(unittest.TestCase):
    def test_registered_alias_maps_to_canonical_module(self) -> None:
        registry = inventory.module_index(inventory.load_modules())
        self.assertEqual(registry["taste-design"].id, "stitch-design-taste")
        self.assertEqual(registry["taste-design"].tier, "integration")

    def test_project_skill_wins_over_global_duplicate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            project_root = base / "project"
            global_root = base / "global"
            project = write_skill(
                project_root,
                "ui-animation",
                "ui-animation",
                "Project UI animation specialist.",
            )
            write_skill(
                global_root,
                "ui-animation",
                "ui-animation",
                "Global UI animation specialist.",
            )
            specs = [
                (project_root, "project", "codex:project"),
                (global_root, "global", "codex:global"),
            ]
            with patch.object(inventory, "root_specs", return_value=specs):
                records = inventory.discover(
                    "codex",
                    base,
                    False,
                    "add motion",
                )
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0].path, str(project.resolve()))
            self.assertEqual(records[0].scope, "project")

    def test_motion_query_ranks_motion_specialist_first(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_skill(
                root,
                "ui-animation",
                "ui-animation",
                "Designs UI motion, animation, easing, and gestures.",
            )
            write_skill(
                root,
                "frontend-design",
                "frontend-design",
                "Creates distinctive frontend visual design.",
            )
            with patch.object(
                inventory,
                "root_specs",
                return_value=[(root, "project", "codex:project")],
            ):
                records = inventory.discover(
                    "codex",
                    root,
                    False,
                    "Make this button animation smooth and accessible",
                )
            self.assertEqual(records[0].name, "ui-animation")
            self.assertGreater(records[0].score, records[1].score)

    def test_dynamic_ui_skill_is_discovered(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_skill(
                root,
                "type-inspector",
                "type-inspector",
                "Audits frontend typography and font loading.",
            )
            with patch.object(
                inventory,
                "root_specs",
                return_value=[(root, "project", "codex:project")],
            ):
                records = inventory.discover("codex", root, False, "font audit")
            self.assertEqual(records[0].module_id, None)
            self.assertIn("typography", records[0].capabilities)
            self.assertFalse(records[0].registered)

    def test_non_ui_and_orchestrator_skills_are_excluded(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_skill(
                root,
                "backend-release",
                "backend-release",
                "Publishes database migrations and API releases.",
            )
            write_skill(
                root,
                "orchestrator",
                "ui-ux-skill-orchestrator",
                "Routes frontend UI and UX skills.",
            )
            with patch.object(
                inventory,
                "root_specs",
                return_value=[(root, "project", "codex:project")],
            ):
                records = inventory.discover("codex", root, False, "")
            self.assertEqual(records, [])


if __name__ == "__main__":
    unittest.main()
