# Workflow Recipes

Use the closest recipe, then remove phases and specialists that do not affect the request.

## Single component: button, input, card, modal, table

1. Treat the existing component library and tokens as lead.
2. Inspect sibling components before proposing new primitives.
3. Assign component anatomy and state behavior to the narrowest component/UX specialist available.
4. Use `ui-ux-pro-max` only for unresolved touch, UX, palette, or typography evidence.
5. Use `ui-animation` only when motion is requested or behavior is non-trivial.
6. Define default, hover, focus-visible, active, disabled, loading, error, and success states as applicable.
7. Implement in the current framework, then test keyboard, screen reader, touch, narrow viewport, and long labels.

Do not redesign global fonts, palette, or spacing for one component.

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

## Audit or polish

1. Use `impeccable` as evaluation lead.
2. Add an accessibility, performance, or motion specialist only where the audit scope requires it.
3. Separate findings from fixes when the user asked only for review.
4. Rank findings by user impact and confidence.
5. If fixes are authorized, batch them, inspect representative screenshots, and confirm once.
6. Do not turn polish into an unrequested redesign.

## Typography or font task

1. Preserve existing fonts unless replacement is requested.
2. Use `ui-ux-pro-max` or a typography specialist for candidate discovery and pairing evidence.
3. Let the lead decide personality and role fit.
4. Define display, heading, body, label, caption, and data roles; omit roles the product does not need.
5. Define size, weight, line height, letter spacing, measure, fallback, loading, and international character requirements.
6. Validate hierarchy at mobile and desktop widths.

## Color or palette task

1. Start with existing semantic roles and brand constraints.
2. Use `ui-ux-pro-max` for candidate palettes.
3. Let the lead select and calibrate the direction.
4. Convert raw colors into semantic tokens for surfaces, text, borders, actions, feedback, focus, and data.
5. Validate contrast, color-blind distinguishability, light/dark modes, and non-color indicators.

## Motion task

1. Use `ui-animation` as lead.
2. Preserve settled layout, type, and palette.
3. State the motion purpose: feedback, continuity, orientation, or deliberate delight.
4. Define enter, update, exit, interruption, reduced-motion, touch, and performance behavior.
5. Implement with the lowest-overhead appropriate primitive.
6. Retoggle rapidly and validate reduced motion and device behavior.

## Design-system creation or extraction

1. Inventory existing tokens, components, naming, styling, accessibility, and documentation.
2. If Figma MCP is connected and Figma-to-code rules are requested, use `figma-create-design-system-rules`.
3. Use `ui-ux-pro-max` for candidate fonts, palettes, product patterns, and charts—not as the source of repository conventions.
4. Use the appointed lead to settle identity and system character.
5. Define semantic tokens, component anatomy, variants, states, responsive rules, motion tokens, and governance.
6. Validate with at least one representative component.

## Stitch workflow

1. Use `taste-design` as lead when the deliverable is Stitch-oriented `DESIGN.md` or Stitch screen generation.
2. Use `ui-ux-pro-max` for supporting research when helpful.
3. Keep exact semantic values and anti-patterns in the generated design system.
4. Validate that implementation output still follows repository and accessibility constraints.

## Figma-to-code rules

1. Confirm Figma MCP is connected.
2. Use `figma-create-design-system-rules` to inspect the codebase and generate persistent conventions.
3. Keep the generated rules repository-specific and actionable.
4. Do not use placeholder assets when real Figma or repository assets exist.
5. Test the rules by implementing one representative component and comparing it with the source.
