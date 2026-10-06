# Routing scenarios

Each scenario matches a golden test in `tests/test_route.py`. Reproduce any of
them in planning mode, which treats every registered module as installed:

```bash
python3 skills/ui-ux-skill-orchestrator/scripts/route.py \
  --assume-installed \
  --query "Build a bold landing page for a coffee brand with smooth scroll animations"
```

## Greenfield landing page with motion

Request: "Build a bold landing page for a coffee brand with smooth scroll
animations" (core modules installed)

- **Rule:** `greenfield`
- **Lead:** `frontend-design`, which owns direction
- **Specialist:** `ui-animation` for motion
- **Validation:** `impeccable`
- **Excluded:** `mies` (single-lead rule) and `ui-ux-pro-max`, because no
  typography, palette, chart, or UX evidence is open

## Landing page with open evidence, motion, and accessibility

Request: "Build a landing page for a fintech app; choose the color palette and
font pairing, make it accessible, and add scroll animations"

- **Scope:** `page`; "app" is context, the explicit deliverable is the page
- **Specialists:** `ui-ux-pro-max` (color, typography), `ui-animation`
  (motion), `fixing-accessibility` (accessibility). The third specialist is
  allowed only because evidence, motion, and validation are all open
- **Validation:** `impeccable`

## Calm analytics dashboard

Request: "Redesign our analytics dashboard to feel calm and minimal"

- **Rule:** `dashboard`
- **Lead:** `mies`
- **Specialist:** `ui-ux-pro-max` for data visualization
- **Validation:** `impeccable`

## Accessibility audit

Request: "Audit the checkout form for accessibility and keyboard focus"

- **Rule:** `accessibility-focus`
- **Lead:** `fixing-accessibility`
- **Validation:** `ui-verification` when browser tooling is available,
  otherwise `impeccable`
- **Check before use:** browser automation for `ui-verification`

## Single component state

Request: "Add an error state to the email input"

- **Rule:** `single-component`
- **Lead:** the existing design system
- **Validation:** none by default; the host runs the component checks in
  Step 8
- **Excluded:** every visual-direction lead

## Spacing fix on an existing page

Request: "Fix the spacing and alignment on the settings page"

- **Rule:** `existing-refinement`
- **Lead:** the existing design system
- **Specialist:** `mies` for spacing and alignment only
- **Validation:** `impeccable`

## Motion-only fix

Request: "Smooth out the janky dropdown animation"

- **Rule:** `motion-focus`, scope `component`
- **Lead:** `ui-animation`; layout, type, and color stay fixed
- **Excluded:** visual-direction leads, with the reason "Not needed"
- **When `ui-animation` is missing:** the existing system leads and the brief
  prints the `setup.py --only ui-animation` command to offer

## Figma rules versus Figma frames

- "Create Figma design system rules for this codebase" →
  `figma-create-design-system-rules`, requires `figma-mcp`
- "Implement this Figma frame as a React page" → `figma-implement-design`;
  `frontend-design` and `mies` are excluded because the frame is the visual
  authority

Without a connected Figma MCP server, stop the tool-bound workflow, explain the
missing connection, and never fabricate Figma-derived rules or values.

## Stitch design system

Request: "Generate a Stitch DESIGN.md for our app"

- **Rule:** `stitch-design-system`, scope `system`
- **Lead:** `stitch-design-taste` (or its `taste-design` alias)
- **Excluded:** `frontend-design`, because the Stitch system owns direction
