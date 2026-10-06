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

    def test_restrained_direction_prefers_mies_over_general_lead(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_skill(
                root,
                "mies",
                "mies",
                "Restrained UI direction, hierarchy, layout, and spacing.",
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
                    "Refine this dashboard into a calm restrained layout",
                )
            scores = {record.name: record.score for record in records}
            self.assertGreater(scores["mies"], scores["frontend-design"])

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

    def test_symlinked_skill_folder_is_discovered_once(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            store = base / "store"
            write_skill(store, "ui-animation", "ui-animation", "Designs UI motion.")
            root = base / "skills"
            root.mkdir()
            try:
                (root / "ui-animation").symlink_to(
                    store / "ui-animation",
                    target_is_directory=True,
                )
                (root / "loop").symlink_to(root, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("Symbolic links are unavailable on this platform.")
            manifests = list(inventory.iter_skill_manifests(root))
            self.assertEqual([path.parent.name for path in manifests], ["ui-animation"])

    def test_hidden_and_deep_roots_require_opt_in(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_skill(
                root / "market" / "plugin" / "1.0.0" / ".claude" / "skills",
                "fancy-ui",
                "fancy-ui",
                "Frontend UI layout patterns.",
            )
            self.assertEqual(len(list(inventory.iter_skill_manifests(root, 6, True))), 1)
            self.assertEqual(list(inventory.iter_skill_manifests(root, 6, False)), [])
            self.assertEqual(list(inventory.iter_skill_manifests(root, 3, True)), [])

    def test_alias_and_canonical_install_are_deduplicated(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_skill(root, "taste-design", "taste-design", "Stitch design system.")
            write_skill(
                root,
                "stitch-design-taste",
                "stitch-design-taste",
                "Stitch design system.",
            )
            with patch.object(
                inventory,
                "root_specs",
                return_value=[(root, "project", "codex:project")],
            ):
                records = inventory.discover("codex", root, False, "")
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0].module_id, "stitch-design-taste")

    def test_frontmatter_subset_handles_bom_block_and_quoted_values(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            block = folder / "block.md"
            block.write_text(
                "\ufeff---\nname: 'block-skill'\ndescription: >-\n"
                "  Designs accessible\n  frontend forms.\nmetadata:\n"
                '  version: "1.0"\n---\n',
                encoding="utf-8",
            )
            self.assertEqual(
                inventory.parse_frontmatter(block),
                ("block-skill", "Designs accessible frontend forms."),
            )
            quoted = folder / "quoted.md"
            quoted.write_text(
                '---\nname: quoted-skill\ndescription: "Audits UI: spacing, color"\n---\n',
                encoding="utf-8",
            )
            self.assertEqual(
                inventory.parse_frontmatter(quoted),
                ("quoted-skill", "Audits UI: spacing, color"),
            )
            plain = folder / "plain.md"
            plain.write_text(
                "---\nname: plain-skill\ndescription: Designs accessible\n"
                "  frontend forms # note\n---\n",
                encoding="utf-8",
            )
            self.assertEqual(
                inventory.parse_frontmatter(plain),
                ("plain-skill", "Designs accessible frontend forms"),
            )
            missing = folder / "missing.md"
            missing.write_text("---\nname: no-description\n---\n", encoding="utf-8")
            self.assertIsNone(inventory.parse_frontmatter(missing))

    def test_engineering_skills_with_ui_words_are_not_listed(self) -> None:
        cases = {
            "spring-boot-service": "Build Spring Boot services with clean controller layout in Kotlin.",
            "postgres-tokens": "Rotate PostgreSQL auth tokens and table permissions.",
            "bevy-ecs": "Entity component system patterns for Bevy game engine UI widgets.",
            "desktop-driver": (
                "Drive a native GUI app; snapshot its accessibility tree and "
                "perform a GUI task."
            ),
        }
        for name, description in cases.items():
            capabilities = inventory.classify(name, description, {})
            self.assertFalse(
                inventory.is_ui_skill(name, description, capabilities),
                name,
            )
        description = "Improves frontend form UX, labels, and validation states."
        capabilities = inventory.classify("form-ux", description, {})
        self.assertTrue(inventory.is_ui_skill("form-ux", description, capabilities))

    def test_engineering_terms_do_not_create_design_concerns(self) -> None:
        self.assertNotIn("motion", inventory.profile_query("Add a Spring Boot endpoint").needs)
        self.assertNotIn(
            "design-system",
            inventory.classify("auth-tokens", "Refresh expired auth tokens.", {}),
        )

    def test_stopwords_are_not_ranking_tokens(self) -> None:
        profile = inventory.profile_query("Please make the onboarding better for us")
        self.assertTrue({"please", "make", "the", "better"}.isdisjoint(profile.tokens))
        self.assertIn("onboarding", profile.tokens)

    def test_common_words_are_not_skill_mentions(self) -> None:
        self.assertFalse(inventory.is_mentioned("a luxury watch landing page", "ux", False))
        self.assertFalse(
            inventory.is_mentioned("a luxury watch landing page", "ui-ux-pro-max", True)
        )
        self.assertTrue(inventory.is_mentioned("use $mies for this", "mies", False))
        self.assertTrue(inventory.is_mentioned("run ui-ux-pro-max first", "ui-ux-pro-max", True))

    def test_integration_modules_need_a_specific_trigger(self) -> None:
        registry = inventory.module_index(inventory.load_modules())
        module = registry["typography-audit"]
        record = inventory.SkillRecord(
            name=module.id,
            description=module.description,
            capabilities=sorted(module.capabilities),
            scope="global",
            agent_root="codex:global",
            path="",
            registered=True,
            module_id=module.id,
            tier=module.tier,
        )
        untriggered = inventory.profile_query("Build a landing page layout with scroll motion")
        self.assertEqual(inventory.rank_record(record, untriggered, registry)[0], 0)
        triggered = inventory.profile_query("Audit the typography hierarchy and font loading")
        score, matched = inventory.rank_record(record, triggered, registry)
        self.assertGreater(score, 0)
        self.assertIn("typography", matched)

    def test_agent_roots_list_project_folders_before_global_folders(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            specs = inventory.root_specs("all", Path(temporary))
        scopes = [spec.scope for spec in specs]
        self.assertIn("global", scopes)
        self.assertEqual(scopes, sorted(scopes, key=lambda scope: scope != "project"))

    def test_claude_code_reads_its_own_folders_and_plugin_cache(self) -> None:
        claude = inventory.load_agents()["claude-code"]
        self.assertNotIn(".agents/skills", {root.path for root in claude.project})
        cache = next(
            root for root in claude.global_roots if root.path == ".claude/plugins/cache"
        )
        self.assertTrue(cache.include_hidden)
        self.assertGreaterEqual(cache.depth, 5)

    def test_unknown_agent_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            inventory.selected_agents("not-an-agent")


if __name__ == "__main__":
    unittest.main()
