# Workflow Recipes

Use the closest recipe, then remove phases and specialists that do not affect the request. `scripts/route.py` names the recipe that matches its draft brief; each `recipe` value in `config/routing-rules.json` must match a heading below.

## Single component: button, input, card, modal, table

1. Treat the existing component library and tokens as lead.
2. Inspect sibling components before proposing new primitives.
3. Assign component anatomy and state behavior to the narrowest component/UX specialist available.
4. Use `ui-ux-pro-max` only for unresolved touch, UX, palette, or typography evidence.
5. Use `ui-animation` only when motion is requested or behavior is non-trivial.
6. Use `fixing-accessibility` when semantics, labels, keyboard, or focus behavior are in scope.
7. Define default, hover, focus-visible, active, disabled, loading, error, and success states as applicable.
8. Implement in the current framework, then test keyboard, screen reader, touch, narrow viewport, and long labels.

Do not redesign global fonts, palette, or spacing for one component. Add a reviewer only when the change is risky.

## Greenfield landing page

1. Use `frontend-design` as lead for subject, audience, page job, visual thesis, typography personality, palette intent, layout signature, and one memorable element.
2. Use `ui-ux-pro-max` for product-pattern, font, palette, landing-structure, and stack evidence. It is required when typography, palette, or style research is explicitly open.
3. Let the lead choose from the evidence; do not paste database output directly into the design.
4. Use `impeccable` as production integrator for responsive behavior, real content, states, assets, hardening, and bounded visual QA.
5. Add `ui-animation` only for a deliberate motion concept. When both evidence and motion are explicitly required, the page may use three specialists so production validation is not displaced.
6. Use `mies` as a final subtractive reviewer only when the direction needs restraint.

## Dashboard or dense product surface

1. Treat user tasks, scan paths, and incumbent components as primary.
2. Use `impeccable` in Operate mode or `mies` for a restrained, high-density lead.
3. Use `ui-ux-pro-max` for chart selection, accessible palette candidates, typography, and stack guidance.
4. Keep motion functional and low frequency; use `ui-animation` for drawers, filters, state transitions, or complex data changes.
5. Validate empty, loading, error, partial-data, overflow, localization, keyboard, and small-screen states.

## Existing-interface redesign

1. Clarify whether the user wants refinement or replacement.
2. Inventory current product truth and retain factual content, behavior, and platform affordances.
3. Use `impeccable` as lead for holistic redesign; use `frontend-design` instead when the central need is a completely new identity.
4. Use `mies` for a bounded reduction and hierarchy pass, not a competing direction.
5. Query `ui-ux-pro-max` only for axes that are genuinely open.
6. Implement the chosen world consistently; never split the difference between old and new.

## Existing-interface refinement or fix

1. Treat existing tokens, components, content, and behavior—or the supplied reference design—as the lead.
2. Reproduce the defect or name the exact refinement target before editing.
3. Give each open concern one narrow owner: `ui-animation` for motion, `fixing-accessibility` for accessibility, `mies` for spacing, alignment, and density reduction, `ui-ux-pro-max` for open type, color, or chart evidence.
4. Fix in place with existing tokens and primitives; do not introduce a new visual direction.
5. Validate once with `impeccable`, or with `ui-verification` when browser tooling is available, and check states, breakpoints, and keyboard paths for regressions.

## Restrained or minimal direction

1. Use `mies` as lead for reduction, proportion, spacing, alignment, and density.
2. Remove before adding: cut decoration, duplicate emphasis, and noise before introducing new elements.
3. Keep incumbent tokens and content unless the user asks for replacement.
4. Use `ui-ux-pro-max` only for genuinely open typography or palette evidence.
5. Keep motion functional and quiet; use `ui-animation` only when motion is requested.
6. Let `impeccable` validate responsive behavior, states, and hardening without adding a competing direction.
7. Confirm hierarchy, focus visibility, and contrast survive the reduction.

## Audit or polish

1. Use `impeccable` as evaluation lead.
2. Add `fixing-accessibility`, `typography-audit`, or `ui-animation` only where the audit scope requires that concern.
3. Use `ui-verification` for measured browser evidence when a runnable app and browser tooling are available.
4. Separate findings from fixes when the user asked only for review.
5. Rank findings by user impact and confidence.
6. If fixes are authorized, batch them, inspect representative screenshots, and confirm once.
7. Do not turn polish into an unrequested redesign.

## Accessibility audit or fix

1. Use `fixing-accessibility` as lead; fall back to `impeccable` audit mode when it is not installed.
2. Check semantics, accessible names, keyboard order, focus visibility and trapping, contrast, target size, reduced motion, and announcements.
3. Preserve the visual direction; change appearance only where a requirement fails.
4. Prefer native elements and existing accessible primitives over ARIA patches.
5. Validate with `ui-verification` (browser checks and screenshots) when available; otherwise state which checks remain code-level only.

## Typography or font task

1. Preserve existing fonts unless replacement is requested.
2. Use `ui-ux-pro-max` or a typography specialist for candidate discovery and pairing evidence.
3. Use `typography-audit` to audit or validate existing type: hierarchy, scale, measure, line height, and font loading.
4. Let the lead decide personality and role fit.
5. Define display, heading, body, label, caption, and data roles; omit roles the product does not need.
6. Define size, weight, line height, letter spacing, measure, fallback, loading, and international character requirements.
7. Validate hierarchy at mobile and desktop widths.

## Color or palette task

1. Start with existing semantic roles and brand constraints.
2. Use `ui-ux-pro-max` for candidate palettes.
3. Let the lead select and calibrate the direction.
4. Convert raw colors into semantic tokens for surfaces, text, borders, actions, feedback, focus, and data.
5. Validate contrast, color-blind distinguishability, light/dark modes, and non-color indicators; `fixing-accessibility` owns that gate when installed.

## Motion task

1. Use `ui-animation` as lead.
2. Preserve settled layout, type, and palette.
3. State the motion purpose: feedback, continuity, orientation, or deliberate delight.
4. Define enter, update, exit, interruption, reduced-motion, touch, and performance behavior.
5. Implement with the lowest-overhead appropriate primitive.
6. Retoggle rapidly and validate reduced motion and device behavior; use `ui-verification` for frame-level browser checks when available.

## Design-system creation or extraction

1. Inventory existing tokens, components, naming, styling, accessibility, and documentation.
2. If Figma MCP is connected and Figma-to-code rules are requested, use `figma-create-design-system-rules`.
3. Use `ui-ux-pro-max` for candidate fonts, palettes, product patterns, and charts—not as the source of repository conventions.
4. Use the appointed lead to settle identity and system character.
5. Define semantic tokens, component anatomy, variants, states, responsive rules, motion tokens, and governance.
6. Validate with at least one representative component.

## Stitch workflow

1. Use `stitch-design-taste` or its installed `taste-design` alias as lead when the deliverable is Stitch-oriented `DESIGN.md` or Stitch screen generation.
2. Use `ui-ux-pro-max` for supporting research when helpful.
3. Keep exact semantic values and anti-patterns in the generated design system.
4. Validate that implementation output still follows repository and accessibility constraints.

## Figma-to-code rules

1. Confirm Figma MCP is connected.
2. Use `figma-create-design-system-rules` to inspect the codebase and generate persistent conventions.
3. Keep the generated rules repository-specific and actionable.
4. Do not use placeholder assets when real Figma or repository assets exist.
5. Test the rules by implementing one representative component and comparing it with the source.

## Figma design to code

1. Confirm Figma MCP is connected and a frame link or desktop selection is available.
2. Use `figma-implement-design` as lead; the Figma design is the visual authority, so exclude competing direction skills.
3. Map Figma variables and styles to existing repository tokens and components before creating new ones.
4. Use real exported assets; never substitute placeholders when the source provides them.
5. Add `fixing-accessibility` or `ui-animation` only for accessibility or motion the frame does not specify.
6. Validate visual parity with `ui-verification` screenshots when available, or with `impeccable`, at the frame's breakpoints.

## Browser verification

1. Confirm a runnable app and Playwright or Chrome DevTools browser tooling.
2. Use `ui-verification` as lead; fall back to `impeccable` with code-level checks when it is not installed.
3. Capture representative widths, interaction states, keyboard paths, and reduced-motion behavior.
4. Record measured evidence—screenshots, console errors, layout shifts, timings—rather than assertions.
5. Report each failure with its owner so fixes route back to the responsible specialist.
