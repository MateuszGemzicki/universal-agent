import sqlite3
import sys
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from agent_system import approvals


class ApprovalTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        approvals.init(self.db)
        self.now = datetime(2026, 10, 25, tzinfo=UTC)

    def tearDown(self):
        self.db.close()

    def propose(self, *, ttl_seconds=60, argv=("safe",)):
        return approvals.propose(
            self.db,
            path="C:/workspace/scripts/example.cmd",
            sha256="a" * 64,
            purpose="test approval",
            argv=list(argv),
            ttl_seconds=ttl_seconds,
            now=self.now,
        )

    def test_expired_approval_fails_closed(self):
        request = self.propose(ttl_seconds=1)
        with self.assertRaisesRegex(ValueError, "expired"):
            approvals.approve(self.db, request["id"], now=self.now + timedelta(seconds=1))

    def test_approved_request_can_be_claimed_only_once(self):
        request = self.propose()
        approvals.approve(self.db, request["id"], now=self.now)
        claimed = approvals.claim_for_execution(self.db, request["id"], now=self.now)
        self.assertEqual(["safe"], claimed["argv"])
        with self.assertRaisesRegex(ValueError, "already consumed"):
            approvals.claim_for_execution(self.db, request["id"], now=self.now)

    def test_proposal_binds_exact_arguments_and_records_result(self):
        request = self.propose(argv=("--mode", "safe"))
        approvals.approve(self.db, request["id"], now=self.now)
        claimed = approvals.claim_for_execution(self.db, request["id"], now=self.now)
        run = approvals.record_execution(
            self.db,
            approval_id=request["id"],
            argv=claimed["argv"],
            exit_code=0,
            output="ok",
            now=self.now,
        )
        self.assertEqual(["--mode", "safe"], run["argv"])
        self.assertEqual(0, run["exit_code"])


if __name__ == "__main__":
    unittest.main()
