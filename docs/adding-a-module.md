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
  "lead_capable": false,
  "description": "Discovers and validates type pairings.",
  "aliases": ["old-example-name"],
  "capabilities": ["typography", "accessibility"],
  "specialties": ["typography"],
  "keywords": ["font pairing", "type scale"],
  "requires": [],
  "source": {
    "package": "owner/repository",
    "skill": "example-skill",
    "url": "https://github.com/owner/repository",
    "path": "skills/example-skill",
    "ref": "main"
  }
}
```

- `id` is the stable orchestrator identity.
- `display_name` is human-facing.
- `tier` is `core` (offered by default setup) or `integration` (offered only
  when a task needs it). An integration must declare at least one specialty;
  it ranks only when a request triggers that specialty or names the module.
- `role` describes exclusive ownership. Core roles must be unique.
- `lead_capable` marks a module that can own visual direction. The router
  excludes idle lead-capable core modules to enforce the single-lead rule.
- `description` explains the module's contribution.
- `aliases` recognize older or host-specific names.
- `capabilities` are concerns the skill can cover; every value must exist in
  `config/capabilities.json`.
- `specialties` are the concerns it owns. They outrank broad capability
  matches and drive the router's fallback owner selection.
- `keywords` are lowercase phrases that add a bounded ranking bonus when a
  request uses them, such as `calm` for a restraint specialist.
- `requires` lists tool prerequisites declared in the manifest's top-level
  `prerequisites`, such as `figma-mcp` or `browser-automation`.
- `source.package` and `source.skill` must work with `npx skills add`.
- `source.url` must point to the original public repository.
- `source.path` and `source.ref` are optional. Set them when the skill lives
  in a subfolder; `setup.py` then installs from
  `https://github.com/<package>/tree/<ref>/<path>`, which avoids depending on
  how the Skills CLI walks a large repository.

## Procedure

1. Review the complete upstream `SKILL.md`, bundled scripts, license, and recent
   maintenance. Reject skills that fetch and follow remote instructions at
   runtime.
2. Verify discovery and the exact install source:

   ```bash
   npx skills add owner/repository --list
   npx skills add owner/repository --list --full-depth
   npx skills add https://github.com/owner/repository/tree/main/skills/example-skill --list
   ```

   Prefer the pinned tree URL (`source.path`) when the plain form needs
   `--full-depth` or lists several unrelated skills.

3. Add one manifest entry. Do not copy upstream files.
4. Add a concern to `config/capabilities.json` only when no existing one fits.
5. Route it: add the module to the `lead`, `support`, or `validation` lists of
   the relevant rules in `config/routing-rules.json`, or add a rule (see
   [Adding a routing rule](adding-a-routing-rule.md)).
6. Update the capability map, the workflow recipes it changes, the README
   module tables, and `NOTICE.md`. A test fails when a module is missing from
   any of them.
7. Add routing tests for at least one positive and one exclusion case.
8. Run:

   ```bash
   python3 skills/ui-ux-skill-orchestrator/scripts/validate.py
   python3 -m unittest discover -s tests -v
   python3 skills/ui-ux-skill-orchestrator/scripts/route.py --assume-installed --query "<realistic request>"
   ```

9. Use a fresh agent session to forward-test a realistic request.

## Replacing a module

Keep the old name in `aliases` when practical, change the source atomically,
and document any ownership change. Do not silently map a materially different
skill to an existing module identity.
