# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and releases use
[Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.2.0] - 2026-10-06

### Added

- `scripts/route.py`: a deterministic router that drafts a brief with one
  lead, owned concerns, a validation owner, exclusions, missing modules with
  install commands, tool prerequisites, and the matching recipe.
- Data-driven catalog: `config/capabilities.json` (concern vocabulary),
  `config/agents.json` (skill folders for 28 agents), and
  `config/routing-rules.json` (prioritized routing rules and scope budgets).
- Modules: `fixing-accessibility` (core), plus `figma-implement-design`,
  `typography-audit`, and `ui-verification` integrations.
- Module fields: `lead_capable`, `keywords`, `requires` with declared
  `prerequisites`, and pinned `source.path`/`source.ref` install sources.
- Recipes for Figma design to code, accessibility audits, browser
  verification, restrained direction, and existing-interface refinement.
- Claude Code plugin and marketplace manifests.
- `inventory_ui_skills.py --list-agents`, `--limit`, and `--min-score`.
- Validation of every config file, cross-references, and Python 3.9 syntax.
- Tests for discovery, matching, routing scenarios, and documentation
  coverage; CI on Python 3.9, 3.10, 3.13, and Windows, plus a lint job.

### Changed

- Ranking favors the specialist that owns a concern over broad generalists,
  ignores stopwords, matches whole words, and requires a trigger before an
  integration module ranks.
- `ui-animation` and `stitch-design-taste` install from pinned tree URLs.
- `setup.py --json` implies `--check` and exits 3 when modules are missing.
- `SKILL.md` documents every supported agent and the routing step.

### Fixed

- Symlinked skill folders, such as Skills CLI installs, are discovered.
- Aliases of one module are listed once.
- Claude Code no longer reads `.agents/skills`; its plugin cache is scanned.
- Project folders now always take precedence over global folders.
- Engineering skills that mention UI words (Spring Boot, PostgreSQL tokens,
  ECS components) are no longer listed as UI skills.
- "ux" inside words such as "luxury" no longer counts as a skill mention.
- Validation paths are portable on Windows.

## [0.1.0] - 2026-07-30

### Added

- Cross-agent UI/UX orchestration skill.
- Manifest-driven specialist registry and dynamic skill discovery.
- Consent-based dependency checks and installation.
- Routing recipes, concern ownership, conflict arbitration, and synthesis
  contract.
- Validation tooling and representative routing tests.

[Unreleased]: https://github.com/Tesfamichael12/ui-ux-skill-orchestrator/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/Tesfamichael12/ui-ux-skill-orchestrator/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/Tesfamichael12/ui-ux-skill-orchestrator/releases/tag/v0.1.0
