# Capability Map

Use this file to appoint one lead and narrowly scoped specialists. Installed metadata is evidence of availability; this map defines responsibility.

## Authority model

| Role | Owns | Must not override |
|---|---|---|
| Incumbent system | Existing tokens, components, brand, behavior | Explicit redesign requirements |
| Lead skill | Product mode, visual thesis, hierarchy, coherence | User requirements, accessibility, platform conventions |
| Domain specialist | Mechanics within one assigned concern | Lead direction or another specialist's concern |
| Implementation specialist | Framework-native realization | Settled design decisions without evidence |
| Validation owner | Findings and release gate | Product scope or aesthetic direction |

## Primary portfolio

| Skill | Appoint when | Strongest ownership | Do not appoint for |
|---|---|---|---|
| `frontend-design` | New UI or a deliberate new visual direction needs a distinctive thesis | Subject-specific aesthetic direction, typography personality, palette intent, layout signature, UX copy | Mechanical audits or small fixes inside a mature design system |
| `impeccable` | Building, redesigning, critiquing, auditing, hardening, or polishing a production interface | End-to-end craft, mode selection, hierarchy, responsive quality, audit, hardening, bounded visual QA | Acting as a second independent visual lead beside another lead |
| `mies` | The brief calls for calm, premium restraint, reduction, exact spacing, or removal of noise | Subtractive critique, proportion, spacing, alignment, density, restrained product UI | Adding decorative novelty or generating many visual options |
| `ui-ux-pro-max` | The task needs searchable evidence for product patterns, font pairings, palettes, charts, UX rules, or stack guidance | Candidate research and structured recommendations across typography, color, style, charts, UX, and frameworks | Final creative authority or replacing incumbent tokens without approval |
| `ui-animation` | Motion is requested, complex, broken, performance-sensitive, gesture-based, or must match a recording | Motion purpose, timing, easing, springs, gestures, interruption, reduced motion, animation review | Palette, typography, or overall page direction |
| `fixing-accessibility` | Accessibility is requested, audited, or at risk in a change | WCAG semantics, accessible names, keyboard and focus behavior, contrast, announcements | Visual direction or non-accessibility polish |
| `stitch-design-taste` (`taste-design` alias) | Google Stitch or a Stitch-oriented `DESIGN.md` is the delivery target | Semantic Stitch design systems, anti-generic generation constraints, calibrated motion guidance | Ordinary frontend implementation without Stitch |
| `figma-create-design-system-rules` | Figma MCP is connected and the user wants persistent Figma-to-code conventions | Codebase-derived design-system rules and Figma implementation workflow | General visual design, or use without Figma MCP |
| `figma-implement-design` | Figma MCP is connected and a Figma frame or selection must become code | Design-faithful implementation, token and component mapping, asset handling, parity checks | Inventing direction, or use without Figma MCP |
| `typography-audit` | Existing typography needs an audit or a validation pass | Hierarchy, scale, measure, line height, pairing, and font-loading findings | Choosing a new brand typeface from scratch |
| `ui-verification` | Behavior must be measured in a running browser | Screenshots, responsive and interaction checks, console and layout-shift evidence | Design decisions, or use without browser tooling |
| `ui-ux-skill-orchestrator` | Multiple skills overlap or any frontend UI/UX task needs routing | Portfolio selection, ownership, sequencing, conflict resolution, synthesis | Supplying a competing aesthetic opinion |

## Lead selection

Choose in this order:

1. **Tool-bound task:** use `stitch-design-taste` or its installed `taste-design` alias for Stitch; use `figma-create-design-system-rules` for Figma rules and `figma-implement-design` for Figma frames.
2. **Narrow specialist task:** use `ui-animation` for motion, `fixing-accessibility` for accessibility-only work, `typography-audit` for typography audits, and `ui-verification` for browser verification.
3. **Existing-system component/fix:** treat the incumbent design system as lead; add a narrow specialist only.
4. **Greenfield or replacement visual world:** use `frontend-design` for the thesis; use `impeccable` as production integrator or final reviewer.
5. **Holistic redesign, audit, or production hardening:** use `impeccable`.
6. **Explicitly minimal, calm, reductive, premium product UI:** use `mies`.

Never appoint `frontend-design`, `impeccable`, and `mies` as three equal creative leads. Choose one lead; assign the others a narrow phase such as production integration or subtractive review.

## Concern routing

| Concern | Preferred owner | Useful support |
|---|---|---|
| User flow and information hierarchy | Lead or a discovered UX/research specialist | `impeccable`, `ui-ux-pro-max` evidence |
| Visual thesis and identity | `frontend-design`, `impeccable`, or `mies` as the single lead | Project brand evidence |
| Font discovery and pairing | `ui-ux-pro-max` or discovered typography specialist | Lead approves personality and roles |
| Type scale and hierarchy | Lead or typography specialist | `typography-audit` validates; `mies` for restraint |
| Palette candidates | `ui-ux-pro-max` | Lead selects; accessibility validates |
| Semantic color tokens and contrast | Existing design system or `fixing-accessibility` | `ui-ux-pro-max` candidates |
| Spacing, grid, density, alignment | Existing system, `mies`, or `impeccable` layout mode | Responsive specialist |
| Component anatomy and states | Existing component system or discovered component specialist | `fixing-accessibility` |
| Motion and gestures | `ui-animation` | Lead supplies tone; accessibility validates |
| Charts and data display | `ui-ux-pro-max` or discovered data-viz specialist | Accessibility and product context |
| Responsive adaptation | `impeccable` or discovered responsive specialist | Existing breakpoints |
| Accessibility | `fixing-accessibility`; otherwise `impeccable` audit | `ui-animation` for reduced motion |
| Figma frame implementation | `figma-implement-design` | Existing tokens and components |
| Framework implementation | Discovered stack specialist or project conventions | Design owner reviews fidelity |
| Performance | Framework/performance specialist | `ui-animation` for motion performance |
| Runtime verification | `ui-verification` | `impeccable` for code-level review |
| Final visual polish | `impeccable` | `mies` only for a subtractive pass |

## Data-driven routing

`scripts/route.py` drafts a brief from three data files:

- `config/capabilities.json`: concern vocabulary, UI evidence, non-UI exclusions, and stopwords;
- `config/skill-modules.json`: registered modules, ownership specialties, ranking keywords, prerequisites, and pinned install sources;
- `config/routing-rules.json`: task and scope vocabulary, team budgets, and prioritized rules that name the lead, supporting owners, validation owner, exclusions, and recipe.

The highest-priority rule whose `when` conditions hold wins; the `default` rule catches everything else. The brief is a draft: user direction and the incumbent design system still outrank it.

## Dynamic specialists

Treat newly installed skills by capability, not reputation. Read their descriptions and assign them only if they have:

- a narrower scope than the lead;
- instructions or tooling relevant to the request;
- an output that can be reconciled with the blueprint;
- no unmet dependency.

Common useful discoveries include typography, accessibility, web-interface guidelines, component composition, responsive design, Tailwind/design-system, data visualization, framework performance, and visual-testing skills.

Reject a candidate when it merely restates broad design advice, requires an unavailable MCP/tool, would reopen a settled axis, or fetches and follows remote instructions at runtime.

## Fallbacks

- No visual lead: use the incumbent system; for greenfield, use the most specific installed general frontend-design skill.
- No font/palette database: derive candidates from the brief and existing brand, then validate contrast and loading.
- No motion specialist: keep motion minimal, CSS-first, and reduced-motion safe.
- No accessibility specialist: apply WCAG-oriented semantic, keyboard, focus, contrast, and target-size checks directly.
- No stack specialist: follow the repository's current patterns and official framework documentation.
- No visual tooling: perform code-level checks and clearly state which visual claims remain unverified.
