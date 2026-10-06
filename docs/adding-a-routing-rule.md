# Adding a routing rule

Routing lives in
`skills/ui-ux-skill-orchestrator/config/routing-rules.json`. Change the data,
not `route.py`, whenever a new situation needs a different team.

## How a rule is chosen

`route.py` profiles the request into:

- **concerns** from `config/capabilities.json` (for example `motion`,
  `typography`, `data-viz`);
- **tasks** from the `tasks` vocabulary: `create`, `redesign`, `refine`,
  `audit`, `debug`, `translate` (default `create`);
- **scope** from the `scopes` vocabulary: `system`, `component` (only for
  narrow tasks), then the narrowest of `page`, `surface`, `component`
  (default `page`).

Rules are checked from the highest `priority` down. The first rule whose
`when` conditions all hold wins. The rule with an empty `when` is the
fallback and must have the lowest priority.

## Rule fields

```json
{
  "id": "motion-focus",
  "description": "Motion is the only open design axis.",
  "priority": 80,
  "when": {
    "capabilities_any": ["motion"],
    "needs_within": ["motion", "accessibility", "performance", "components"]
  },
  "lead": ["ui-animation"],
  "support": [{ "module": "fixing-accessibility", "for": ["accessibility"] }],
  "validation": ["ui-verification", "impeccable"],
  "exclude": [],
  "recipe": "Motion task"
}
```

| Field        | Meaning                                                                                                                        |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| `when`       | Conditions; all must hold                                                                                                      |
| `lead`       | Ordered preferences. The first installed one leads. `"incumbent"` means the existing design system or supplied reference leads |
| `support`    | Specialists, each added only for the listed concerns the request actually raises and nobody already owns                       |
| `validation` | Ordered preferences for the single validation owner                                                                            |
| `exclude`    | Installed modules to keep out, with the reason shown in the brief                                                              |
| `recipe`     | A `## ` heading in `references/workflow-recipes.md`, or `null`                                                                 |

`lead` and `validation` entries may be objects with their own condition:

```json
{ "module": "mies", "when": { "terms_any": ["calm", "minimal"] } }
```

## Conditions

| Key                        | Holds when                                                       |
| -------------------------- | ---------------------------------------------------------------- |
| `capabilities_any`         | At least one listed concern is present                           |
| `capabilities_all`         | Every listed concern is present                                  |
| `capabilities_none`        | No listed concern is present                                     |
| `needs_within`             | Every detected concern is in the list (use it for focused rules) |
| `tasks_any` / `tasks_none` | A listed task is / is not detected                               |
| `scopes_any`               | The scope is one of the listed scopes                            |
| `terms_any` / `terms_none` | A listed phrase is / is not in the request                       |

## Budgets

Each scope sets `max_specialists`. `page` also sets
`extended_max_specialists`, used only when a validation owner exists, motion
is requested, and an evidence concern (`color`, `data-viz`, `typography`, or
`ux`) is open. `component` sets `assign_validation: false`, so a single
component gets a reviewer only when the user asks for an audit.

## Procedure

1. Write the request examples the rule must catch and the near misses it must
   not catch.
2. Pick a priority between the rules it should beat and the rules that should
   beat it. Tool-bound and narrow rules sit above broad ones.
3. Prefer `needs_within` for focused rules so a request with extra concerns
   falls through to a broader rule.
4. Add a recipe heading when no existing recipe describes the workflow.
5. Add golden scenarios to `tests/test_route.py` for the positive case and a
   near miss.
6. Run:

   ```bash
   python3 skills/ui-ux-skill-orchestrator/scripts/validate.py
   python3 -m unittest discover -s tests -v
   python3 skills/ui-ux-skill-orchestrator/scripts/route.py --assume-installed --query "<example request>"
   ```

The validator rejects unknown modules, capabilities, tasks, scopes, condition
keys, and recipe headings, duplicate rule ids, and a missing or misplaced
fallback rule.
