# Adding a module

Add or replace specialists through
`skills/ui-ux-skill-orchestrator/config/skill-modules.json`.

## Selection criteria

A module should contribute at least one of:

- narrower expertise than the current lead;
- deterministic local data or tooling;
- a tool-bound workflow;
- validation that the current portfolio cannot perform reliably.

Do not add a module solely because it is popular or repeats broad design
advice.

## Manifest fields

```json
{
  "id": "example-skill",
  "display_name": "Example Skill",
  "tier": "core",
  "role": "typography-evidence",
  "description": "Discovers and validates type pairings.",
  "aliases": ["old-example-name"],
  "capabilities": ["typography", "accessibility"],
  "specialties": ["typography"],
  "source": {
    "package": "owner/repository",
    "skill": "example-skill",
    "url": "https://github.com/owner/repository"
  }
}
```

- `id` is the stable orchestrator identity.
- `display_name` is human-facing.
- `tier` is `core` or `integration`.
- `role` describes exclusive ownership.
- `description` explains the module's contribution.
- `aliases` recognize older or host-specific names.
- `capabilities` are concerns the skill can cover.
- `specialties` receive extra ranking weight.
- `source.package` and `source.skill` must work with `npx skills add`.
- `source.url` must point to the original public repository.

## Procedure

1. Review the complete upstream `SKILL.md`, bundled scripts, license, and recent
   maintenance.
2. Verify discovery:

   ```bash
   npx skills add owner/repository --skill example-skill --list
   ```

3. Add one manifest entry. Do not copy upstream files.
4. Update the capability map only when ownership rules change.
5. Add routing tests for at least one positive and one exclusion case.
6. Run:

   ```bash
   python3 skills/ui-ux-skill-orchestrator/scripts/validate.py
   python3 -m unittest discover -s tests -v
   ```

7. Use a fresh agent session to forward-test a realistic request.

## Replacing a module

Keep the old name in `aliases` when practical, change the source atomically,
and document any ownership change. Do not silently map a materially different
skill to an existing module identity.
