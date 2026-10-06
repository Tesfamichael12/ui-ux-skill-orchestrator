#!/usr/bin/env python3
"""Discover and rank UI/UX Agent Skills using the orchestrator's data-driven catalog.

The catalog lives in ``config/``: ``skill-modules.json`` registers specialists,
``capabilities.json`` defines the concern taxonomy and matching vocabulary, and
``agents.json`` lists the skill folders each supported agent loads.
"""

from __future__ import annotations

import argparse
import functools
import json
import math
import os
import re
import sys
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path
from typing import Iterable, Iterator, Mapping, NamedTuple, Sequence


SKILL_DIR = Path(__file__).resolve().parents[1]
CONFIG_DIR = SKILL_DIR / "config"
DEFAULT_CONFIG = CONFIG_DIR / "skill-modules.json"
CAPABILITIES_CONFIG = CONFIG_DIR / "capabilities.json"
AGENTS_CONFIG = CONFIG_DIR / "agents.json"
ORCHESTRATOR_NAMES = frozenset({"ui-ux-skill-orchestrator"})
IGNORED_DIRECTORIES = frozenset(
    {
        ".git",
        ".hg",
        ".svn",
        ".venv",
        "__pycache__",
        "__pypackages__",
        "node_modules",
        "vendor",
        "venv",
    }
)
DEFAULT_DEPTH = 3

# A specialty match outweighs a broad capability match so narrow specialists
# rank above generalists for the concern they own.
SPECIALTY_WEIGHT = 12
CAPABILITY_WEIGHT = 8
KEYWORD_WEIGHT = 6
KEYWORD_CAP = 2
NAME_MENTION_BONUS = 20
TEXT_OVERLAP_CAP = 4
MIN_RANKED_SCORE = 10
DEFAULT_RANKED_LIMIT = 12

BRITISH_SPELLINGS = {
    "behaviour": "behavior",
    "behaviours": "behaviors",
    "centre": "center",
    "colour": "color",
    "colourful": "colorful",
    "colours": "colors",
    "customise": "customize",
    "grey": "gray",
    "minimise": "minimize",
    "optimisation": "optimization",
    "optimise": "optimize",
    "optimised": "optimized",
    "prioritise": "prioritize",
    "visualisation": "visualization",
    "visualisations": "visualizations",
    "visualise": "visualize",
}
TOKEN_PATTERN = re.compile(r"[a-z0-9][a-z0-9.+#-]*")
FRONTMATTER_KEY = re.compile(r"^([A-Za-z0-9_-]+):(?:\s+(.*)|\s*)$")
NESTED_KEY = re.compile(r"^\s*(?:-\s|[A-Za-z0-9_-]+:(?:\s|$))")


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
    source_path: str | None = None
    source_ref: str = "main"
    requires: tuple[str, ...] = ()
    lead_capable: bool = False
    keywords: tuple[str, ...] = ()

    @property
    def names(self) -> set[str]:
        return {self.id, self.install_skill, *self.aliases}

    @property
    def install_source(self) -> str:
        """Skills CLI source; a pinned path sidesteps repository-wide discovery quirks."""
        if self.source_path:
            return f"https://github.com/{self.package}/tree/{self.source_ref}/{self.source_path}"
        return self.package


@dataclass(frozen=True, eq=False)
class Taxonomy:
    signals: Mapping[str, tuple[str, ...]]
    query_terms: Mapping[str, tuple[str, ...]]
    labels: Mapping[str, str]
    ui_terms: tuple[str, ...]
    non_ui_terms: tuple[str, ...]
    stopwords: frozenset[str]


@dataclass(frozen=True)
class RootSpec:
    path: str
    depth: int = DEFAULT_DEPTH
    include_hidden: bool = False


@dataclass(frozen=True)
class AgentSpec:
    id: str
    label: str
    project: tuple[RootSpec, ...]
    global_roots: tuple[RootSpec, ...]


class SkillRoot(NamedTuple):
    path: Path
    scope: str
    label: str
    depth: int = DEFAULT_DEPTH
    include_hidden: bool = False


@dataclass(frozen=True, eq=False)
class QueryProfile:
    text: str
    needs: tuple[str, ...]
    evidence: Mapping[str, tuple[str, ...]]
    tokens: frozenset[str]


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
    matched: list[str] = field(default_factory=list)


def read_json_object(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path.name} must contain a JSON object.")
    return payload


def load_modules(config_path: Path = DEFAULT_CONFIG) -> list[Module]:
    """Load portfolio modules from JSON without external dependencies."""
    payload = read_json_object(config_path)
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
                source_path=source.get("path"),
                source_ref=source.get("ref", "main"),
                requires=tuple(item.get("requires", [])),
                lead_capable=bool(item.get("lead_capable", False)),
                keywords=tuple(item.get("keywords", [])),
            )
        )
    return modules


def load_prerequisites(config_path: Path = DEFAULT_CONFIG) -> dict[str, str]:
    return dict(read_json_object(config_path).get("prerequisites", {}))


def module_index(modules: Iterable[Module]) -> dict[str, Module]:
    """Map canonical names and aliases to their module."""
    index: dict[str, Module] = {}
    for module in modules:
        for name in module.names:
            index[name] = module
    return index


@functools.lru_cache(maxsize=None)
def load_taxonomy(path: Path = CAPABILITIES_CONFIG) -> Taxonomy:
    """Load the capability taxonomy and matching vocabulary."""
    payload = read_json_object(path)
    signals: dict[str, tuple[str, ...]] = {}
    query_terms: dict[str, tuple[str, ...]] = {}
    labels: dict[str, str] = {}
    for capability, spec in payload["capabilities"].items():
        own = tuple(spec.get("signals", []))
        signals[capability] = own
        query_terms[capability] = own + tuple(spec.get("query_terms", []))
        labels[capability] = spec.get("label", capability)
    return Taxonomy(
        signals=signals,
        query_terms=query_terms,
        labels=labels,
        ui_terms=tuple(payload.get("ui_terms", [])),
        non_ui_terms=tuple(payload.get("non_ui_terms", [])),
        stopwords=frozenset(payload.get("stopwords", [])),
    )


def capability_ids(path: Path = CAPABILITIES_CONFIG) -> set[str]:
    return set(load_taxonomy(path).signals)


def root_spec(value: object) -> RootSpec:
    if isinstance(value, str):
        return RootSpec(value)
    if isinstance(value, dict) and isinstance(value.get("path"), str):
        return RootSpec(
            path=value["path"],
            depth=int(value.get("depth", DEFAULT_DEPTH)),
            include_hidden=bool(value.get("include_hidden", False)),
        )
    raise ValueError(f"Invalid skill root: {value!r}")


@functools.lru_cache(maxsize=None)
def load_agents(path: Path = AGENTS_CONFIG) -> dict[str, AgentSpec]:
    """Load the skill folders each supported agent reads."""
    payload = read_json_object(path)
    agents: dict[str, AgentSpec] = {}
    for agent_id, spec in payload["agents"].items():
        agents[agent_id] = AgentSpec(
            id=agent_id,
            label=spec.get("label", agent_id),
            project=tuple(root_spec(item) for item in spec.get("project", [])),
            global_roots=tuple(root_spec(item) for item in spec.get("global", [])),
        )
    return agents


def agent_ids() -> list[str]:
    return list(load_agents())


def unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1].replace('\\"', '"')
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1].replace("''", "'")
    return re.sub(r"\s+#.*$", "", value)


def top_level_scalars(lines: Sequence[str]) -> dict[str, str]:
    """Read top-level scalar keys from a small, dependency-free YAML subset."""
    values: dict[str, str] = {}
    index = 0
    while index < len(lines):
        match = FRONTMATTER_KEY.match(lines[index])
        index += 1
        if not match:
            continue
        key, value = match.group(1), (match.group(2) or "").strip()
        continuation: list[str] = []
        while index < len(lines) and (not lines[index].strip() or lines[index][0].isspace()):
            continuation.append(lines[index])
            index += 1
        parts = [line.strip() for line in continuation if line.strip()]
        if value[:1] in {"|", ">"}:
            value = " ".join(parts)
        elif value:
            value = unquote(" ".join([value, *parts]))
        elif parts:
            first = next(line for line in continuation if line.strip())
            value = "" if NESTED_KEY.match(first) else unquote(" ".join(parts))
        values[key] = value
    return values


def parse_frontmatter(path: Path) -> tuple[str, str] | None:
    """Return a skill's name and description, or None when they are missing."""
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
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

    values = top_level_scalars(lines[1:end])
    name = values.get("name", "").strip()
    description = values.get("description", "").strip()
    if not name or not description:
        return None
    return name, description


def find_workspace_root(cwd: Path) -> Path:
    for candidate in (cwd, *cwd.parents):
        if (candidate / ".git").exists():
            return candidate
    return cwd


def selected_agents(agent: str) -> list[str]:
    agents = load_agents()
    if agent == "all":
        return list(agents)
    if agent not in agents:
        raise ValueError(f"Unknown agent: {agent}")
    return [agent]


def root_specs(agent: str, cwd: Path) -> list[SkillRoot]:
    """Return every project root before any global root so local overrides win."""
    agents = load_agents()
    names = selected_agents(agent)
    home = Path.home()
    workspace = find_workspace_root(cwd)
    specs: list[SkillRoot] = []
    for agent_name in names:
        for base in dict.fromkeys([cwd, workspace]):
            for root in agents[agent_name].project:
                specs.append(
                    SkillRoot(
                        base / root.path,
                        "project",
                        f"{agent_name}:project",
                        root.depth,
                        root.include_hidden,
                    )
                )
    for agent_name in names:
        for root in agents[agent_name].global_roots:
            specs.append(
                SkillRoot(
                    home / root.path,
                    "global",
                    f"{agent_name}:global",
                    root.depth,
                    root.include_hidden,
                )
            )

    unique: list[SkillRoot] = []
    seen: set[Path] = set()
    for spec in specs:
        expanded = spec.path.expanduser()
        if expanded in seen:
            continue
        seen.add(expanded)
        unique.append(spec._replace(path=expanded))
    return unique


def iter_skill_manifests(
    root: Path,
    max_depth: int = DEFAULT_DEPTH,
    include_hidden: bool = False,
) -> Iterator[Path]:
    """Yield SKILL.md files, following symlinked skill folders once each.

    A folder that holds SKILL.md is a skill; nested folders inside it are not
    searched, matching how the Skills CLI shadows nested manifests.
    """
    if not root.is_dir():
        return
    visited: set[str] = set()
    pending: list[tuple[Path, int]] = [(root, 0)]
    while pending:
        current, depth = pending.pop()
        real = os.path.realpath(current)
        if real in visited:
            continue
        visited.add(real)
        manifest = current / "SKILL.md"
        if manifest.is_file():
            yield manifest
            continue
        if depth >= max_depth:
            continue
        try:
            entries = sorted(os.scandir(current), key=lambda entry: entry.name)
        except OSError:
            continue
        for entry in reversed(entries):
            if entry.name in IGNORED_DIRECTORIES:
                continue
            if entry.name.startswith(".") and not include_hidden:
                continue
            try:
                if entry.is_dir():
                    pending.append((Path(entry.path), depth + 1))
            except OSError:
                continue


def normalize_text(text: str) -> str:
    """Lower-case text and fold common British spellings onto the vocabulary."""
    lowered = text.lower().replace("\u2019", "'")
    return re.sub(
        r"[a-z]+",
        lambda match: BRITISH_SPELLINGS.get(match.group(0), match.group(0)),
        lowered,
    )


@functools.lru_cache(maxsize=4096)
def term_pattern(term: str) -> re.Pattern[str]:
    """Match a term or phrase on word boundaries, tolerating separators and plurals."""
    words = re.sub(r"[-_]+", " ", term.lower()).split()
    body = r"[\s_/-]+".join(re.escape(word) for word in words)
    return re.compile(rf"(?<![a-z0-9]){body}(?:e?s)?(?![a-z0-9])")


def matched_terms(text: str, terms: Iterable[str]) -> list[str]:
    return [term for term in terms if term_pattern(term).search(text)]


def capability_matches(
    text: str,
    vocabulary: Mapping[str, Sequence[str]],
) -> dict[str, list[str]]:
    matches: dict[str, list[str]] = {}
    for capability, terms in vocabulary.items():
        hits = matched_terms(text, terms)
        if hits:
            matches[capability] = hits
    return matches


def classify(
    name: str,
    description: str,
    registry: Mapping[str, Module],
    taxonomy: Taxonomy | None = None,
) -> list[str]:
    module = registry.get(name)
    if module:
        return sorted(module.capabilities)
    taxonomy = taxonomy or load_taxonomy()
    text = normalize_text(f"{name} {description}")
    return sorted(capability_matches(text, taxonomy.signals))


def ui_evidence(
    name: str,
    description: str,
    taxonomy: Taxonomy | None = None,
) -> tuple[int, int]:
    """Count distinct UI terms and non-UI context terms in a skill's metadata."""
    taxonomy = taxonomy or load_taxonomy()
    text = normalize_text(f"{name} {description}")
    return (
        len(matched_terms(text, taxonomy.ui_terms)),
        len(matched_terms(text, taxonomy.non_ui_terms)),
    )


def is_ui_skill(
    name: str,
    description: str,
    capabilities: Iterable[str],
    taxonomy: Taxonomy | None = None,
) -> bool:
    """An unregistered skill qualifies only when UI evidence outweighs other context."""
    if not set(capabilities):
        return False
    ui_hits, non_ui_hits = ui_evidence(name, description, taxonomy)
    return ui_hits > 0 and ui_hits > non_ui_hits


def tokens_of(text: str, stopwords: frozenset[str]) -> frozenset[str]:
    return frozenset(
        token
        for token in TOKEN_PATTERN.findall(text)
        if len(token) > 2 and token not in stopwords
    )


def profile_query(query: str, taxonomy: Taxonomy | None = None) -> QueryProfile:
    """Map a request onto the concern taxonomy."""
    taxonomy = taxonomy or load_taxonomy()
    text = normalize_text(query)
    evidence = capability_matches(text, taxonomy.query_terms)
    return QueryProfile(
        text=text,
        needs=tuple(sorted(evidence)),
        evidence={capability: tuple(hits) for capability, hits in evidence.items()},
        tokens=tokens_of(text, taxonomy.stopwords),
    )


def query_capabilities(query: str) -> set[str]:
    return set(profile_query(query).needs)


def is_mentioned(text: str, name: str, registered: bool) -> bool:
    """True when a request names the skill rather than just using a common word."""
    if re.search(rf"[$/@]{re.escape(name)}(?![a-z0-9-])", text):
        return True
    if registered or "-" in name or any(character.isdigit() for character in name):
        return term_pattern(name).search(text) is not None
    return False


def rank_record(
    record: SkillRecord,
    profile: QueryProfile,
    registry: Mapping[str, Module],
    taxonomy: Taxonomy | None = None,
) -> tuple[int, list[str]]:
    """Score one skill for a request and return the concerns it matched."""
    taxonomy = taxonomy or load_taxonomy()
    module = registry.get(record.name)
    names = module.names if module else {record.name}
    mentioned = any(is_mentioned(profile.text, name, module is not None) for name in names)
    needs = set(profile.needs)
    capabilities = set(record.capabilities)
    matched = needs & capabilities
    owned = needs & set(module.specialties) if module else set()

    if module and module.tier == "integration" and not owned and not mentioned:
        return 0, []
    if not matched and not mentioned:
        return 0, []

    breadth = min(1.0, math.sqrt(4 / max(len(capabilities), 1)))
    score = SPECIALTY_WEIGHT * len(owned) + round(CAPABILITY_WEIGHT * len(matched) * breadth)
    if module:
        keywords = matched_terms(profile.text, module.keywords)
        score += KEYWORD_WEIGHT * min(KEYWORD_CAP, len(keywords))
    description_tokens = tokens_of(
        normalize_text(f"{record.name} {record.description}"),
        taxonomy.stopwords,
    )
    score += min(TEXT_OVERLAP_CAP, len(profile.tokens & description_tokens))
    if mentioned:
        score += NAME_MENTION_BONUS
    return score, sorted(matched)


def score_record(record: SkillRecord, query: str, registry: Mapping[str, Module]) -> int:
    if not query:
        return 0
    return rank_record(record, profile_query(query), registry)[0]


def discover(
    agent: str,
    cwd: Path,
    include_all: bool,
    query: str,
    config_path: Path = DEFAULT_CONFIG,
) -> list[SkillRecord]:
    """Find installed skills; registered modules are deduplicated across aliases."""
    modules = load_modules(config_path)
    registry = module_index(modules)
    taxonomy = load_taxonomy()
    records: dict[str, SkillRecord] = {}

    for spec in root_specs(agent, cwd):
        root = SkillRoot(*spec)
        for manifest in iter_skill_manifests(root.path, root.depth, root.include_hidden):
            parsed = parse_frontmatter(manifest)
            if not parsed:
                continue
            name, description = parsed
            if name in ORCHESTRATOR_NAMES:
                continue
            module = registry.get(name)
            key = module.id if module else name
            if key in records:
                continue
            capabilities = classify(name, description, registry, taxonomy)
            if (
                module is None
                and not include_all
                and not is_ui_skill(name, description, capabilities, taxonomy)
            ):
                continue
            records[key] = SkillRecord(
                name=name,
                description=description,
                capabilities=capabilities,
                scope=root.scope,
                agent_root=root.label,
                path=str(manifest.parent.resolve()),
                registered=module is not None,
                module_id=module.id if module else None,
                tier=module.tier if module else None,
                role=module.role if module else None,
                source_package=module.package if module else None,
            )

    ranked: list[SkillRecord] = list(records.values())
    if query:
        profile = profile_query(query, taxonomy)
        scored: list[SkillRecord] = []
        for record in ranked:
            score, matched = rank_record(record, profile, registry, taxonomy)
            scored.append(replace(record, score=score, matched=matched))
        ranked = sorted(scored, key=lambda item: (-item.score, not item.registered, item.name))
    else:
        ranked.sort(key=lambda item: (not item.registered, item.name))
    return ranked


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


def markdown(records: Sequence[SkillRecord], query: str) -> str:
    lines = ["# UI/UX skill inventory", ""]
    if query:
        needs = profile_query(query).needs
        lines.append(f'Ranked for: "{query}"')
        lines.append("Detected concerns: " + (", ".join(needs) or "none"))
        lines.extend(
            [
                "",
                "| Skill | Score | Module | Tier | Role | Matched | Scope | Path |",
                "|---|---:|---|---|---|---|---|---|",
            ]
        )
    else:
        lines.extend(
            [
                "| Skill | Module | Tier | Role | Capabilities | Scope | Path |",
                "|---|---|---|---|---|---|---|",
            ]
        )
    for record in records:
        module = record.module_id or "dynamic"
        tier = record.tier or "discovered"
        role = record.role or "unassigned"
        if query:
            matched = ", ".join(record.matched) or "named"
            lines.append(
                f"| `{record.name}` | {record.score} | {module} | {tier} | {role} | "
                f"{matched} | {record.scope} | `{record.path}` |"
            )
        else:
            capabilities = ", ".join(record.capabilities) or "unclassified"
            lines.append(
                f"| `{record.name}` | {module} | {tier} | {role} | {capabilities} | "
                f"{record.scope} | `{record.path}` |"
            )
    lines.extend(["", f"Listed {len(records)} skill(s)."])
    return "\n".join(lines)


def agents_markdown() -> str:
    lines = [
        "| Agent | Label | Project folders | Global folders (under ~) |",
        "|---|---|---|---|",
    ]
    for agent in load_agents().values():
        project = ", ".join(f"`{root.path}`" for root in agent.project)
        global_roots = ", ".join(f"`{root.path}`" for root in agent.global_roots)
        lines.append(f"| `{agent.id}` | {agent.label} | {project} | {global_roots} |")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--agent",
        choices=(*agent_ids(), "all"),
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
        help="Include unregistered skills without UI/UX signals.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help=(
            f"Maximum rows after ranking (default: {DEFAULT_RANKED_LIMIT} with --query, "
            "otherwise all; 0 means no limit)."
        ),
    )
    parser.add_argument(
        "--min-score",
        type=int,
        default=MIN_RANKED_SCORE,
        help=f"Hide ranked skills below this score (default: {MIN_RANKED_SCORE}).",
    )
    parser.add_argument(
        "--list-agents",
        action="store_true",
        help="Print supported agent identifiers and their skill folders.",
    )
    return parser


def safe_console() -> None:
    """Replace characters a console encoding cannot show instead of crashing on them."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(errors="replace")


def main() -> int:
    safe_console()
    args = build_parser().parse_args()
    if args.list_agents:
        print(agents_markdown())
        return 0
    try:
        records = discover(
            args.agent,
            Path.cwd().resolve(),
            args.include_all,
            args.query,
            args.config.resolve(),
        )
    except (OSError, KeyError, ValueError, json.JSONDecodeError) as error:
        print(f"Configuration error: {error}", file=sys.stderr)
        return 2
    limit = args.limit
    if args.query:
        records = [record for record in records if record.score >= args.min_score]
        if limit is None:
            limit = DEFAULT_RANKED_LIMIT
    if limit:
        records = records[:limit]
    if args.format == "json":
        print(json.dumps([asdict(record) for record in records], indent=2))
    else:
        print(markdown(records, args.query))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
