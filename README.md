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

## License

Released under the [MIT License](LICENSE). Specialist skills are separate
third-party projects with their own licenses and are never vendored into this
repository.
