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
│   ├── agents.json
│   ├── capabilities.json
│   ├── routing-rules.json
│   └── skill-modules.json
├── references/
│   ├── capability-map.md
│   ├── synthesis-contract.md
│   └── workflow-recipes.md
└── scripts/
    ├── inventory_ui_skills.py
    ├── route.py
    ├── setup.py
    └── validate.py
```

`SKILL.md` contains the operating loop. Detailed maps and schemas load only
when needed. Scripts use the Python standard library (3.9 or newer) and can run
without loading their implementation into the agent's context.

## Data-driven catalog

Behavior that changes as the ecosystem changes lives in JSON, not code:

| File                        | Owns                                                                                                                                        |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `config/skill-modules.json` | Registered modules: tier, role, capabilities, specialties, ranking keywords, `lead_capable`, tool prerequisites, and pinned install sources |
| `config/capabilities.json`  | The concern taxonomy: description signals, extra query terms, UI evidence, non-UI exclusions, and stopwords                                 |
| `config/agents.json`        | Project and global skill folders for each supported agent, including depth and hidden-folder rules                                          |
| `config/routing-rules.json` | Task and scope vocabulary, team budgets per scope, and prioritized routing rules                                                            |

`validate.py` checks every file's schema and cross-references, so a typo in a
module id, capability, or recipe name fails CI instead of misrouting at
runtime.

## Discovery

`inventory_ui_skills.py` scans each agent's folders, project folders first so
local copies override global ones. It follows symlinked skill folders once,
skips dependency and VCS folders, and stops descending at a folder that holds a
`SKILL.md`. Registered modules are deduplicated across aliases.

Unregistered skills are classified from their name and description. One is
listed only when it matches a capability and its UI evidence outweighs
non-UI context, so a Spring Boot or PostgreSQL skill that mentions "layout" or
"tokens" stays out.

With `--query`, skills are ranked: a specialty match outweighs a broad
capability match, broad generalists are discounted, module keywords add a
bounded bonus, and integration modules need a specific trigger.

## Routing

`route.py` turns a request into a draft brief:

1. infer concerns from the taxonomy, the task, and the narrowest explicit
   scope;
2. select the highest-priority rule whose `when` conditions hold;
3. appoint the first installed lead candidate, or fall back to the incumbent
   system;
4. choose a validation owner (none by default for a single component);
5. add supporting owners for open concerns within the scope budget, never
   giving one concern to two members;
6. list exclusions, missing preferred modules with install commands, tool
   prerequisites, and uncovered concerns.

The brief is deliberately a draft. The agent confirms it against the product's
design truth, and explicit user direction always wins.

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
Modules that live in a subfolder of a larger repository are installed from a
pinned tree URL, so the Skills CLI installs exactly that folder.

No dependency code is imported by the orchestrator. A user can decline every
installation and still receive a reduced fallback workflow. Candidates that
fetch and follow remote instructions at runtime are not registered, because
their behavior can change without a reviewable release.
