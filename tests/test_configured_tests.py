import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from agent_system.cli import resolve_test_command


class ConfiguredTestCommandTests(unittest.TestCase):
    def setUp(self):
        self.config = {
            "repositories": [
                {"name": "configured", "test_command": ["python", "-m", "unittest"]},
                {"name": "empty", "test_command": []},
            ]
        }

    def test_uses_configured_command_when_no_override_is_supplied(self):
        self.assertEqual(
            ["python", "-m", "unittest"],
            resolve_test_command(self.config, "configured", []),
        )

    def test_explicit_command_overrides_configured_command(self):
        self.assertEqual(
            ["python", "-m", "pytest", "-q"],
            resolve_test_command(self.config, "configured", ["python", "-m", "pytest", "-q"]),
        )

    def test_rejects_repository_without_configured_or_explicit_command(self):
        with self.assertRaisesRegex(ValueError, "No test command"):
            resolve_test_command(self.config, "empty", [])


if __name__ == "__main__":
    unittest.main()
