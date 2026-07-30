from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch


REPOSITORY = Path(__file__).resolve().parents[1]
SCRIPTS = REPOSITORY / "skills" / "ui-ux-skill-orchestrator" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import setup as specialist_setup  # noqa: E402
from inventory_ui_skills import load_modules  # noqa: E402


class SetupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.modules = load_modules()

    def test_default_selection_contains_only_core_modules(self) -> None:
        selected = specialist_setup.select_modules(self.modules, False, [])
        self.assertTrue(selected)
        self.assertTrue(all(module.tier == "core" for module in selected))
        self.assertNotIn("stitch-design-taste", {module.id for module in selected})

    def test_integrations_can_be_included(self) -> None:
        selected = specialist_setup.select_modules(self.modules, True, [])
        ids = {module.id for module in selected}
        self.assertIn("stitch-design-taste", ids)
        self.assertIn("figma-create-design-system-rules", ids)

    def test_alias_selects_canonical_module(self) -> None:
        selected = specialist_setup.select_modules(
            self.modules,
            False,
            ["taste-design"],
        )
        self.assertEqual([module.id for module in selected], ["stitch-design-taste"])

    def test_unknown_module_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unknown module"):
            specialist_setup.select_modules(
                self.modules,
                False,
                ["not-a-real-module"],
            )

    def test_global_install_command_is_noninteractive(self) -> None:
        module = next(item for item in self.modules if item.id == "ui-animation")
        command = specialist_setup.install_command(module, "codex", False)
        self.assertEqual(
            command,
            [
                "npx",
                "--yes",
                "skills",
                "add",
                "mblode/agent-skills",
                "--skill",
                "ui-animation",
                "-a",
                "codex",
                "-y",
                "-g",
            ],
        )

    def test_project_install_does_not_include_global_flag(self) -> None:
        module = self.modules[0]
        command = specialist_setup.install_command(module, "cursor", True)
        self.assertNotIn("-g", command)
        self.assertEqual(command[-3:], ["-a", "cursor", "-y"])

    def test_all_agents_uses_cli_wildcard(self) -> None:
        command = specialist_setup.install_command(self.modules[0], "all", False)
        self.assertIn("*", command)

    def test_noninteractive_session_does_not_imply_consent(self) -> None:
        with patch.object(specialist_setup.sys.stdin, "isatty", return_value=False):
            self.assertFalse(
                specialist_setup.confirm_install(3, "codex", project=False)
            )


if __name__ == "__main__":
    unittest.main()
