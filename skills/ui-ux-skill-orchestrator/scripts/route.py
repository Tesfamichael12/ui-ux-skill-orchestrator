#!/usr/bin/env python3
"""Draft a routing brief: one lead, narrow specialists, and one validation owner.

The brief is a deterministic starting point built from ``config/routing-rules.json``
and the installed skill inventory. The agent still confirms it against the
product's design truth before acting on it.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Mapping, Sequence

from inventory_ui_skills import (
    CONFIG_DIR,
    DEFAULT_CONFIG,
    Module,
    SkillRecord,
    agent_ids,
    discover,
    load_modules,
    load_prerequisites,
    load_taxonomy,
    matched_terms,
    profile_query,
    read_json_object,
    safe_console,
)


RULES_CONFIG = CONFIG_DIR / "routing-rules.json"
SETUP_SCRIPT = Path(__file__).resolve().parent / "setup.py"
INCUMBENT = "incumbent"
SCOPES = ("component", "page", "surface", "system")
TASKS = ("create", "redesign", "refine", "audit", "debug", "translate")
CONDITION_KEYS = frozenset(
    {
        "capabilities_any",
        "capabilities_all",
        "capabilities_none",
        "needs_within",
        "tasks_any",
        "tasks_none",
        "scopes_any",
        "terms_any",
        "terms_none",
    }
)
NARROW_TASKS = frozenset({"audit", "debug", "refine", "translate"})
INCUMBENT_OWNS = (
    "components",
    "content",
    "design-system",
    "direction",
    "implementation",
    "layout",
    "typography",
    "color",
    "ux",
)
# Open axes that justify a research specialist; direction alone belongs to the lead.
EVIDENCE_NEEDS = frozenset({"color", "data-viz", "typography", "ux"})


@dataclass(frozen=True)
class Request:
    query: str
    text: str
    needs: tuple[str, ...]
    tasks: tuple[str, ...]
    scope: str


@dataclass
class Member:
    module: str
    skill: str | None
    owns: list[str]
    reason: str
    requires: list[str] = field(default_factory=list)


@dataclass
class Brief:
    query: str
    scope: str
    tasks: list[str]
    needs: list[str]
    rule: str
    rule_description: str
    recipe: str | None
    lead: Member
    specialists: list[Member]
    validation: Member | None
    excluded: list[dict[str, str]]
    missing: list[dict[str, str]]
    prerequisites: dict[str, str]
    uncovered: list[str]
    candidates: list[str]


def load_rules(path: Path = RULES_CONFIG) -> dict:
    return read_json_object(path)


def infer_scope(text: str, tasks: Sequence[str], rules: Mapping) -> str:
    """Pick the narrowest explicit scope; "a page for our app" is a page."""
    matched = {
        scope for scope in SCOPES if matched_terms(text, rules["scopes"][scope]["terms"])
    }
    if "system" in matched:
        return "system"
    if "component" in matched and set(tasks) <= NARROW_TASKS:
        return "component"
    for scope in ("page", "surface", "component"):
        if scope in matched:
            return scope
    return rules.get("default_scope", "page")


def analyze(
    query: str,
    rules: Mapping,
    task: str | None = None,
    scope: str | None = None,
) -> Request:
    profile = profile_query(query, load_taxonomy())
    if task:
        tasks = [task]
    else:
        tasks = [name for name in TASKS if matched_terms(profile.text, rules["tasks"][name])]
        tasks = tasks or [rules.get("default_task", "create")]
    return Request(
        query=query,
        text=profile.text,
        needs=profile.needs,
        tasks=tuple(tasks),
        scope=scope or infer_scope(profile.text, tasks, rules),
    )


def condition_holds(condition: Mapping, request: Request) -> bool:
    needs = set(request.needs)
    tasks = set(request.tasks)
    checks = {
        "capabilities_any": lambda values: bool(needs & set(values)),
        "capabilities_all": lambda values: set(values) <= needs,
        "capabilities_none": lambda values: not needs & set(values),
        "needs_within": lambda values: needs <= set(values),
        "tasks_any": lambda values: bool(tasks & set(values)),
        "tasks_none": lambda values: not tasks & set(values),
        "scopes_any": lambda values: request.scope in values,
        "terms_any": lambda values: bool(matched_terms(request.text, values)),
        "terms_none": lambda values: not matched_terms(request.text, values),
    }
    return all(checks[key](value) for key, value in condition.items())


def select_rule(rules: Mapping, request: Request) -> Mapping:
    ordered = sorted(rules["rules"], key=lambda rule: -int(rule.get("priority", 0)))
    for rule in ordered:
        if condition_holds(rule.get("when", {}), request):
            return rule
    raise ValueError("routing-rules.json needs a fallback rule with an empty 'when'.")


def entry_candidates(entries: Sequence, request: Request) -> list[str]:
    """Resolve ordered module preferences; object entries apply only when their condition holds."""
    candidates: list[str] = []
    for entry in entries:
        if isinstance(entry, str):
            candidates.append(entry)
        elif condition_holds(entry.get("when", {}), request):
            candidates.append(entry["module"])
    return candidates


def module_member(
    module: Module,
    installed: Mapping[str, SkillRecord],
    owns: Sequence[str],
    reason: str,
) -> Member:
    return Member(
        module=module.id,
        skill=installed[module.id].name,
        owns=sorted(set(owns)),
        reason=reason,
        requires=list(module.requires),
    )


def install_hint(module: Module, agent: str) -> dict[str, str]:
    return {
        "module": module.id,
        "source": module.source_url,
        "install": f'python3 "{SETUP_SCRIPT}" --agent {agent} --only {module.id}',
    }


def incumbent_lead(needs: set[str], reason: str) -> Member:
    return Member(INCUMBENT, None, sorted(needs & set(INCUMBENT_OWNS)) or ["direction"], reason)


def build_brief(
    request: Request,
    rules: Mapping,
    modules: Sequence[Module],
    installed: Mapping[str, SkillRecord],
    dynamic: Sequence[SkillRecord] = (),
    prerequisites: Mapping[str, str] | None = None,
    agent: str = "<host>",
) -> Brief:
    by_id = {module.id: module for module in modules}
    needs = set(request.needs)
    rule = select_rule(rules, request)
    missing: dict[str, Module] = {}

    lead: Member | None = None
    for candidate in entry_candidates(rule["lead"], request):
        if candidate == INCUMBENT:
            lead = incumbent_lead(
                needs,
                "The existing design system or supplied reference stays the visual authority.",
            )
            break
        module = by_id[candidate]
        if candidate in installed:
            owns = set(module.specialties) | ({"direction"} if module.lead_capable else set())
            lead = module_member(module, installed, owns, f"Lead for rule '{rule['id']}'.")
            break
        missing.setdefault(candidate, module)
    if lead is None:
        lead = incumbent_lead(
            needs,
            "No preferred lead is installed; the existing system and core rules lead.",
        )

    team = {lead.module}
    if lead.module == INCUMBENT:
        # The incumbent system is the authority, but specialists may still own
        # the mechanics of an open concern inside it.
        owned: set[str] = set()
        covered = set(INCUMBENT_OWNS)
    else:
        owned = set(lead.owns)
        covered = set(by_id[lead.module].capabilities)

    scope = rules["scopes"][request.scope]
    validation: Member | None = None
    if scope.get("assign_validation", True):
        validation_candidates = [
            module_id
            for module_id in entry_candidates(rule.get("validation", []), request)
            if module_id not in team
        ]
        for module_id in validation_candidates:
            if module_id in installed:
                module = by_id[module_id]
                validation = module_member(
                    module,
                    installed,
                    set(module.specialties),
                    "Validates the integrated result.",
                )
                team.add(module_id)
                owned.update(validation.owns)
                break
        if validation is None and validation_candidates:
            first = by_id[validation_candidates[0]]
            missing.setdefault(first.id, first)

    budget = int(scope["max_specialists"])
    # A page may take a third specialist only when research, motion, and
    # production validation are all independently open.
    extended = scope.get("extended_max_specialists")
    if extended and validation is not None and "motion" in needs and needs & EVIDENCE_NEEDS:
        budget = int(extended)
    specialists: list[Member] = []

    def add(module: Module, owns: set[str], reason: str) -> None:
        if len(specialists) >= budget or module.id in team:
            return
        specialists.append(module_member(module, installed, owns, reason))
        team.add(module.id)
        owned.update(owns)
        covered.update(owns)

    for entry in rule.get("support", []):
        wanted = (needs & set(entry["for"])) - owned
        module = by_id[entry["module"]]
        if not wanted or module.id in team:
            continue
        if module.id not in installed:
            missing.setdefault(module.id, module)
            continue
        add(module, wanted, "Owns " + ", ".join(sorted(wanted)) + ".")

    for need in sorted(needs - covered - owned):
        owners = [
            module
            for module in modules
            if need in module.specialties
            and module.id in installed
            and module.id not in team
            and not module.lead_capable
        ]
        owners.sort(key=lambda module: (module.tier != "core", module.id))
        if owners:
            add(owners[0], {need}, f"Owns {need}, which the lead does not cover.")

    if lead.module == INCUMBENT:
        lead.owns = sorted((needs & set(INCUMBENT_OWNS)) - owned) or ["direction"]

    excluded: list[dict[str, str]] = []
    for entry in rule.get("exclude", []):
        if entry["module"] in installed and entry["module"] not in team:
            excluded.append({"module": entry["module"], "reason": entry["reason"]})
    listed = {entry["module"] for entry in excluded}
    lead_module = by_id.get(lead.module)
    if lead_module is not None and lead_module.lead_capable:
        exclusion_reason = f"Single-lead rule: {lead.skill} owns visual direction."
    elif lead_module is not None:
        exclusion_reason = (
            f"Not needed: {lead.skill} owns this focused task and the existing "
            "design system keeps visual direction."
        )
    else:
        exclusion_reason = "Single-lead rule: the existing design system owns visual direction."
    for module in modules:
        if (
            module.lead_capable
            and module.tier == "core"
            and module.id in installed
            and module.id not in team
            and module.id not in listed
            and needs & set(module.capabilities)
        ):
            excluded.append({"module": module.id, "reason": exclusion_reason})

    members = [lead, *specialists, *([validation] if validation else [])]
    for member in members:
        if member.module != INCUMBENT:
            covered.update(by_id[member.module].capabilities)
    uncovered = sorted(needs - covered)
    candidates = [
        record.name
        for record in sorted(
            dynamic,
            key=lambda record: (-len(set(record.capabilities) & set(uncovered)), record.name),
        )
        if set(record.capabilities) & set(uncovered)
    ][:3]

    prerequisites = prerequisites or {}
    required = sorted({item for member in members for item in member.requires})
    return Brief(
        query=request.query,
        scope=request.scope,
        tasks=list(request.tasks),
        needs=list(request.needs),
        rule=rule["id"],
        rule_description=rule.get("description", ""),
        recipe=rule.get("recipe"),
        lead=lead,
        specialists=specialists,
        validation=validation,
        excluded=excluded,
        missing=[
            install_hint(module, agent) for module in missing.values() if module.id not in team
        ],
        prerequisites={item: prerequisites.get(item, "") for item in required},
        uncovered=uncovered,
        candidates=candidates,
    )


def member_line(role: str, member: Member) -> str:
    skill = f"`{member.skill}`" if member.skill else "existing design system"
    owns = ", ".join(member.owns) or "—"
    return f"| {role} | {skill} | {owns} | {member.reason} |"


def render_markdown(brief: Brief) -> str:
    lines = [
        "# Routing brief (draft)",
        "",
        f'Request: "{brief.query}"',
        f"Scope: {brief.scope} · Task: {', '.join(brief.tasks)} · "
        f"Concerns: {', '.join(brief.needs) or 'none detected'}",
        f"Rule: `{brief.rule}` — {brief.rule_description}",
    ]
    if brief.recipe:
        lines.append(f'Recipe: "{brief.recipe}" in references/workflow-recipes.md')
    lines.extend(["", "| Role | Skill | Owns | Why |", "|---|---|---|---|"])
    lines.append(member_line("Lead", brief.lead))
    lines.extend(member_line("Specialist", member) for member in brief.specialists)
    if brief.validation:
        lines.append(member_line("Validation", brief.validation))
    if brief.excluded:
        lines.extend(["", "Excluded:"])
        lines.extend(f"- `{item['module']}` — {item['reason']}" for item in brief.excluded)
    if brief.prerequisites:
        lines.extend(["", "Check before use:"])
        lines.extend(
            f"- {name}: {description}" for name, description in brief.prerequisites.items()
        )
    if brief.missing:
        lines.extend(["", "Preferred but not installed (ask before installing):"])
        lines.extend(f"- `{item['module']}` — `{item['install']}`" for item in brief.missing)
    if brief.uncovered:
        lines.extend(["", "Uncovered concerns: " + ", ".join(brief.uncovered)])
        if brief.candidates:
            lines.append(
                "Installed candidates to evaluate: "
                + ", ".join(f"`{name}`" for name in brief.candidates)
            )
    lines.extend(
        [
            "",
            "Confirm the brief against the product's design truth. Explicit user direction "
            "and an existing design system outrank this draft.",
        ]
    )
    return "\n".join(lines)


def installed_inventory(
    agent: str,
    cwd: Path,
    modules: Sequence[Module],
    assume_installed: bool,
    config_path: Path,
) -> tuple[dict[str, SkillRecord], list[SkillRecord]]:
    if assume_installed:
        records = {
            module.id: SkillRecord(
                name=module.id,
                description=module.description,
                capabilities=sorted(module.capabilities),
                scope="planned",
                agent_root="planned",
                path="",
                registered=True,
                module_id=module.id,
                tier=module.tier,
                role=module.role,
                source_package=module.package,
            )
            for module in modules
        }
        return records, []
    records = discover(agent, cwd, False, "", config_path)
    installed = {record.module_id: record for record in records if record.module_id}
    dynamic = [record for record in records if not record.registered]
    return installed, dynamic


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--query", required=True, help="The user's UI/UX request.")
    parser.add_argument(
        "--agent",
        choices=(*agent_ids(), "all"),
        default="all",
        help="Host agent whose installed skills are considered (default: all).",
    )
    parser.add_argument("--task", choices=TASKS, help="Override the inferred task.")
    parser.add_argument("--scope", choices=SCOPES, help="Override the inferred scope.")
    parser.add_argument(
        "--assume-installed",
        action="store_true",
        help="Route as if every registered module were installed (planning mode).",
    )
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--rules", type=Path, default=RULES_CONFIG)
    return parser


def main() -> int:
    safe_console()
    args = build_parser().parse_args()
    try:
        rules = load_rules(args.rules.resolve())
        modules = load_modules(args.config.resolve())
        prerequisites = load_prerequisites(args.config.resolve())
        installed, dynamic = installed_inventory(
            args.agent,
            Path.cwd().resolve(),
            modules,
            args.assume_installed,
            args.config.resolve(),
        )
        request = analyze(args.query, rules, args.task, args.scope)
        brief = build_brief(
            request, rules, modules, installed, dynamic, prerequisites, args.agent
        )
    except (OSError, KeyError, ValueError, json.JSONDecodeError) as error:
        print(f"Configuration error: {error}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(asdict(brief), indent=2))
    else:
        print(render_markdown(brief))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
