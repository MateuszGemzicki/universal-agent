import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agent_system.skill_integrity import verify


class SkillSnapshotTests(unittest.TestCase):
    def test_every_routed_skill_has_an_exact_locked_snapshot(self):
        result = verify(ROOT)
        self.assertEqual(68, result["expected_count"])
        self.assertTrue(result["ok"], result["errors"])
        self.assertEqual([], result["errors"])


if __name__ == "__main__":
    unittest.main()
