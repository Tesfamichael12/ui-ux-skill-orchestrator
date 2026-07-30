#!/usr/bin/env python3
"""Validate the UI/UX Skill Orchestrator package and module manifest."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

from inventory_ui_skills import CAPABILITY_SIGNALS, DEFAULT_CONFIG, parse_frontmatter


SKILL_DIR = Path(__file__).resolve().parents[1]
REQUIRED_PATHS = {
    "SKILL.md",
    "agents/openai.yaml",
    "config/skill-modules.json",
    "references/capability-map.md",
    "references/synthesis-contract.md",
    "references/workflow-recipes.md",
    "scripts/inventory_ui_skills.py",
    "scripts/setup.py",
    "scripts/validate.py",
}
ALLOWED_SKILL_ENTRIES = {"SKILL.md", "agents", "config", "references", "scripts"}
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


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
        str(path.relative_to(SKILL_DIR))
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


def validate_modules(errors: list[str]) -> None:
    try:
        payload = json.loads(DEFAULT_CONFIG.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"Invalid module manifest: {error}")
        return
    if payload.get("schema_version") != 1:
        errors.append("Module manifest schema_version must be 1.")
    modules = payload.get("modules")
    if not isinstance(modules, list) or not modules:
        errors.append("Module manifest must contain a non-empty modules list.")
        return

    known_names: dict[str, str] = {}
    allowed_capabilities = set(CAPABILITY_SIGNALS)
    core_roles: set[str] = set()
    for index, module in enumerate(modules):
        label = f"modules[{index}]"
        if not isinstance(module, dict):
            errors.append(f"{label} must be an object.")
            continue
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
        missing = sorted(required - set(module))
        if missing:
            errors.append(f"{label} is missing: {', '.join(missing)}")
            continue

        module_id = module["id"]
        if not isinstance(module_id, str) or not NAME_PATTERN.fullmatch(module_id):
            errors.append(f"{label}.id must be lowercase hyphen-case.")
            continue
        if module["tier"] not in {"core", "integration"}:
            errors.append(f"{module_id}.tier must be core or integration.")
        if not isinstance(module["role"], str) or not module["role"].strip():
            errors.append(f"{module_id}.role must be a non-empty string.")
        elif module["tier"] == "core":
            if module["role"] in core_roles:
                errors.append(f"Core role is duplicated: {module['role']}")
            core_roles.add(module["role"])

        aliases = module["aliases"]
        if not isinstance(aliases, list):
            errors.append(f"{module_id}.aliases must be a list.")
            aliases = []
        names = [module_id, *aliases]
        for name in names:
            if not isinstance(name, str) or not NAME_PATTERN.fullmatch(name):
                errors.append(f"{module_id} contains an invalid alias: {name!r}")
                continue
            if name in known_names:
                errors.append(
                    f"Module name or alias {name!r} is shared by "
                    f"{known_names[name]} and {module_id}."
                )
            known_names[name] = module_id

        capabilities = module["capabilities"]
        specialties = module["specialties"]
        if not isinstance(capabilities, list) or not capabilities:
            errors.append(f"{module_id}.capabilities must be a non-empty list.")
            capabilities = []
        if not isinstance(specialties, list):
            errors.append(f"{module_id}.specialties must be a list.")
            specialties = []
        unknown = sorted(set(capabilities) - allowed_capabilities)
        if unknown:
            errors.append(
                f"{module_id} has unknown capabilities: {', '.join(unknown)}"
            )
        if not set(specialties).issubset(capabilities):
            errors.append(f"{module_id}.specialties must be a capability subset.")

        source = module["source"]
        if not isinstance(source, dict):
            errors.append(f"{module_id}.source must be an object.")
            continue
        if set(source) != {"package", "skill", "url"}:
            errors.append(
                f"{module_id}.source must contain exactly package, skill, and url."
            )
            continue
        if not re.fullmatch(r"[^/\s]+/[^/\s]+", source["package"]):
            errors.append(f"{module_id}.source.package must use owner/repository.")
        if not NAME_PATTERN.fullmatch(source["skill"]):
            errors.append(f"{module_id}.source.skill must be lowercase hyphen-case.")
        parsed_url = urlparse(source["url"])
        if parsed_url.scheme != "https" or parsed_url.netloc != "github.com":
            errors.append(f"{module_id}.source.url must be an HTTPS GitHub URL.")


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
        try:
            compile(text, str(path), "exec")
        except SyntaxError as error:
            errors.append(f"{path.name} has invalid Python syntax: {error}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    errors: list[str] = []
    validate_file_set(errors)
    validate_frontmatter(errors)
    validate_modules(errors)
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
