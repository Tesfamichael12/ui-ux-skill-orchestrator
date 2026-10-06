# UI/UX Skill Orchestrator

A portable Agent Skill that routes frontend design work to the smallest
high-value combination of UI/UX specialists, reconciles their guidance, and
produces one implementation-ready result.

The orchestrator does not replace design skills. It gives them clear ownership:
one lead establishes direction, narrow specialists settle typography, color,
spacing, motion, accessibility, or tooling concerns, and one integrated review
checks the finished work.

## Install

Install globally with the open-source Skills CLI:

```bash
npx skills add Tesfamichael12/ui-ux-skill-orchestrator \
  --skill ui-ux-skill-orchestrator \
  -g
```

Install for a specific agent without interactive destination prompts:

```bash
npx skills add Tesfamichael12/ui-ux-skill-orchestrator \
  --skill ui-ux-skill-orchestrator \
  -g -a codex -y
```

Replace `codex` with another supported agent identifier such as
`claude-code`, `cursor`, `antigravity`, `gemini-cli`, `github-copilot`, or
`opencode`. List every identifier the scripts understand with:

```bash
python3 skills/ui-ux-skill-orchestrator/scripts/inventory_ui_skills.py --list-agents
```

Restart the agent after installation if it does not refresh its skill inventory
automatically.

### Claude Code plugin

The repository is also a Claude Code plugin marketplace:

```text
/plugin marketplace add Tesfamichael12/ui-ux-skill-orchestrator
/plugin install ui-ux-skill-orchestrator@ui-ux-skill-orchestrator
```

Plugin skills are namespaced, so the skill appears as
`ui-ux-skill-orchestrator:ui-ux-skill-orchestrator`.

### Uninstall

```bash
npx skills remove ui-ux-skill-orchestrator -g
```

For the Claude Code plugin, run
`/plugin uninstall ui-ux-skill-orchestrator@ui-ux-skill-orchestrator`.
Specialist skills are separate installs; remove them the same way by name.

## Set up the specialist portfolio

On its first UI/UX task, the orchestrator checks whether its core specialists
are available. If any are missing, it identifies their original repositories
and asks before installing them.

Run the same check manually from a clone:

```bash
python3 skills/ui-ux-skill-orchestrator/scripts/setup.py \
  --agent codex \
  --check
```

Offer one interactive installation prompt:

```bash
python3 skills/ui-ux-skill-orchestrator/scripts/setup.py \
  --agent codex
```

Preview every command without changing the system:

```bash
python3 skills/ui-ux-skill-orchestrator/scripts/setup.py \
  --agent codex \
  --dry-run
```

The script never installs third-party skills without terminal confirmation.
`--yes` exists for automation, but should be used only after the user has
explicitly approved the listed sources.

`setup.py` exit codes:

| Code | Meaning |
|---|---|
| 0 | Every selected module is installed, or a dry run printed its commands |
| 2 | Configuration error, such as an unknown module name |
| 3 | Check only (`--check` or `--json`): modules are missing |
| 4 | The user declined installation |
| 5 | `npx` is not available |
| 6 | An installation command failed |
| 7 | Installation finished, but a module is still not discoverable |

### Core modules

| Module | Primary responsibility | Source |
|---|---|---|
| `frontend-design` | Distinctive visual direction | [anthropics/skills](https://github.com/anthropics/skills) |
| `impeccable` | Production integration and audit | [pbakaus/impeccable](https://github.com/pbakaus/impeccable) |
| `ui-ux-pro-max` | Font, palette, UX, chart, and stack evidence | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) |
| `mies` | Restraint, spacing, hierarchy, and reduction | [deeflect/mies](https://github.com/deeflect/mies) |
| `ui-animation` | Motion mechanics and reduced-motion behavior | [mblode/agent-skills](https://github.com/mblode/agent-skills) |
| `fixing-accessibility` | WCAG semantics, keyboard, focus, and contrast fixes | [ibelick/ui-skills](https://github.com/ibelick/ui-skills) |

### Optional integrations

| Module | Used when | Requires | Source |
|---|---|---|---|
| `stitch-design-taste` | Google Stitch or `DESIGN.md` is the target | — | [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) |
| `figma-create-design-system-rules` | Figma-to-code rules are requested | Figma MCP | [openai/skills](https://github.com/openai/skills) |
| `figma-implement-design` | A Figma frame must become code | Figma MCP | [openai/skills](https://github.com/openai/skills) |
| `typography-audit` | Existing typography needs an audit | — | [mblode/agent-skills](https://github.com/mblode/agent-skills) |
| `ui-verification` | Behavior must be measured in a browser | Browser automation | [mblode/agent-skills](https://github.com/mblode/agent-skills) |

These dependencies are referenced, not redistributed. Each remains governed by
its own license and release process. Skills that fetch and follow remote
instructions at runtime are deliberately not registered.

## Use

Invoke it explicitly:

```text
Use $ui-ux-skill-orchestrator to build an accessible analytics dashboard with
strong typography and restrained motion.
```

Compatible agents may also activate it implicitly for frontend UI/UX requests.

The orchestrator:

1. inspects the user brief and incumbent design system;
2. discovers installed UI/UX skills;
3. appoints one lead and the minimum useful specialists;
4. assigns exclusive concern ownership;
5. resolves conflicts through a fixed authority ladder;
6. combines decisions into one blueprint;
7. implements and validates the result when the request includes implementation.

### Inspect a routing decision

The router prints the draft brief the skill starts from:

```bash
python3 skills/ui-ux-skill-orchestrator/scripts/route.py \
  --agent codex \
  --query "Redesign our analytics dashboard to feel calm and minimal"
```

```text
Rule: `dashboard` — Dense, data-heavy product surface.
| Lead       | `mies`          | direction, layout |
| Specialist | `ui-ux-pro-max` | data-viz          |
| Validation | `impeccable`    | audit, performance, responsive |
```

Add `--assume-installed` to plan as if every registered module were present,
`--task` or `--scope` to override inference, and `--format json` for tooling.
Rank the raw inventory for a request with
`inventory_ui_skills.py --query "<request>"`. More examples are in
[examples/routing-scenarios.md](examples/routing-scenarios.md).

## Why this exists

Installing several strong design skills creates a new problem: they overlap.
Running all of them wastes context and can produce competing palettes, type
systems, spacing scales, or visual directions. This skill treats the portfolio
like a design team rather than a panel of independent critics.

## Repository layout

```text
.
├── .claude-plugin/          # Claude Code plugin and marketplace manifests
├── skills/
│   └── ui-ux-skill-orchestrator/
│       ├── SKILL.md
│       ├── agents/openai.yaml
│       ├── config/          # modules, capabilities, agents, routing rules
│       ├── references/
│       └── scripts/
├── tests/
├── docs/
├── examples/
└── .github/
```

Only the directory under `skills/` is installed by skill package managers.
Repository documentation, tests, and contribution files remain outside the
runtime skill.

## Compatibility

The package follows the open Agent Skills format: a `SKILL.md` with YAML
frontmatter plus optional scripts and references. Its scripts need Python 3.9
or newer and no third-party packages.

Discovery knows the skill folders of 28 agents, including Codex, Claude Code
(with installed plugins), Cursor, GitHub Copilot, Gemini CLI, Antigravity,
OpenCode, Windsurf, Cline, Roo Code, Kiro CLI, and Amp. The folders live in
[`config/agents.json`](skills/ui-ux-skill-orchestrator/config/agents.json).

## Modular by design

Everything that changes with the ecosystem is data:

- [`skill-modules.json`](skills/ui-ux-skill-orchestrator/config/skill-modules.json)
  registers specialists: tier, role, capabilities, specialties, keywords, tool
  prerequisites, and pinned install sources;
- [`capabilities.json`](skills/ui-ux-skill-orchestrator/config/capabilities.json)
  defines the concern vocabulary used to classify skills and requests;
- [`routing-rules.json`](skills/ui-ux-skill-orchestrator/config/routing-rules.json)
  maps situations to a lead, specialists, a validation owner, and a recipe;
- [`agents.json`](skills/ui-ux-skill-orchestrator/config/agents.json) lists
  where each agent loads skills.

New specialists and rules therefore need no code changes, and `validate.py`
cross-checks every reference. The orchestrator also discovers unregistered
UI/UX skills and can use them as dynamic candidates after evaluating their
scope and dependencies.

See [Architecture](docs/architecture.md),
[Adding a module](docs/adding-a-module.md), and
[Adding a routing rule](docs/adding-a-routing-rule.md).

## Troubleshooting

- **The agent does not see the skill.** Restart the agent, then confirm the
  folder with `npx skills list -g`.
- **A specialist shows as missing although it is installed.** Run
  `inventory_ui_skills.py --agent <host>`; if it lives in an unusual folder,
  add the folder to `config/agents.json`.
- **A third-party repository lists no skills.** Some repositories need
  `--full-depth`; registered modules avoid this by installing from a pinned
  tree URL.
- **Figma or browser modules do nothing.** They need a connected Figma MCP
  server or browser automation; `setup.py --check` lists these prerequisites.

## Development

The runtime has no third-party Python dependency.

```bash
python3 skills/ui-ux-skill-orchestrator/scripts/validate.py
python3 -m unittest discover -s tests -v
npx skills add . --list
claude plugin validate .
```

Read [CONTRIBUTING.md](CONTRIBUTING.md) before proposing changes. Security
concerns should follow [SECURITY.md](SECURITY.md).

## License

Released under the [MIT License](LICENSE). Specialist skills are separate
third-party projects with their own licenses and are never vendored into this
repository.
