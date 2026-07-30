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
`claude-code`, `cursor`, `antigravity`, `gemini-cli`, or `opencode`.

Restart the agent after installation if it does not refresh its skill inventory
automatically.

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

### Core modules

| Module | Primary responsibility | Source |
|---|---|---|
| `frontend-design` | Distinctive visual direction | [anthropics/skills](https://github.com/anthropics/skills) |
| `impeccable` | Production integration and audit | [pbakaus/impeccable](https://github.com/pbakaus/impeccable) |
| `ui-ux-pro-max` | Font, palette, UX, chart, and stack evidence | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) |
| `mies` | Restraint, spacing, hierarchy, and reduction | [deeflect/mies](https://github.com/deeflect/mies) |
| `ui-animation` | Motion mechanics and reduced-motion behavior | [mblode/agent-skills](https://github.com/mblode/agent-skills) |

### Optional integrations

| Module | Used when | Source |
|---|---|---|
| `stitch-design-taste` | Google Stitch or `DESIGN.md` is the target | [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) |
| `figma-create-design-system-rules` | Figma MCP rules are requested | [openai/skills](https://github.com/openai/skills) |

These dependencies are referenced, not redistributed. Each remains governed by
its own license and release process.

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

## Why this exists

Installing several strong design skills creates a new problem: they overlap.
Running all of them wastes context and can produce competing palettes, type
systems, spacing scales, or visual directions. This skill treats the portfolio
like a design team rather than a panel of independent critics.

## Repository layout

```text
.
├── skills/
│   └── ui-ux-skill-orchestrator/
│       ├── SKILL.md
│       ├── agents/openai.yaml
│       ├── references/
│       └── scripts/
├── tests/
├── docs/
└── .github/
```

Only the directory under `skills/` is installed by skill package managers.
Repository documentation, tests, and contribution files remain outside the
runtime skill.

## Compatibility

The package follows the open Agent Skills format: a `SKILL.md` with YAML
frontmatter plus optional scripts and references. It is designed for
skills-compatible agents including Codex, Claude Code, Cursor, Antigravity,
Gemini CLI, OpenCode, GitHub Copilot, and others supported by the Skills CLI.

## Modular by design

The specialist registry lives in
[`config/skill-modules.json`](skills/ui-ux-skill-orchestrator/config/skill-modules.json).
Each entry declares aliases, capabilities, specialties, role, tier, and source.
The discovery and setup scripts consume this file directly.

New specialists can therefore be added without changing routing code. The
orchestrator also discovers unregistered UI/UX skills and can use them as
dynamic candidates after evaluating their scope and dependencies.

See [Architecture](docs/architecture.md) and
[Adding a module](docs/adding-a-module.md).

## Development

The runtime has no third-party Python dependency.

```bash
python3 skills/ui-ux-skill-orchestrator/scripts/validate.py
python3 -m unittest discover -s tests -v
npx skills add . --list
```

Read [CONTRIBUTING.md](CONTRIBUTING.md) before proposing changes. Security
concerns should follow [SECURITY.md](SECURITY.md).

## License

Released under the [MIT License](LICENSE). Specialist skills are separate
third-party projects with their own licenses and are never vendored into this
repository.
