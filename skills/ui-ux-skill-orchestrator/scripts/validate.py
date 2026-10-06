#!/usr/bin/env python3
"""Validate the UI/UX Skill Orchestrator package and its data-driven catalog."""

from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse

from inventory_ui_skills import (
    AGENTS_CONFIG,
    CAPABILITIES_CONFIG,
    DEFAULT_CONFIG,
    parse_frontmatter,
)
from route import CONDITION_KEYS, INCUMBENT, RULES_CONFIG, SCOPES, TASKS


SKILL_DIR = Path(__file__).resolve().parents[1]
REQUIRED_PATHS = {
    "SKILL.md",
    "agents/openai.yaml",
    "config/agents.json",
    "config/capabilities.json",
    "config/routing-rules.json",
    "config/skill-modules.json",
    "references/capability-map.md",
    "references/synthesis-contract.md",
    "references/workflow-recipes.md",
    "scripts/inventory_ui_skills.py",
    "scripts/route.py",
    "scripts/setup.py",
    "scripts/validate.py",
}
ALLOWED_SKILL_ENTRIES = {"SKILL.md", "agents", "config", "references", "scripts"}
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
REF_PATTERN = re.compile(r"^[A-Za-z0-9._/-]+$")
MAX_ROOT_DEPTH = 8
MIN_PYTHON = (3, 9)


def load_json(path: Path, errors: list[str]) -> dict | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"Invalid {path.name}: {error}")
        return None
    if not isinstance(payload, dict):
        errors.append(f"{path.name} must contain a JSON object.")
        return None
    if payload.get("schema_version") != 1:
        errors.append(f"{path.name} schema_version must be 1.")
    return payload


def is_term_list(value: object) -> bool:
    return isinstance(value, list) and all(
        isinstance(item, str) and item.strip() and item == item.lower() for item in value
    )


def duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    repeated: set[str] = set()
    for value in values:
        (repeated if value in seen else seen).add(value)
    return sorted(repeated)


def is_safe_relative(path_text: object) -> bool:
    if not isinstance(path_text, str) or not path_text.strip():
        return False
    path = PurePosixPath(path_text)
    return not path.is_absolute() and ".." not in path.parts and "\\" not in path_text


def validate_frontmatter(errors: list[str]) -> None:
    manifest = SKILL_DIR / "SKILL.md"
    parsed = parse_frontmatter(manifest)
    if not parsed:
        errors.append("SKILL.md must contain name and description frontmatter.")
        return
    name, description = parsed
    if not NAME_PATTERN.fullmatch(name) or len(name) > 64:
        errors.append("Skill name must be lowercase hyphen-case and at most 64 characters.")
    if name != SKILL_DIR.name:
        errors.append("Skill folder and frontmatter name must match for portability.")
    if not description.strip():
        errors.append("Skill description must not be empty.")
    if len(description) > 1024:
        errors.append("Skill description must be at most 1024 characters.")
    if len(manifest.read_text(encoding="utf-8").splitlines()) > 500:
        errors.append("SKILL.md must remain under 500 lines.")


def validate_file_set(errors: list[str]) -> None:
    present = {
        path.relative_to(SKILL_DIR).as_posix()
        for path in SKILL_DIR.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }
    missing = sorted(REQUIRED_PATHS - present)
    if missing:
        errors.append("Missing required files: " + ", ".join(missing))
    unexpected = sorted(
        path.name
        for path in SKILL_DIR.iterdir()
        if path.name not in ALLOWED_SKILL_ENTRIES and path.name != "__pycache__"
    )
    if unexpected:
        errors.append("Unexpected runtime entries: " + ", ".join(unexpected))


def validate_capabilities(errors: list[str]) -> set[str]:
    """Validate the taxonomy and return its capability identifiers."""
    payload = load_json(CAPABILITIES_CONFIG, errors)
    if payload is None:
        return set()
    capabilities = payload.get("capabilities")
    if not isinstance(capabilities, dict) or not capabilities:
        errors.append("capabilities.json must define a non-empty capabilities object.")
        return set()
    for capability, spec in capabilities.items():
        if not NAME_PATTERN.fullmatch(capability):
            errors.append(f"Capability id must be hyphen-case: {capability!r}")
        if not isinstance(spec, dict):
            errors.append(f"Capability {capability} must be an object.")
            continue
        if not isinstance(spec.get("label"), str) or not spec["label"].strip():
            errors.append(f"Capability {capability} needs a label.")
        signals = spec.get("signals")
        query_terms = spec.get("query_terms", [])
        if not is_term_list(signals) or not signals:
            errors.append(f"Capability {capability} needs lowercase signals.")
            continue
        if not is_term_list(query_terms):
            errors.append(f"Capability {capability} query_terms must be lowercase strings.")
            continue
        repeated = duplicates([*signals, *query_terms])
        if repeated:
            errors.append(f"Capability {capability} repeats terms: {', '.join(repeated)}")
    for key in ("ui_terms", "non_ui_terms", "stopwords"):
        values = payload.get(key)
        if not is_term_list(values) or not values:
            errors.append(f"capabilities.json {key} must be a non-empty lowercase list.")
            continue
        repeated = duplicates(values)
        if repeated:
            errors.append(f"capabilities.json {key} repeats: {', '.join(repeated)}")
    return set(capabilities)


def validate_agents(errors: list[str]) -> None:
    payload = load_json(AGENTS_CONFIG, errors)
    if payload is None:
        return
    agents = payload.get("agents")
    if not isinstance(agents, dict) or not agents:
        errors.append("agents.json must define a non-empty agents object.")
        return
    for agent_id, spec in agents.items():
        if not NAME_PATTERN.fullmatch(agent_id) or agent_id == "all":
            errors.append(f"Agent id must be hyphen-case and not 'all': {agent_id!r}")
        if not isinstance(spec, dict) or not isinstance(spec.get("label"), str):
            errors.append(f"Agent {agent_id} needs an object with a label.")
            continue
        for scope in ("project", "global"):
            roots = spec.get(scope)
            if not isinstance(roots, list) or not roots:
                errors.append(f"Agent {agent_id}.{scope} must be a non-empty list.")
                continue
            for root in roots:
                path = root.get("path") if isinstance(root, dict) else root
                if not is_safe_relative(path):
                    errors.append(f"Agent {agent_id}.{scope} has an unsafe path: {root!r}")
                if isinstance(root, dict):
                    depth = root.get("depth", 3)
                    if not isinstance(depth, int) or not 1 <= depth <= MAX_ROOT_DEPTH:
                        errors.append(
                            f"Agent {agent_id}.{scope} depth must be 1-{MAX_ROOT_DEPTH}."
                        )
                    if not isinstance(root.get("include_hidden", False), bool):
                        errors.append(f"Agent {agent_id}.{scope} include_hidden must be boolean.")


def validate_source(module_id: str, source: object, errors: list[str]) -> None:
    if not isinstance(source, dict):
        errors.append(f"{module_id}.source must be an object.")
        return
    required = {"package", "skill", "url"}
    if not required <= set(source) or not set(source) <= required | {"path", "ref"}:
        errors.append(
            f"{module_id}.source needs package, skill, and url, plus optional path and ref."
        )
        return
    package = source["package"]
    install_skill = source["skill"]
    source_url = source["url"]
    if not isinstance(package, str) or not re.fullmatch(r"[^/\s]+/[^/\s]+", package):
        errors.append(f"{module_id}.source.package must use owner/repository.")
        return
    if not isinstance(install_skill, str) or not NAME_PATTERN.fullmatch(install_skill):
        errors.append(f"{module_id}.source.skill must be lowercase hyphen-case.")
    parsed_url = urlparse(source_url) if isinstance(source_url, str) else None
    if parsed_url is None or parsed_url.scheme != "https" or parsed_url.netloc != "github.com":
        errors.append(f"{module_id}.source.url must be an HTTPS GitHub URL.")
    elif parsed_url.path.strip("/").lower() != package.lower():
        errors.append(f"{module_id}.source.url must point to {package}.")
    if "path" in source and not is_safe_relative(source["path"]):
        errors.append(f"{module_id}.source.path must be a relative path inside the repository.")
    if "ref" in source and (
        not isinstance(source["ref"], str) or not REF_PATTERN.fullmatch(source["ref"])
    ):
        errors.append(f"{module_id}.source.ref must be a branch, tag, or commit.")


def validate_modules(errors: list[str], capabilities: set[str]) -> set[str]:
    """Validate the module manifest and return the registered module identifiers."""
    payload = load_json(DEFAULT_CONFIG, errors)
    if payload is None:
        return set()
    portfolio_version = payload.get("portfolio_version")
    if not isinstance(portfolio_version, str) or not re.fullmatch(
        r"\d+\.\d+\.\d+",
        portfolio_version,
    ):
        errors.append("Module manifest portfolio_version must use semantic X.Y.Z.")
    prerequisites = payload.get("prerequisites", {})
    if not isinstance(prerequisites, dict) or not all(
        NAME_PATTERN.fullmatch(key) and isinstance(value, str) and value.strip()
        for key, value in prerequisites.items()
    ):
        errors.append("Module manifest prerequisites must map hyphen-case ids to descriptions.")
        prerequisites = {}
    modules = payload.get("modules")
    if not isinstance(modules, list) or not modules:
        errors.append("Module manifest must contain a non-empty modules list.")
        return set()

    known_names: dict[str, str] = {}
    module_ids: set[str] = set()
    core_roles: set[str] = set()
    required = {
        "id",
        "display_name",
        "tier",
        "role",
        "description",
        "aliases",
        "capabilities",
        "specialties",
        "source",
    }
    for index, module in enumerate(modules):
        label = f"modules[{index}]"
        if not isinstance(module, dict):
            errors.append(f"{label} must be an object.")
            continue
        missing = sorted(required - set(module))
        if missing:
            errors.append(f"{label} is missing: {', '.join(missing)}")
            continue

        module_id = module["id"]
        if not isinstance(module_id, str) or not NAME_PATTERN.fullmatch(module_id):
            errors.append(f"{label}.id must be lowercase hyphen-case.")
            continue
        module_ids.add(module_id)
        for field in ("display_name", "description"):
            if not isinstance(module[field], str) or not module[field].strip():
                errors.append(f"{module_id}.{field} must be a non-empty string.")
        if module["tier"] not in {"core", "integration"}:
            errors.append(f"{module_id}.tier must be core or integration.")
        if not isinstance(module["role"], str) or not module["role"].strip():
            errors.append(f"{module_id}.role must be a non-empty string.")
        elif module["tier"] == "core":
            if module["role"] in core_roles:
                errors.append(f"Core role is duplicated: {module['role']}")
            core_roles.add(module["role"])
        if not isinstance(module.get("lead_capable", False), bool):
            errors.append(f"{module_id}.lead_capable must be boolean.")

        aliases = module["aliases"]
        if not isinstance(aliases, list):
            errors.append(f"{module_id}.aliases must be a list.")
            aliases = []
        for name in [module_id, *aliases]:
            if not isinstance(name, str) or not NAME_PATTERN.fullmatch(name):
                errors.append(f"{module_id} contains an invalid alias: {name!r}")
                continue
            if name in known_names:
                errors.append(
                    f"Module name or alias {name!r} is shared by "
                    f"{known_names[name]} and {module_id}."
                )
            known_names[name] = module_id

        module_capabilities = module["capabilities"]
        specialties = module["specialties"]
        if not isinstance(module_capabilities, list) or not module_capabilities:
            errors.append(f"{module_id}.capabilities must be a non-empty list.")
            module_capabilities = []
        if not isinstance(specialties, list):
            errors.append(f"{module_id}.specialties must be a list.")
            specialties = []
        unknown = sorted(set(module_capabilities) - capabilities)
        if capabilities and unknown:
            errors.append(f"{module_id} has unknown capabilities: {', '.join(unknown)}")
        if not set(specialties).issubset(module_capabilities):
            errors.append(f"{module_id}.specialties must be a capability subset.")
        if module["tier"] == "integration" and not specialties:
            errors.append(f"{module_id} is an integration and needs a gating specialty.")
        if not is_term_list(module.get("keywords", [])):
            errors.append(f"{module_id}.keywords must be lowercase strings.")
        requires = module.get("requires", [])
        if not isinstance(requires, list) or not set(requires) <= set(prerequisites):
            errors.append(f"{module_id}.requires must list declared prerequisites.")
        validate_source(module_id, module["source"], errors)
    return module_ids


def recipe_headings() -> set[str]:
    path = SKILL_DIR / "references" / "workflow-recipes.md"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return set()
    return {match.strip() for match in re.findall(r"^## (.+)$", text, re.MULTILINE)}


def validate_condition(
    label: str,
    condition: object,
    capabilities: set[str],
    errors: list[str],
) -> None:
    if not isinstance(condition, dict):
        errors.append(f"{label} must be an object.")
        return
    unknown = sorted(set(condition) - CONDITION_KEYS)
    if unknown:
        errors.append(f"{label} has unknown keys: {', '.join(unknown)}")
    allowed = {
        "capabilities_any": capabilities,
        "capabilities_all": capabilities,
        "capabilities_none": capabilities,
        "needs_within": capabilities,
        "tasks_any": set(TASKS),
        "tasks_none": set(TASKS),
        "scopes_any": set(SCOPES),
    }
    for key, value in condition.items():
        if not isinstance(value, list) or not value:
            errors.append(f"{label}.{key} must be a non-empty list.")
            continue
        if key in allowed and capabilities and not set(value) <= allowed[key]:
            errors.append(f"{label}.{key} has unknown values: {sorted(set(value) - allowed[key])}")
        if key.startswith("terms_") and not is_term_list(value):
            errors.append(f"{label}.{key} must be lowercase strings.")


def validate_preferences(
    label: str,
    entries: list,
    allow_incumbent: bool,
    capabilities: set[str],
    module_ids: set[str],
    errors: list[str],
) -> None:
    """Check an ordered preference list of module ids or {module, when} objects."""
    for entry in entries:
        module_id = entry.get("module") if isinstance(entry, dict) else entry
        if module_id == INCUMBENT and allow_incumbent:
            continue
        if module_id not in module_ids:
            errors.append(f"{label} references unknown module {module_id!r}.")
        if isinstance(entry, dict):
            validate_condition(f"{label}.when", entry.get("when"), capabilities, errors)


def validate_rules(errors: list[str], capabilities: set[str], module_ids: set[str]) -> None:
    payload = load_json(RULES_CONFIG, errors)
    if payload is None:
        return
    tasks = payload.get("tasks")
    if not isinstance(tasks, dict) or set(tasks) != set(TASKS):
        errors.append(f"routing-rules.json tasks must define exactly: {', '.join(TASKS)}")
    elif not all(is_term_list(terms) and terms for terms in tasks.values()):
        errors.append("routing-rules.json task terms must be non-empty lowercase lists.")
    scopes = payload.get("scopes")
    if not isinstance(scopes, dict) or set(scopes) != set(SCOPES):
        errors.append(f"routing-rules.json scopes must define exactly: {', '.join(SCOPES)}")
    else:
        for scope, spec in scopes.items():
            budget = spec.get("max_specialists") if isinstance(spec, dict) else None
            extended = spec.get("extended_max_specialists", budget) if isinstance(spec, dict) else None
            if not isinstance(budget, int) or budget < 0:
                errors.append(f"Scope {scope}.max_specialists must be a non-negative integer.")
            elif not isinstance(extended, int) or extended < budget:
                errors.append(f"Scope {scope}.extended_max_specialists must be >= max_specialists.")
            if not isinstance(spec, dict) or not is_term_list(spec.get("terms")):
                errors.append(f"Scope {scope}.terms must be lowercase strings.")
            elif not isinstance(spec.get("assign_validation", True), bool):
                errors.append(f"Scope {scope}.assign_validation must be boolean.")
    if payload.get("default_scope") not in SCOPES:
        errors.append("routing-rules.json default_scope must be a defined scope.")
    if payload.get("default_task") not in TASKS:
        errors.append("routing-rules.json default_task must be a defined task.")

    rules = payload.get("rules")
    if not isinstance(rules, list) or not rules:
        errors.append("routing-rules.json must contain a non-empty rules list.")
        return
    headings = recipe_headings()
    seen: set[str] = set()
    fallbacks: list[tuple[int, str]] = []
    priorities: list[int] = []
    for index, rule in enumerate(rules):
        label = f"rules[{index}]"
        if not isinstance(rule, dict):
            errors.append(f"{label} must be an object.")
            continue
        rule_id = rule.get("id")
        if not isinstance(rule_id, str) or not NAME_PATTERN.fullmatch(rule_id):
            errors.append(f"{label}.id must be hyphen-case.")
            continue
        label = f"rule {rule_id}"
        if rule_id in seen:
            errors.append(f"Duplicate rule id: {rule_id}")
        seen.add(rule_id)
        priority = rule.get("priority")
        if not isinstance(priority, int):
            errors.append(f"{label}.priority must be an integer.")
            priority = 0
        priorities.append(priority)
        when = rule.get("when", {})
        validate_condition(f"{label}.when", when, capabilities, errors)
        if when == {}:
            fallbacks.append((priority, rule_id))

        lead = rule.get("lead")
        if not isinstance(lead, list) or not lead:
            errors.append(f"{label}.lead must be a non-empty list.")
        else:
            validate_preferences(f"{label}.lead", lead, True, capabilities, module_ids, errors)
        validation = rule.get("validation", [])
        if not isinstance(validation, list):
            errors.append(f"{label}.validation must be a list.")
        else:
            validate_preferences(
                f"{label}.validation", validation, False, capabilities, module_ids, errors
            )
        for entry in rule.get("support", []):
            if not isinstance(entry, dict) or entry.get("module") not in module_ids:
                errors.append(f"{label}.support references an unknown module: {entry!r}")
                continue
            wanted = entry.get("for")
            if not isinstance(wanted, list) or not wanted or (
                capabilities and not set(wanted) <= capabilities
            ):
                errors.append(f"{label}.support {entry['module']} needs known 'for' capabilities.")
        for entry in rule.get("exclude", []):
            if (
                not isinstance(entry, dict)
                or entry.get("module") not in module_ids
                or not isinstance(entry.get("reason"), str)
            ):
                errors.append(f"{label}.exclude entries need a known module and a reason.")
        recipe = rule.get("recipe")
        if recipe is not None and recipe not in headings:
            errors.append(f"{label}.recipe {recipe!r} is not a heading in workflow-recipes.md.")

    if len(fallbacks) != 1:
        errors.append("routing-rules.json needs exactly one fallback rule with an empty 'when'.")
    elif fallbacks[0][0] != min(priorities) or priorities.count(fallbacks[0][0]) > 1:
        errors.append("The fallback rule must have the single lowest priority.")


def validate_markdown_links(errors: list[str]) -> None:
    for markdown in SKILL_DIR.rglob("*.md"):
        text = markdown.read_text(encoding="utf-8")
        for target in MARKDOWN_LINK_PATTERN.findall(text):
            clean = target.strip().strip("<>")
            if (
                not clean
                or clean.startswith(("#", "http://", "https://", "mailto:"))
            ):
                continue
            path_text = clean.split("#", 1)[0]
            resolved = (markdown.parent / path_text).resolve()
            try:
                resolved.relative_to(SKILL_DIR)
            except ValueError:
                errors.append(
                    f"{markdown.relative_to(SKILL_DIR)} links outside the skill: {target}"
                )
                continue
            if not resolved.exists():
                errors.append(
                    f"{markdown.relative_to(SKILL_DIR)} has a missing link: {target}"
                )


def validate_openai_metadata(errors: list[str]) -> None:
    path = SKILL_DIR / "agents" / "openai.yaml"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        errors.append(f"Cannot read agents/openai.yaml: {error}")
        return
    values = dict(
        re.findall(r'^\s{2}([a-z_]+):\s+"([^"]*)"\s*$', text, re.MULTILINE)
    )
    for field in ("display_name", "short_description", "default_prompt"):
        if field not in values:
            errors.append(f"agents/openai.yaml is missing quoted {field}.")
    short = values.get("short_description", "")
    if short and not 25 <= len(short) <= 64:
        errors.append("short_description must contain 25 to 64 characters.")
    prompt = values.get("default_prompt", "")
    if prompt and "$ui-ux-skill-orchestrator" not in prompt:
        errors.append("default_prompt must mention $ui-ux-skill-orchestrator.")
    if not re.search(
        r"^\s{2}allow_implicit_invocation:\s+true\s*$",
        text,
        re.MULTILINE,
    ):
        errors.append("allow_implicit_invocation must be true.")


def validate_python(errors: list[str]) -> None:
    for path in sorted((SKILL_DIR / "scripts").glob("*.py")):
        text = path.read_text(encoding="utf-8")
        if not text.startswith("#!/usr/bin/env python3"):
            errors.append(f"{path.name} must start with a portable Python shebang.")
        if "from __future__ import annotations" not in text:
            errors.append(f"{path.name} must import annotations from __future__ for Python 3.9.")
        try:
            ast.parse(text, filename=str(path), feature_version=MIN_PYTHON)
        except SyntaxError as error:
            errors.append(
                f"{path.name} is not valid Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]} syntax: {error}"
            )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    errors: list[str] = []
    validate_file_set(errors)
    validate_frontmatter(errors)
    capabilities = validate_capabilities(errors)
    validate_agents(errors)
    module_ids = validate_modules(errors, capabilities)
    validate_rules(errors, capabilities, module_ids)
    validate_markdown_links(errors)
    validate_openai_metadata(errors)
    validate_python(errors)

    if args.json:
        print(json.dumps({"valid": not errors, "errors": errors}, indent=2))
    elif errors:
        print("Validation failed:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("Skill package is valid.")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
