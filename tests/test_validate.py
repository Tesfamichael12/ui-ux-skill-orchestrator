from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]
VALIDATOR = (
    REPOSITORY
    / "skills"
    / "ui-ux-skill-orchestrator"
    / "scripts"
    / "validate.py"
)


class ValidationTests(unittest.TestCase):
    def test_repository_skill_is_valid(self) -> None:
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), "--json"],
            cwd=REPOSITORY,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('"valid": true', result.stdout)


if __name__ == "__main__":
    unittest.main()
