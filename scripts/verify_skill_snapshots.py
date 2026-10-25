"""Verify, or deliberately refresh, hashes for vendored Agent Skill snapshots."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agent_system.skill_integrity import verify, write_lock


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-reviewed-lock",
        action="store_true",
        help="write hashes after a human has reviewed the updated snapshots",
    )
    args = parser.parse_args()
    if args.write_reviewed_lock:
        lock = write_lock(ROOT)
        print(json.dumps({"written": str(lock)}, indent=2))
        return 0
    result = verify(ROOT)
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
