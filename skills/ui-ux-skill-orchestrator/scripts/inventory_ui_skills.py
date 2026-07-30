#!/usr/bin/env python3
"""Discover and rank UI/UX Agent Skills using a modular portfolio manifest."""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Iterator


SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = SKILL_DIR / "config" / "skill-modules.json"
ORCHESTRATOR_NAMES = {"ui-ux-skill-orchestrator"}
IGNORED_DIRECTORIES = {
    ".git",
    "__pycache__",
    "__pypackages__",
    "node_modules",
    "vendor",
}

UI_TERMS = {
    "accessibility",
    "animation",
    "color",
    "colour",
    "component",
    "dashboard",
    "design",
    "figma",
    "font",
    "front-end",
    "frontend",
    "interface",
    "layout",
    "motion",
    "palette",
    "responsive",
    "spacing",
    "stitch",
    "tailwind",
    "typography",
    "ui",
    "ux",
    "visual",
}

CAPABILITY_SIGNALS = {
    "direction": {"aesthetic", "brand", "creative", "direction", "identity", "visual"},
    "ux": {"flow", "information architecture", "research", "usability", "user experience", "ux"},
    "typography": {"font", "typeface", "typography", "typeset"},
    "color": {"color", "colour", "contrast", "palette"},
    "layout": {"alignment", "grid", "layout", "spacing", "spatial"},
    "components": {"button", "component", "form", "interaction state", "modal", "table"},
    "motion": {"animation", "easing", "gesture", "motion", "spring", "transition"},
    "accessibility": {"a11y", "accessibility", "aria", "keyboard", "screen reader", "wcag"},
    "responsive": {"adaptive", "breakpoint", "mobile", "responsive"},
    "performance": {"bundle", "performance", "render", "speed"},
    "audit": {"audit", "critique", "polish", "review"},
    "design-system": {"design system", "design-system", "token"},
    "data-viz": {"chart", "dashboard", "data visualization", "visualization"},
    "figma": {"figma"},
    "stitch": {"google stitch", "stitch"},
    "implementation": {"css", "frontend", "html", "next.js", "react", "tailwind", "vue"},
}

QUERY_ALIASES = {
    "typography": {"font", "fonts", "type", "typeface", "typefaces", "typography"},
    "color": {"color", "colors", "colour", "colours", "palette", "palettes", "theme"},
    "layout": {"alignment", "density", "grid", "layout", "space", "spacing"},
    "components": {
        "button",
        "buttons",
        "card",
        "cards",
        "component",
        "components",
        "dialog",
        "form",
        "input",
        "modal",
        "table",
    },
    "motion": {
        "animate",
        "animated",
        "animation",
        "animations",
        "gesture",
        "motion",
        "smooth",
        "transition",
        "transitions",
    },
    "accessibility": {
        "a11y",
        "accessibility",
        "accessible",
        "aria",
        "contrast",
        "focus",
        "keyboard",
        "wcag",
    },
    "responsive": {"adaptive", "breakpoint", "mobile", "responsive"},
    "performance": {"fast", "jank", "optimize", "performance", "slow"},
    "audit": {"audit", "critique", "polish", "review"},
    "design-system": {"design-system", "system", "token", "tokens"},
    "data-viz": {"chart", "dashboard", "graph", "visualization"},
    "figma": {"figma"},
    "stitch": {"stitch"},
    "ux": {"flow", "journey", "research", "usability", "ux"},
    "direction": {"aesthetic", "brand", "design", "redesign", "style", "visual"},
    "implementation": {"css", "frontend", "html", "next", "react", "tailwind", "vue"},
}

AGENT_ROOTS = {
    "codex": {
        "project": [".agents/skills", ".codex/skills"],
        "global": [".agents/skills", ".codex/skills"],
    },
    "claude-code": {
        "project": [".agents/skills", ".claude/skills"],
        "global": [".agents/skills", ".claude/skills"],
    },
    "cursor": {
        "project": [".agents/skills", ".cursor/skills"],
        "global": [".agents/skills", ".cursor/skills"],
    },
    "antigravity": {
        "project": [".agents/skills", ".gemini/skills"],
        "global": [
            ".agents/skills",
            ".gemini/config/skills",
            ".gemini/antigravity/skills",
        ],
    },
    "gemini-cli": {
        "project": [".agents/skills", ".gemini/skills"],
        "global": [".agents/skills", ".gemini/skills", ".gemini/config/skills"],
    },
    "opencode": {
        "project": [".agents/skills", ".config/opencode/skills"],
        "global": [".agents/skills", ".config/opencode/skills"],
    },
    "github-copilot": {
        "project": [".agents/skills", ".github/skills"],
        "global": [".agents/skills", ".copilot/skills"],
    },
}


@dataclass(frozen=True)
class Module:
    id: str
    display_name: str
    tier: str
    role: str
    description: str
    aliases: tuple[str, ...]
    capabilities: tuple[str, ...]
    specialties: tuple[str, ...]
    package: str
    install_skill: str
    source_url: str

    @property
    def names(self) -> set[str]:
        return {self.id, self.install_skill, *self.aliases}


@dataclass(frozen=True)
class SkillRecord:
    name: str
    description: str
    capabilities: list[str]
    scope: str
    agent_root: str
    path: str
    registered: bool
    module_id: str | None = None
    tier: str | None = None
    role: str | None = None
    source_package: str | None = None
    score: int = 0


def load_modules(config_path: Path = DEFAULT_CONFIG) -> list[Module]:
    """Load portfolio modules from JSON without external dependencies."""
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    modules: list[Module] = []
    for item in payload.get("modules", []):
        source = item["source"]
        modules.append(
            Module(
                id=item["id"],
                display_name=item["display_name"],
                tier=item["tier"],
                role=item["role"],
                description=item["description"],
                aliases=tuple(item.get("aliases", [])),
                capabilities=tuple(item["capabilities"]),
                specialties=tuple(item.get("specialties", [])),
                package=source["package"],
                install_skill=source["skill"],
                source_url=source["url"],
            )
        )
    return modules


def module_index(modules: Iterable[Module]) -> dict[str, Module]:
    """Map canonical names and aliases to their module."""
    index: dict[str, Module] = {}
    for module in modules:
        for name in module.names:
            index[name] = module
    return index


def normalize_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def parse_frontmatter(path: Path) -> tuple[str, str] | None:
    """Parse required skill metadata with a deliberately small YAML subset."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        return None
    if not lines or lines[0].strip() != "---":
        return None

    end = next(
        (index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---"),
        None,
    )
    if end is None:
        return None

    frontmatter = lines[1:end]
    name = ""
    description = ""
    index = 0
    while index < len(frontmatter):
        line = frontmatter[index]
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not match:
            index += 1
            continue
        key, value = match.group(1), match.group(2)
        if key == "name":
            name = normalize_scalar(value)
        elif key == "description":
            if value in {"|", "|-", ">", ">-"}:
                continuation: list[str] = []
                index += 1
                while index < len(frontmatter):
                    nested = frontmatter[index]
                    if nested and not nested[0].isspace():
                        index -= 1
                        break
                    continuation.append(nested.strip())
                    index += 1
                description = " ".join(part for part in continuation if part)
            else:
                description = normalize_scalar(value)
        index += 1

    if not name or not description:
        return None
    return name, description


def find_workspace_root(cwd: Path) -> Path:
    for candidate in (cwd, *cwd.parents):
        if (candidate / ".git").exists():
            return candidate
    return cwd


def selected_agents(agent: str) -> list[str]:
    return list(AGENT_ROOTS) if agent == "all" else [agent]


def root_specs(agent: str, cwd: Path) -> list[tuple[Path, str, str]]:
    """Return project roots before global roots so local overrides win."""
    home = Path.home()
    workspace = find_workspace_root(cwd)
    specs: list[tuple[Path, str, str]] = []

    for agent_name in selected_agents(agent):
        roots = AGENT_ROOTS[agent_name]
        for base in dict.fromkeys([cwd, workspace]):
            for relative in roots["project"]:
                specs.append((base / relative, "project", f"{agent_name}:project"))
        for relative in roots["global"]:
            specs.append((home / relative, "global", f"{agent_name}:global"))

    unique: list[tuple[Path, str, str]] = []
    seen: set[Path] = set()
    for path, scope, label in specs:
        expanded = path.expanduser()
        if expanded in seen:
            continue
        seen.add(expanded)
        unique.append((expanded, scope, label))
    return unique


def iter_skill_manifests(root: Path, max_depth: int = 3) -> Iterator[Path]:
    """Yield SKILL.md files without traversing dependency or VCS trees."""
    if not root.is_dir():
        return
    root_depth = len(root.parts)
    for current, directories, files in os.walk(root):
        current_path = Path(current)
        depth = len(current_path.parts) - root_depth
        directories[:] = [
            name
            for name in directories
            if name not in IGNORED_DIRECTORIES
            and not name.startswith(".")
            and depth < max_depth
        ]
        if "SKILL.md" in files:
            yield current_path / "SKILL.md"


def contains_signal(haystack: str, signal: str) -> bool:
    pattern = rf"(?<![a-z0-9]){re.escape(signal)}(?![a-z0-9])"
    return re.search(pattern, haystack) is not None


def classify(name: str, description: str, registry: dict[str, Module]) -> list[str]:
    module = registry.get(name)
    if module:
        return sorted(module.capabilities)

    capabilities: set[str] = set()
    haystack = f"{name} {description}".lower()
    for capability, signals in CAPABILITY_SIGNALS.items():
        if any(contains_signal(haystack, signal) for signal in signals):
            capabilities.add(capability)
    return sorted(capabilities)


def is_ui_skill(name: str, description: str, capabilities: Iterable[str]) -> bool:
    haystack = f"{name} {description}".lower()
    return bool(set(capabilities)) and any(
        contains_signal(haystack, term) for term in UI_TERMS
    )


def query_capabilities(query: str) -> set[str]:
    tokens = set(re.findall(r"[a-z0-9-]+", query.lower()))
    selected: set[str] = set()
    for capability, aliases in QUERY_ALIASES.items():
        if tokens.intersection(aliases):
            selected.add(capability)
    return selected


def score_record(record: SkillRecord, query: str, registry: dict[str, Module]) -> int:
    if not query:
        return 0
    needs = query_capabilities(query)
    score = len(needs.intersection(record.capabilities)) * 8
    module = registry.get(record.name)
    if module:
        score += len(needs.intersection(module.specialties)) * 12
    query_tokens = set(re.findall(r"[a-z0-9-]+", query.lower()))
    text_tokens = set(
        re.findall(r"[a-z0-9-]+", f"{record.name} {record.description}".lower())
    )
    score += len(query_tokens.intersection(text_tokens))
    if record.name in query.lower():
        score += 12
    return score


def discover(
    agent: str,
    cwd: Path,
    include_all: bool,
    query: str,
    config_path: Path = DEFAULT_CONFIG,
) -> list[SkillRecord]:
    modules = load_modules(config_path)
    registry = module_index(modules)
    records_by_name: dict[str, SkillRecord] = {}

    for root, scope, label in root_specs(agent, cwd):
        for manifest in iter_skill_manifests(root):
            parsed = parse_frontmatter(manifest)
            if not parsed:
                continue
            name, description = parsed
            if name in ORCHESTRATOR_NAMES:
                continue
            capabilities = classify(name, description, registry)
            if not include_all and not is_ui_skill(name, description, capabilities):
                continue
            module = registry.get(name)
            record = SkillRecord(
                name=name,
                description=description,
                capabilities=capabilities,
                scope=scope,
                agent_root=label,
                path=str(manifest.parent.resolve()),
                registered=module is not None,
                module_id=module.id if module else None,
                tier=module.tier if module else None,
                role=module.role if module else None,
                source_package=module.package if module else None,
            )
            records_by_name.setdefault(name, record)

    records = [
        SkillRecord(
            **{
                **asdict(record),
                "score": score_record(record, query, registry),
            }
        )
        for record in records_by_name.values()
    ]
    if query:
        records.sort(key=lambda item: (-item.score, item.name))
    else:
        records.sort(key=lambda item: (not item.registered, item.name))
    return records


def installed_module_ids(
    agent: str,
    cwd: Path,
    config_path: Path = DEFAULT_CONFIG,
) -> set[str]:
    return {
        record.module_id
        for record in discover(agent, cwd, True, "", config_path)
        if record.module_id
    }


def markdown(records: list[SkillRecord], query: str) -> str:
    title = "# UI/UX skill inventory"
    if query:
        title += f'\n\nRanked for: "{query}"'
    lines = [
        title,
        "",
        "| Skill | Score | Module | Tier | Role | Capabilities | Scope | Path |",
        "|---|---:|---|---|---|---|---|---|",
    ]
    for record in records:
        capabilities = ", ".join(record.capabilities) or "unclassified"
        lines.append(
            f"| `{record.name}` | {record.score} | "
            f"{record.module_id or 'dynamic'} | {record.tier or 'discovered'} | "
            f"{record.role or 'unassigned'} | {capabilities} | {record.scope} | "
            f"`{record.path}` |"
        )
    lines.extend(["", f"Discovered {len(records)} skill(s)."])
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--agent",
        choices=(*AGENT_ROOTS.keys(), "all"),
        default="all",
        help="Limit skill roots to one host agent (default: all).",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="Module manifest path.",
    )
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="Output format.",
    )
    parser.add_argument("--query", default="", help="Rank skills for a UI/UX request.")
    parser.add_argument(
        "--include-all",
        action="store_true",
        help="Include skills without UI/UX signals.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Limit output after ranking; 0 means no limit.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    records = discover(
        args.agent,
        Path.cwd().resolve(),
        args.include_all,
        args.query,
        args.config.resolve(),
    )
    if args.limit > 0:
        records = records[: args.limit]
    if args.format == "json":
        print(json.dumps([asdict(record) for record in records], indent=2))
    else:
        print(markdown(records, args.query))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
