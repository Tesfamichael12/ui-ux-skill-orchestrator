#!/usr/bin/env python3
"""Inventory UI/UX agent skills across project and global skill roots."""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


UI_TERMS = {
    "ui",
    "ux",
    "frontend",
    "front-end",
    "design",
    "visual",
    "typography",
    "font",
    "color",
    "colour",
    "palette",
    "layout",
    "spacing",
    "responsive",
    "accessibility",
    "animation",
    "motion",
    "component",
    "figma",
    "stitch",
    "tailwind",
    "interface",
    "dashboard",
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

KNOWN_CAPABILITIES = {
    "frontend-design": {
        "direction",
        "typography",
        "color",
        "layout",
        "components",
        "responsive",
    },
    "impeccable": {
        "direction",
        "ux",
        "typography",
        "color",
        "layout",
        "components",
        "motion",
        "accessibility",
        "responsive",
        "performance",
        "audit",
        "design-system",
        "implementation",
    },
    "mies": {
        "direction",
        "ux",
        "typography",
        "layout",
        "components",
        "motion",
        "accessibility",
        "responsive",
        "audit",
        "design-system",
    },
    "ui-ux-pro-max": {
        "direction",
        "ux",
        "typography",
        "color",
        "layout",
        "components",
        "motion",
        "accessibility",
        "responsive",
        "performance",
        "data-viz",
        "implementation",
    },
    "ui-animation": {"motion", "accessibility", "performance", "components", "audit"},
    "taste-design": {
        "direction",
        "typography",
        "color",
        "layout",
        "motion",
        "design-system",
        "stitch",
    },
    "figma-create-design-system-rules": {"design-system", "figma", "implementation"},
    "web-design-guidelines": {
        "layout",
        "components",
        "accessibility",
        "responsive",
        "audit",
    },
    "fixing-accessibility": {"accessibility", "components", "audit"},
    "fixing-motion-performance": {"motion", "performance", "audit"},
    "tailwind-design-system": {"design-system", "implementation", "components", "responsive"},
    "design-taste-frontend": {
        "direction",
        "typography",
        "color",
        "layout",
        "components",
        "motion",
    },
}

QUERY_ALIASES = {
    "typography": {"font", "fonts", "type", "typeface", "typefaces", "typography"},
    "color": {"color", "colors", "colour", "colours", "palette", "palettes", "theme"},
    "layout": {"alignment", "grid", "layout", "space", "spacing"},
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

SPECIALTY_CAPABILITIES = {
    "frontend-design": {"direction"},
    "impeccable": {"audit", "performance", "responsive"},
    "mies": {"layout"},
    "ui-ux-pro-max": {"typography", "color", "data-viz", "ux"},
    "ui-animation": {"motion"},
    "taste-design": {"stitch"},
    "figma-create-design-system-rules": {"figma", "design-system"},
}


@dataclass(frozen=True)
class SkillRecord:
    name: str
    description: str
    capabilities: list[str]
    scope: str
    agent_root: str
    path: str
    score: int = 0


def normalize_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def parse_frontmatter(path: Path) -> tuple[str, str] | None:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        return None

    if not lines or lines[0].strip() != "---":
        return None

    end = next((index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---"), None)
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


def root_specs(agent: str, cwd: Path) -> list[tuple[Path, str, str]]:
    home = Path.home()
    workspace = find_workspace_root(cwd)
    specs: list[tuple[Path, str, str]] = []

    for base in dict.fromkeys([cwd, workspace]):
        for relative, label in [
            (".agents/skills", "project-common"),
            (".agent/skills", "project-antigravity-legacy"),
            (".codex/skills", "project-codex"),
            (".claude/skills", "project-claude"),
            (".cursor/skills", "project-cursor"),
            (".gemini/skills", "project-gemini"),
        ]:
            specs.append((base / relative, "project", label))

    if agent in {"codex", "all"}:
        specs.extend(
            [
                (home / ".codex/skills", "global", "codex"),
                (home / ".agents/skills", "global", "agents-common"),
            ]
        )
    if agent in {"antigravity", "all"}:
        specs.extend(
            [
                (home / ".gemini/config/skills", "global", "antigravity-current"),
                (home / ".gemini/antigravity/skills", "global", "antigravity-legacy"),
                (home / ".agents/skills", "global", "agents-common"),
            ]
        )
    if agent == "all":
        specs.extend(
            [
                (home / ".claude/skills", "global", "claude"),
                (home / ".cursor/skills", "global", "cursor"),
            ]
        )

    unique: list[tuple[Path, str, str]] = []
    seen: set[Path] = set()
    for path, scope, label in specs:
        expanded = path.expanduser()
        if expanded in seen:
            continue
        seen.add(expanded)
        unique.append((expanded, scope, label))
    return unique


def classify(name: str, description: str) -> list[str]:
    if name in KNOWN_CAPABILITIES:
        return sorted(KNOWN_CAPABILITIES[name])

    capabilities: set[str] = set()
    haystack = f"{name} {description}".lower()
    for capability, signals in CAPABILITY_SIGNALS.items():
        if any(signal in haystack for signal in signals):
            capabilities.add(capability)
    return sorted(capabilities)


def is_ui_skill(name: str, description: str, capabilities: Iterable[str]) -> bool:
    haystack = f"{name} {description}".lower()
    return bool(set(capabilities)) and any(term in haystack for term in UI_TERMS)


def query_capabilities(query: str) -> set[str]:
    tokens = set(re.findall(r"[a-z0-9-]+", query.lower()))
    selected: set[str] = set()
    for capability, aliases in QUERY_ALIASES.items():
        if tokens.intersection(aliases):
            selected.add(capability)
    return selected


def score_record(record: SkillRecord, query: str) -> int:
    if not query:
        return 0
    needs = query_capabilities(query)
    score = len(needs.intersection(record.capabilities)) * 8
    specialties = SPECIALTY_CAPABILITIES.get(record.name, set())
    score += len(needs.intersection(specialties)) * 12
    query_tokens = set(re.findall(r"[a-z0-9-]+", query.lower()))
    text_tokens = set(re.findall(r"[a-z0-9-]+", f"{record.name} {record.description}".lower()))
    score += len(query_tokens.intersection(text_tokens))
    if record.name in query.lower():
        score += 12
    return score


def discover(agent: str, cwd: Path, include_all: bool, query: str) -> list[SkillRecord]:
    records_by_name: dict[str, SkillRecord] = {}
    for root, scope, label in root_specs(agent, cwd):
        if not root.is_dir():
            continue
        try:
            children = sorted(root.iterdir())
        except OSError:
            continue
        for child in children:
            manifest = child / "SKILL.md"
            if not manifest.is_file():
                continue
            parsed = parse_frontmatter(manifest)
            if not parsed:
                continue
            name, description = parsed
            if name == "ui-ux-skill-orchestrator":
                continue
            capabilities = classify(name, description)
            if not include_all and not is_ui_skill(name, description, capabilities):
                continue
            record = SkillRecord(
                name=name,
                description=description,
                capabilities=capabilities,
                scope=scope,
                agent_root=label,
                path=str(child.resolve()),
            )
            if name not in records_by_name:
                records_by_name[name] = record

    records = [
        SkillRecord(**{**asdict(record), "score": score_record(record, query)})
        for record in records_by_name.values()
    ]
    if query:
        records.sort(key=lambda item: (-item.score, item.name))
    else:
        records.sort(key=lambda item: item.name)
    return records


def markdown(records: list[SkillRecord], query: str) -> str:
    title = "# UI/UX skill inventory"
    if query:
        title += f'\n\nRanked for: "{query}"'
    lines = [
        title,
        "",
        "| Skill | Score | Scope | Capabilities | Root | Path |",
        "|---|---:|---|---|---|---|",
    ]
    for record in records:
        capabilities = ", ".join(record.capabilities) or "unclassified"
        lines.append(
            f"| `{record.name}` | {record.score} | {record.scope} | {capabilities} | "
            f"{record.agent_root} | `{record.path}` |"
        )
    lines.extend(["", f"Discovered {len(records)} skill(s)."])
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--agent",
        choices=("codex", "antigravity", "all"),
        default="all",
        help="Limit global roots to one host agent (default: all).",
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
    records = discover(args.agent, Path.cwd().resolve(), args.include_all, args.query)
    if args.limit > 0:
        records = records[: args.limit]
    if args.format == "json":
        print(json.dumps([asdict(record) for record in records], indent=2))
    else:
        print(markdown(records, args.query))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
