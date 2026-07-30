---
name: ui-ux-skill-orchestrator
description: Route UI/UX and visual frontend work to the smallest high-value combination of installed design skills, then reconcile their guidance into one production-ready blueprint and implementation. Use first when creating, redesigning, reviewing, or polishing pages, components, design systems, typography, color palettes, spacing, layout, responsive behavior, accessibility, motion, Figma/Stitch workflows, or frontend UX—especially when several UI skills overlap and the agent must decide which specialist owns each concern.
---

# UI/UX Skill Orchestrator

Select specialists; do not compete with them. Establish one source of design truth, appoint one lead, assign narrow ownership to supporting skills, and merge their decisions before implementation.

## Step 0: Check specialist readiness

At the first UI/UX request in a session, determine the host agent and run:

```bash
python3 <skill-base-dir>/scripts/setup.py --agent <host> --check
```

If core modules are missing, show the user the missing names and original
sources, then ask permission to install them. After explicit approval, run:

```bash
python3 <skill-base-dir>/scripts/setup.py --agent <host>
```

The setup command presents one terminal `yes/no` confirmation. Use `--yes` only
when the user already gave explicit installation approval. Never install
third-party skills silently.

Registered integration modules are optional. Check or offer only the
integration required by the current task:

```bash
python3 <skill-base-dir>/scripts/setup.py \
  --agent <host> \
  --only stitch-design-taste
```

If the user declines installation, continue with the fallback rules in
[references/capability-map.md](references/capability-map.md). Missing
specialists reduce available evidence; they do not automatically block the
task.

## Non-negotiable rules

1. Honor the user brief and existing product system before any skill preference.
2. Use the fewest skills that cover the actual request. Never invoke every design skill.
3. Appoint exactly one lead for visual direction or evaluation.
4. Give each specialist exclusive ownership of a concern. Do not let two skills independently redesign the same axis.
5. Resolve disagreements before writing code. Emit one value, pattern, or rule per decision—not a collage of alternatives.
6. Preserve incumbent tokens, components, behavior, and content for a refinement. Replace them only when the user requests a redesign.
7. Continue through implementation when the user asks to build or change something. Do not stop after recommending skills.
8. Validate the integrated result, not isolated specialist advice.

## Step 1: Discover the available skill portfolio

Determine the host agent (`codex`, `antigravity`, or `all`) and run once:

```bash
python3 <skill-base-dir>/scripts/inventory_ui_skills.py --agent <host> --format markdown
```

Add `--query "<user request>"` to rank likely specialists. Treat the output as an inventory, not the final routing decision.

If the script is unavailable, inspect the host's advertised skills and their `name` and `description`. Never claim an unavailable skill was invoked.

For each selected skill, use native skill invocation when the host supports it. Otherwise read the selected `SKILL.md` from the inventory path. Read each selected instruction file completely before applying it.

The registered portfolio is data-driven. Read
[config/skill-modules.json](config/skill-modules.json) only when checking
dependencies, aliases, provenance, or extending the portfolio. Treat an
unregistered discovered skill as a dynamic candidate and evaluate it using the
rules in [references/capability-map.md](references/capability-map.md).

## Step 2: Establish design truth

Inspect the target and record:

- user and job-to-be-done;
- surface: marketing, product, dashboard, form, content, mobile, or design system;
- task: create, redesign, refine, audit, debug, or translate from design;
- current visual authority: design tokens, theme, `DESIGN.md`, components, CSS, screenshots, or Figma;
- stack and platform;
- requested aesthetic, brand, accessibility, performance, and delivery constraints.

Use this precedence:

1. explicit user requirements;
2. existing approved product/design system;
3. platform and accessibility conventions;
4. appointed lead skill;
5. specialist recommendations;
6. generic defaults.

Do not infer greenfield from a missing `DESIGN.md`. Existing code can still be the visual authority.

## Step 3: Decompose the request

Mark only the concerns that can change:

- UX structure and user flow
- creative direction and visual identity
- typography
- color and contrast
- spacing, grid, and responsive layout
- components and interaction states
- motion and animation
- accessibility
- data visualization
- design-system rules and tokens
- framework implementation
- performance and production hardening
- visual review and polish

Read [references/capability-map.md](references/capability-map.md) to choose the lead and specialists. Read [references/workflow-recipes.md](references/workflow-recipes.md) when the task matches a common page, component, audit, Figma, Stitch, or motion workflow.

## Step 4: Form the smallest useful team

Use this budget:

| Scope | Portfolio |
|---|---|
| Narrow fix or single component | 1 lead or specialist; add 1 reviewer only if risk warrants it |
| Page or focused feature | 1 lead + up to 2 specialists; allow a third only when research, motion, and production validation are all independently open |
| Product surface or redesign | 1 lead + up to 3 specialists |
| Design system or multi-surface program | 1 lead + up to 4 specialists, phased rather than simultaneous |

Typical ownership:

- lead: product mode, aesthetic thesis, hierarchy, and final coherence;
- typography/color research: candidate evidence only;
- layout specialist: spacing, grid, density, and responsive behavior;
- component specialist: anatomy, states, semantics, and touch behavior;
- motion specialist: purpose, easing, timing, interruption, reduced motion;
- accessibility specialist: WCAG, keyboard, focus, semantics, contrast;
- implementation specialist: framework-native code and performance;
- reviewer: bounded audit after integration.

Exclude any skill whose contribution is already covered or irrelevant. Record the exclusion when it prevents obvious overlap.

When typography, palette, chart choice, or product-pattern research is explicitly requested and is not already fixed by the product system, include the strongest evidence specialist for that axis. Evidence specialists propose and test candidates; they do not replace the lead's final creative judgment.

## Step 5: Create the routing brief

Keep this concise and internal unless the user asks for a plan or the routing choice materially changes the work:

```text
Surface / mode:
Task:
Incumbent authority:
Lead:
Specialists:
Ownership:
Excluded:
Validation owner:
```

For complex work, follow the complete merge schema in [references/synthesis-contract.md](references/synthesis-contract.md).

## Step 6: Execute in dependency order

Run only the phases the task needs:

1. **Evidence** — inspect product truth, code, assets, and constraints.
2. **UX** — settle user job, information hierarchy, flow, content, and states.
3. **Direction** — settle one visual thesis and signature.
4. **System** — settle type, color, spacing, grid, radius, elevation, and icon rules.
5. **Components** — settle anatomy, variants, interaction states, copy, and responsive behavior.
6. **Motion** — add purposeful motion only after layout and states are stable.
7. **Implementation** — translate the merged blueprint into the existing stack.
8. **Validation** — test accessibility, responsive behavior, interaction, motion, performance, and visual coherence.

Do not ask later phases to reopen settled upstream decisions unless they find a concrete violation. Return the issue to the owner, revise once, then continue.

When independent read-only analysis can run in parallel, give every specialist the same brief and strict ownership boundary. Never parallelize competing visual directions for implementation unless the user explicitly requests alternatives.

## Step 7: Merge specialist output

Use a decision ledger for every contested axis:

| Axis | Owner | Evidence | Final decision | Rejected conflict |
|---|---|---|---|---|

Apply these arbitration rules:

- project tokens beat generated palettes and scales;
- user-pinned aesthetics beat anti-pattern preferences;
- accessibility and platform requirements beat decorative choices;
- the lead controls identity and hierarchy;
- domain specialists control mechanics inside the lead's direction;
- measured evidence beats taste assertions;
- a narrower specialist beats a generalist only within its assigned concern.

Do not average conflicting recommendations. Choose one, document why, and propagate it through tokens, components, states, and tests.

## Step 8: Validate the combined result

Verify proportionately:

- no hardcoded values where project tokens exist;
- typography roles, line length, hierarchy, and loading behavior;
- semantic color roles and contrast;
- spacing rhythm, alignment, container consistency, and density;
- default, hover, focus-visible, active, disabled, loading, error, and success states;
- keyboard and screen-reader behavior;
- mobile, tablet, desktop, zoom, long content, and localization pressure;
- reduced-motion behavior and animation interruption;
- layout stability, asset optimization, and framework performance;
- screenshots at representative widths when the environment supports them.

Run one integrated review, fix findings in one batch, and confirm once. Avoid endless polish loops.

## Output contract

For implementation requests, deliver the working result and summarize the routing only when useful. For planning-only requests, return:

1. selected portfolio and ownership;
2. consolidated blueprint;
3. implementation order;
4. validation gates;
5. unresolved inputs that genuinely block execution.

Never return six disconnected skill reports. The output must read as one design team made one decision.
