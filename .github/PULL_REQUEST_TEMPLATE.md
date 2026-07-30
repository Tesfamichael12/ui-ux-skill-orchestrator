## Summary

Describe the routing or packaging problem and the chosen change.

## Ownership impact

State which lead, specialist, concern, or fallback behavior changes.

## Validation

- [ ] `python3 skills/ui-ux-skill-orchestrator/scripts/validate.py`
- [ ] `python3 -m unittest discover -s tests -v`
- [ ] `npx skills add . --list`
- [ ] Forward-tested when routing behavior changed

## Safety

- [ ] No third-party skill content is vendored.
- [ ] No dependency installs without explicit consent.
- [ ] Sources and aliases are accurate.
