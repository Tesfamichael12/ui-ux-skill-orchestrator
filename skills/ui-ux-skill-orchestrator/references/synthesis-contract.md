# Synthesis Contract

Use this contract for page-level, redesign, design-system, or multi-specialist work.

## Shared brief

Give every selected specialist the same immutable core:

```text
User:
User job:
Surface and product mode:
Task and allowed degree of change:
Current visual authority:
Stack and platform:
Content/assets:
Pinned requirements:
Accessibility/performance targets:
Assigned concern:
Decisions already closed:
Expected output:
```

Do not ask specialists to invent missing facts that another phase owns.

## Specialist output schema

Require each specialist to return:

```text
Concern:
Evidence inspected:
Recommendation:
Concrete values/patterns:
Constraints:
Conflicts detected:
Validation:
Confidence:
```

Reject broad essays, duplicated project analysis, and recommendations outside the assigned concern.

## Consolidated blueprint

Merge approved decisions into this order:

1. **Intent** — user, job, surface, success, product mode.
2. **Authority** — incumbent artifacts and precedence.
3. **Direction** — visual thesis, facets, anti-reference, signature.
4. **Typography** — families, roles, scale, weights, metrics, loading.
5. **Color** — semantic tokens, states, contrast, light/dark behavior.
6. **Spatial system** — container, grid, spacing scale, density, radii, elevation.
7. **Responsive system** — breakpoints/containers, reflow, touch, overflow.
8. **Components** — primitives, anatomy, variants, states, copy.
9. **Motion** — purpose, duration, easing, choreography, interruption, reduced motion.
10. **Accessibility** — semantics, keyboard, focus, target size, contrast, screen reader.
11. **Implementation** — files, dependencies, sequence, reuse, migrations.
12. **Validation** — tests, screenshots, devices, gates, remaining uncertainty.

Omit unchanged sections for narrow work.

## Decision ledger

Use one row for every decision that had multiple credible recommendations:

| Axis | Owner | Candidate evidence | Final decision | Why | Propagation |
|---|---|---|---|---|---|

Propagation states exactly where the choice appears: tokens, components, page sections, motion, tests, or docs.

## Conflict protocol

1. Identify whether the conflict is factual, constraint-based, or taste-based.
2. Apply the authority ladder from `SKILL.md`.
3. Return the issue to the assigned owner only.
4. Require a concrete revision, not another option list.
5. Update the blueprint and every downstream use.
6. Reopen a settled decision at most once unless new user evidence appears.

Examples:

- Generated blue clashes with brand tokens → brand tokens win; recalibrate the generated palette.
- Lead requests subtle gray text below contrast threshold → accessibility wins; preserve hierarchy using size or weight.
- Motion specialist requests springy buttons in a restrained enterprise tool → lead controls tone; motion specialist retunes mechanics.
- Font specialist proposes a display face without required language glyphs → platform/content requirement wins; choose a compatible candidate.
- Component specialist creates a new button primitive despite an existing library → incumbent component system wins; extend the existing primitive.

## Implementation handoff

Before coding, ensure the blueprint has:

- no competing palettes, type scales, or spacing systems;
- no undefined component states;
- no motion without reduced-motion behavior;
- no hardcoded values that should be tokens;
- no new dependency without a concrete need;
- no unresolved decision that changes architecture or visual direction.

Then implement in dependency order: tokens → primitives → composed components → surfaces → motion → validation.

## Final report

Keep the user-facing report proportional:

- outcome first;
- important design decisions;
- files/artifacts changed;
- validation evidence;
- genuine limitations.

Do not expose internal specialist transcripts unless requested.
