#!/usr/bin/env python3
"""Check and optionally install the orchestrator's specialist skill portfolio."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Sequence

from inventory_ui_skills import (
    DEFAULT_CONFIG,
    Module,
    agent_ids,
    installed_module_ids,
    load_modules,
    load_prerequisites,
)


def select_modules(
    modules: Sequence[Module],
    include_integrations: bool,
    only: Sequence[str],
) -> list[Module]:
    """Select core modules, requested integrations, or explicit module IDs."""
    if only:
        by_name = {
            name: module
            for module in modules
            for name in module.names
        }
        unknown = sorted(set(only) - set(by_name))
        if unknown:
            raise ValueError(f"Unknown module(s): {', '.join(unknown)}")
        selected: list[Module] = []
        seen: set[str] = set()
        for name in only:
            module = by_name[name]
            if module.id not in seen:
                selected.append(module)
                seen.add(module.id)
        return selected

    tiers = {"core"}
    if include_integrations:
        tiers.add("integration")
    return [module for module in modules if module.tier in tiers]


def install_command(module: Module, agent: str, project: bool) -> list[str]:
    target_agent = "*" if agent == "all" else agent
    command = [
        "npx",
        "--yes",
        "skills",
        "add",
        module.install_source,
        "--skill",
        module.install_skill,
        "-a",
        target_agent,
        "-y",
    ]
    if not project:
        command.append("-g")
    return command


def command_text(command: Sequence[str]) -> str:
    return " ".join(f"'{part}'" if " " in part else part for part in command)


def print_status(
    selected: Sequence[Module],
    installed: set[str],
    missing: Sequence[Module],
    agent: str,
    project: bool,
    prerequisites: dict[str, str],
) -> None:
    scope = "project" if project else "global"
    print(f"UI/UX specialist check for {agent} ({scope} install target)")
    print()
    for module in selected:
        marker = "installed" if module.id in installed else "missing"
        print(f"  [{marker:9}] {module.id:<34} {module.role}")
    if missing:
        print()
        print("Missing modules will be installed from their original repositories:")
        for module in missing:
            print(f"  - {module.id}: {module.source_url}")
    needed = sorted({item for module in selected for item in module.requires})
    if needed:
        print()
        print("Some modules only work when these tools are available:")
        for item in needed:
            print(f"  - {item}: {prerequisites.get(item, '')}")


def payload(
    selected: Sequence[Module],
    installed: set[str],
    missing: Sequence[Module],
    agent: str,
    project: bool,
) -> dict[str, object]:
    return {
        "agent": agent,
        "scope": "project" if project else "global",
        "ready": not missing,
        "selected": [module.id for module in selected],
        "installed": sorted(installed.intersection(module.id for module in selected)),
        "missing": [module.id for module in missing],
        "sources": {
            module.id: module.source_url
            for module in missing
        },
        "requires": {
            module.id: list(module.requires)
            for module in selected
            if module.requires
        },
    }


def confirm_install(count: int, agent: str, project: bool) -> bool:
    if not sys.stdin.isatty():
        print(
            "Installation needs interactive consent. Re-run with --yes only after "
            "the user has explicitly approved these sources.",
            file=sys.stderr,
        )
        return False
    scope = "into this project" if project else "globally"
    answer = input(
        f"\nInstall all {count} missing specialist skill(s) {scope} "
        f"for {agent}? [y/N]: "
    )
    return answer.strip().lower() in {"y", "yes"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--agent",
        required=True,
        choices=(*agent_ids(), "all"),
        help="Agent destination used by the Skills CLI.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="Module manifest path.",
    )
    parser.add_argument(
        "--include-integrations",
        action="store_true",
        help="Include every optional integration registered in the manifest.",
    )
    parser.add_argument(
        "--only",
        nargs="+",
        default=[],
        metavar="MODULE",
        help="Check or install only named module IDs or aliases.",
    )
    parser.add_argument(
        "--project",
        action="store_true",
        help="Install into the current project instead of globally.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Report status without offering installation.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Install without prompting; use only after explicit user approval.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print installation commands without executing them.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable status; implies --check.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        modules = load_modules(args.config.resolve())
        prerequisites = load_prerequisites(args.config.resolve())
        selected = select_modules(modules, args.include_integrations, args.only)
    except (OSError, KeyError, json.JSONDecodeError, ValueError) as error:
        print(f"Configuration error: {error}", file=sys.stderr)
        return 2

    installed = installed_module_ids(
        args.agent,
        Path.cwd().resolve(),
        args.config.resolve(),
    )
    missing = [module for module in selected if module.id not in installed]

    if args.json:
        print(
            json.dumps(
                payload(
                    selected,
                    installed,
                    missing,
                    args.agent,
                    args.project,
                ),
                indent=2,
            )
        )
        return 3 if missing else 0

    print_status(selected, installed, missing, args.agent, args.project, prerequisites)
    if not missing:
        print("\nPortfolio is ready.")
        return 0
    if args.check:
        return 3

    commands = [
        install_command(module, args.agent, args.project)
        for module in missing
    ]
    if args.dry_run:
        print("\nCommands:")
        for command in commands:
            print(f"  {command_text(command)}")
        return 0

    if not args.yes and not confirm_install(len(missing), args.agent, args.project):
        print("Installation cancelled. The orchestrator will use available fallbacks.")
        return 4
    if shutil.which("npx") is None:
        print(
            "npx is required. Install a current Node.js distribution, then retry.",
            file=sys.stderr,
        )
        return 5

    failures: list[str] = []
    for module, command in zip(missing, commands):
        print(f"\nInstalling {module.id} from {module.source_url}")
        result = subprocess.run(command, check=False)
        if result.returncode != 0:
            failures.append(module.id)

    if failures:
        print(
            f"\nInstallation failed for: {', '.join(failures)}",
            file=sys.stderr,
        )
        return 6

    verified = installed_module_ids(
        args.agent,
        Path.cwd().resolve(),
        args.config.resolve(),
    )
    unverified = [module.id for module in missing if module.id not in verified]
    if unverified:
        print(
            "\nThe installer completed, but discovery could not verify: "
            + ", ".join(unverified),
            file=sys.stderr,
        )
        print("Restart the agent and run this script with --check.")
        return 7

    print("\nAll selected specialist skills are installed and discoverable.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
