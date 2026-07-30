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
| `taste-design` | Google Stitch or a Stitch-oriented `DESIGN.md` is the delivery target | Semantic Stitch design systems, anti-generic generation constraints, calibrated motion guidance | Ordinary frontend implementation without Stitch |
| `figma-create-design-system-rules` | Figma MCP is connected and the user wants persistent Figma-to-code conventions | Codebase-derived design-system rules and Figma implementation workflow | General visual design, or use without Figma MCP |
| `ui-ux-skill-orchestrator` | Multiple skills overlap or any frontend UI/UX task needs routing | Portfolio selection, ownership, sequencing, conflict resolution, synthesis | Supplying a competing aesthetic opinion |

## Lead selection

Choose in this order:

1. **Tool-bound task:** use `taste-design` for Stitch or `figma-create-design-system-rules` for Figma rules.
2. **Narrow specialist task:** use `ui-animation` for motion, an accessibility specialist for accessibility-only work, or a typography specialist for typography-only work.
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
| Type scale and hierarchy | Lead or typography specialist | `mies` for restraint |
| Palette candidates | `ui-ux-pro-max` | Lead selects; accessibility validates |
| Semantic color tokens and contrast | Existing design system or accessibility specialist | `ui-ux-pro-max` candidates |
| Spacing, grid, density, alignment | Existing system, `mies`, or `impeccable` layout mode | Responsive specialist |
| Component anatomy and states | Existing component system or discovered component specialist | Accessibility specialist |
| Motion and gestures | `ui-animation` | Lead supplies tone; accessibility validates |
| Charts and data display | `ui-ux-pro-max` or discovered data-viz specialist | Accessibility and product context |
| Responsive adaptation | `impeccable` or discovered responsive specialist | Existing breakpoints |
| Accessibility | Discovered accessibility specialist; otherwise `impeccable` audit | `ui-animation` for reduced motion |
| Framework implementation | Discovered stack specialist or project conventions | Design owner reviews fidelity |
| Performance | Framework/performance specialist | `ui-animation` for motion performance |
| Final visual polish | `impeccable` | `mies` only for a subtractive pass |

## Dynamic specialists

Treat newly installed skills by capability, not reputation. Read their descriptions and assign them only if they have:

- a narrower scope than the lead;
- instructions or tooling relevant to the request;
- an output that can be reconciled with the blueprint;
- no unmet dependency.

Common useful discoveries include typography, accessibility, web-interface guidelines, component composition, responsive design, Tailwind/design-system, data visualization, framework performance, and visual-testing skills.

Reject a candidate when it merely restates broad design advice, requires an unavailable MCP/tool, or would reopen a settled axis.

## Fallbacks

- No visual lead: use the incumbent system; for greenfield, use the most specific installed general frontend-design skill.
- No font/palette database: derive candidates from the brief and existing brand, then validate contrast and loading.
- No motion specialist: keep motion minimal, CSS-first, and reduced-motion safe.
- No accessibility specialist: apply WCAG-oriented semantic, keyboard, focus, contrast, and target-size checks directly.
- No stack specialist: follow the repository's current patterns and official framework documentation.
- No visual tooling: perform code-level checks and clearly state which visual claims remain unverified.
