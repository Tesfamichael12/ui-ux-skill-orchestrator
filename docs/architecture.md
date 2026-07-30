# Architecture

## Goals

The orchestrator must be portable, deterministic where possible, conservative
about context, and open to stronger future specialists.

It separates four concerns:

1. **Discovery** finds installed and dynamically available skills.
2. **Routing** assigns one lead and narrow concern owners.
3. **Synthesis** resolves conflicts into one design and implementation plan.
4. **Validation** reviews the integrated result.

```mermaid
flowchart LR
    A[User request] --> B[Inspect product truth]
    B --> C[Discover installed skills]
    C --> D[Choose one lead]
    D --> E[Assign narrow specialists]
    E --> F[Resolve conflicts]
    F --> G[Consolidated blueprint]
    G --> H[Implementation]
    H --> I[Integrated validation]
```

## Runtime package

The installed skill contains:

```text
ui-ux-skill-orchestrator/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── config/
│   └── skill-modules.json
├── references/
│   ├── capability-map.md
│   ├── synthesis-contract.md
│   └── workflow-recipes.md
└── scripts/
    ├── inventory_ui_skills.py
    ├── setup.py
    └── validate.py
```

`SKILL.md` contains the operating loop. Detailed maps and schemas load only
when needed. Scripts use the Python standard library and can run without
loading their implementation into the agent's context.

## Authority

The fixed precedence is:

1. explicit user requirements;
2. approved incumbent design system;
3. platform and accessibility conventions;
4. selected lead;
5. narrow specialists;
6. generic defaults.

This prevents a font database from replacing brand typography, a motion
specialist from changing the page direction, or a generalist from overriding
accessibility requirements.

## Module registry

`config/skill-modules.json` is the extension point. Registered modules get
explicit capabilities, specialties, aliases, provenance, and setup behavior.
Unregistered UI/UX skills remain discoverable and can be evaluated at runtime,
but are never installed automatically.

Core modules cover common frontend work. Integration modules are offered only
when the current task needs their narrow capability, such as a Stitch or Figma
workflow or a future domain-specific specialist.

## Installation security

The orchestrator itself is installed separately from specialists. `setup.py`
performs a read-only check first, shows missing sources, requests one terminal
confirmation, delegates installation to `npx skills`, and verifies discovery.

No dependency code is imported by the orchestrator. A user can decline every
installation and still receive a reduced fallback workflow.
