from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path
from typing import Iterable


REPOSITORY = Path(__file__).resolve().parents[1]
SCRIPTS = REPOSITORY / "skills" / "ui-ux-skill-orchestrator" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import route  # noqa: E402
from inventory_ui_skills import SkillRecord, load_modules, load_prerequisites  # noqa: E402


MODULES = load_modules()
BY_ID = {module.id: module for module in MODULES}
RULES = route.load_rules()
PREREQUISITES = load_prerequisites()
ALL = tuple(BY_ID)
CORE = tuple(module.id for module in MODULES if module.tier == "core")


def installed(ids: Iterable[str]) -> dict[str, SkillRecord]:
    return {
        module_id: SkillRecord(
            name=module_id,
            description=BY_ID[module_id].description,
            capabilities=sorted(BY_ID[module_id].capabilities),
            scope="global",
            agent_root="test:global",
            path="",
            registered=True,
            module_id=module_id,
            tier=BY_ID[module_id].tier,
            role=BY_ID[module_id].role,
        )
        for module_id in ids
    }


def brief(
    query: str,
    available: Iterable[str] = ALL,
    task: str | None = None,
    scope: str | None = None,
) -> route.Brief:
    request = route.analyze(query, RULES, task, scope)
    return route.build_brief(
        request,
        RULES,
        MODULES,
        installed(available),
        (),
        PREREQUISITES,
        "codex",
    )


def team(result: route.Brief) -> list[str]:
    members = [result.lead, *result.specialists]
    if result.validation:
        members.append(result.validation)
    return [member.module for member in members]


class RoutingScenarioTests(unittest.TestCase):
    def assert_single_owner_per_concern(self, result: route.Brief) -> None:
        owners: dict[str, str] = {}
        for member in [*result.specialists, *([result.validation] if result.validation else [])]:
            for concern in member.owns:
                self.assertNotIn(
                    concern,
                    owners,
                    f"{concern} owned by {owners.get(concern)} and {member.module}",
                )
                owners[concern] = member.module

    def test_stitch_request_is_led_by_stitch_module(self) -> None:
        result = brief("Generate a Stitch DESIGN.md for our app")
        self.assertEqual(result.rule, "stitch-design-system")
        self.assertEqual(result.lead.module, "stitch-design-taste")
        self.assertIn("frontend-design", {item["module"] for item in result.excluded})

    def test_figma_rules_and_figma_implementation_route_differently(self) -> None:
        rules = brief("Create Figma design system rules for this codebase")
        self.assertEqual(rules.lead.module, "figma-create-design-system-rules")
        self.assertIn("figma-mcp", rules.prerequisites)

        frame = brief("Implement this Figma frame as a React page")
        self.assertEqual(frame.rule, "figma-design-to-code")
        self.assertEqual(frame.lead.module, "figma-implement-design")
        excluded = {item["module"]: item["reason"] for item in frame.excluded}
        self.assertIn("Figma", excluded["frontend-design"])

    def test_narrow_motion_fix_uses_motion_lead_without_reviewer(self) -> None:
        result = brief("Smooth out the janky dropdown animation")
        self.assertEqual(result.rule, "motion-focus")
        self.assertEqual(result.scope, "component")
        self.assertEqual(result.lead.module, "ui-animation")
        self.assertIsNone(result.validation)
        self.assertTrue(result.excluded)
        self.assertTrue(all("Not needed" in item["reason"] for item in result.excluded))

    def test_accessibility_audit_prefers_accessibility_specialist(self) -> None:
        result = brief("Audit the checkout form for accessibility and keyboard focus")
        self.assertEqual(result.rule, "accessibility-focus")
        self.assertEqual(result.lead.module, "fixing-accessibility")
        self.assertEqual(result.validation.module, "ui-verification")
        self.assertIn("browser-automation", result.prerequisites)

        core_only = brief(
            "Audit the checkout form for accessibility and keyboard focus",
            CORE,
        )
        self.assertEqual(core_only.validation.module, "impeccable")
        self.assertEqual(core_only.missing, [])

    def test_typography_audit_assigns_typography_specialist(self) -> None:
        result = brief("Audit the typography hierarchy and font loading on our docs")
        self.assertIn("typography-audit", team(result))

    def test_greenfield_page_keeps_research_out_without_open_evidence(self) -> None:
        result = brief(
            "Build a bold landing page for a coffee brand with smooth scroll animations",
            CORE,
        )
        self.assertEqual(result.rule, "greenfield")
        self.assertEqual(result.lead.module, "frontend-design")
        self.assertEqual([member.module for member in result.specialists], ["ui-animation"])
        self.assertEqual(result.validation.module, "impeccable")
        self.assertNotIn("ui-ux-pro-max", team(result))
        self.assertIn("mies", {item["module"] for item in result.excluded})

    def test_page_budget_extends_only_for_evidence_motion_and_validation(self) -> None:
        query = (
            "Build a landing page for a fintech app; choose the color palette and "
            "font pairing, make it accessible{motion}"
        )
        extended = brief(query.format(motion=", and add scroll animations"), CORE)
        self.assertEqual(extended.scope, "page")
        self.assertEqual(len(extended.specialists), 3)
        self.assert_single_owner_per_concern(extended)

        standard = brief(query.format(motion=""), CORE)
        self.assertEqual(len(standard.specialists), 2)
        self.assertNotIn("ui-animation", team(standard))

    def test_palette_for_a_built_page_keeps_production_validation(self) -> None:
        result = brief("Build a pricing page for our SaaS product with a new color palette", CORE)
        self.assertEqual(result.rule, "color-selection")
        self.assertEqual(result.lead.module, "frontend-design")
        self.assertEqual([member.module for member in result.specialists], ["ui-ux-pro-max"])
        self.assertEqual(result.validation.module, "impeccable")

        palette_only = brief("Choose a color palette for our existing brand", CORE)
        self.assertEqual(palette_only.lead.module, route.INCUMBENT)
        self.assertEqual(palette_only.validation.module, "fixing-accessibility")

    def test_calm_dashboard_is_led_by_mies_and_validated_by_impeccable(self) -> None:
        result = brief("Redesign our analytics dashboard to feel calm and minimal", CORE)
        self.assertEqual(result.rule, "dashboard")
        self.assertEqual(result.lead.module, "mies")
        self.assertIn("ui-ux-pro-max", team(result))
        self.assertEqual(result.validation.module, "impeccable")
        self.assertEqual(result.missing, [])

    def test_single_component_keeps_incumbent_system_as_lead(self) -> None:
        result = brief("Add an error state to the email input", CORE)
        self.assertEqual(result.scope, "component")
        self.assertEqual(result.rule, "single-component")
        self.assertEqual(result.lead.module, route.INCUMBENT)
        self.assertIsNone(result.validation)
        self.assertLessEqual(len(result.specialists), 1)

    def test_refinement_uses_incumbent_lead_and_layout_specialist(self) -> None:
        result = brief("Fix the spacing and alignment on the settings page", CORE)
        self.assertEqual(result.rule, "existing-refinement")
        self.assertEqual(result.lead.module, route.INCUMBENT)
        self.assertIn("mies", [member.module for member in result.specialists])
        self.assertEqual(result.validation.module, "impeccable")

    def test_missing_lead_falls_back_to_incumbent_with_install_hint(self) -> None:
        available = [module_id for module_id in CORE if module_id != "ui-animation"]
        result = brief("Smooth out the janky dropdown animation", available)
        self.assertEqual(result.lead.module, route.INCUMBENT)
        self.assertIn("No preferred lead", result.lead.reason)
        hints = {item["module"]: item["install"] for item in result.missing}
        self.assertIn("--only ui-animation", hints["ui-animation"])
        self.assertIn("--agent codex", hints["ui-animation"])

    def test_overrides_replace_inferred_task_and_scope(self) -> None:
        request = route.analyze("Make the hero better", RULES, "audit", "surface")
        self.assertEqual(request.tasks, ("audit",))
        self.assertEqual(request.scope, "surface")

    def test_default_rule_catches_unmatched_requests(self) -> None:
        request = route.Request(query="", text="", needs=(), tasks=("create",), scope="system")
        self.assertEqual(route.select_rule(RULES, request)["id"], "default")

    def test_every_rule_resolves_a_lead_when_all_modules_are_installed(self) -> None:
        for rule in RULES["rules"]:
            for entry in rule["lead"]:
                module_id = entry["module"] if isinstance(entry, dict) else entry
                if module_id != route.INCUMBENT:
                    self.assertIn(module_id, BY_ID, rule["id"])

    def test_cli_emits_json_brief_in_planning_mode(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "route.py"),
                "--assume-installed",
                "--format",
                "json",
                "--query",
                "Generate a Stitch DESIGN.md for our app",
            ],
            cwd=REPOSITORY,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["rule"], "stitch-design-system")
        self.assertEqual(payload["lead"]["module"], "stitch-design-taste")


if __name__ == "__main__":
    unittest.main()
