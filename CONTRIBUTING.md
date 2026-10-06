# Contributing

Contributions that improve routing precision, portability, safety, or
validation are welcome.

## Before opening a change

1. Search existing issues and pull requests.
2. Keep the orchestrator neutral: specialists own design opinions; the
   orchestrator owns selection, boundaries, sequencing, and synthesis.
3. Do not vendor third-party skills or copy their instructions.
4. Add new specialists through the module manifest and new routing behavior
   through `config/routing-rules.json` unless routing mechanics genuinely need
   to change.
5. Keep scripts on the Python standard library and compatible with Python
   3.9.

## Local workflow

```bash
git clone https://github.com/Tesfamichael12/ui-ux-skill-orchestrator.git
cd ui-ux-skill-orchestrator
python3 skills/ui-ux-skill-orchestrator/scripts/validate.py
python3 -m unittest discover -s tests -v
npx skills add . --list
```

Create a focused branch and use descriptive commits. Pull requests should
explain the routing problem, the ownership rule being changed, and the
validation evidence.

## Adding or replacing a specialist

Follow [docs/adding-a-module.md](docs/adding-a-module.md). Include:

- the canonical public repository and installable skill name;
- aliases found in older or host-specific installations;
- narrow capabilities and specialties;
- a realistic prompt demonstrating why the module improves routing;
- a fallback for users who decline installation.

## Changing routing

Follow [docs/adding-a-routing-rule.md](docs/adding-a-routing-rule.md). Include
the requests the rule must catch, the near misses it must not catch, and
golden scenarios in `tests/test_route.py` for both.

## Pull request checklist

- [ ] `SKILL.md` remains concise and uses progressive disclosure.
- [ ] No specialist becomes a competing second lead.
- [ ] No installation occurs without explicit consent.
- [ ] All bundled scripts use the Python standard library unless justified.
- [ ] Validation and unit tests pass.
- [ ] Public documentation reflects user-visible changes.
- [ ] Third-party attribution and links are accurate.

By contributing, you agree that your contribution is licensed under the MIT
License.
