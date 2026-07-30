# Releasing

1. Ensure `main` is clean and current.
2. Run the validation suite:

   ```bash
   python3 skills/ui-ux-skill-orchestrator/scripts/validate.py
   python3 -m unittest discover -s tests -v
   npx skills add . --list
   ```

3. Test a local install into a temporary project and verify the installed file
   set.
4. Move relevant changelog entries from `Unreleased` into a semantic version.
5. Commit the release metadata.
6. Create an annotated tag:

   ```bash
   git tag -a vX.Y.Z -m "vX.Y.Z"
   ```

7. Push the branch and tag, then create a GitHub release from the changelog.
8. Verify public installation from `owner/repository` on a clean environment.

Never rewrite published release tags. Use a patch release for corrections.
