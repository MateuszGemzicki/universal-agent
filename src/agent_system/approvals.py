"""One-use, time-bounded approvals for local CMD scripts."""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime, timedelta


DEFAULT_TTL_SECONDS = 900
MAX_TTL_SECONDS = 86_400


def _timestamp(now: datetime | None = None) -> str:
    return (now or datetime.now(UTC)).astimezone(UTC).isoformat()


def _columns(db: sqlite3.Connection, table: str) -> set[str]:
    return {row[1] for row in db.execute(f"PRAGMA table_info({table})")}


def init(db: sqlite3.Connection) -> None:
    """Create the current schema and migrate legacy approval records safely."""
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS approvals_v2(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kind TEXT NOT NULL,
            path TEXT NOT NULL,
            sha256 TEXT NOT NULL,
            purpose TEXT NOT NULL,
            state TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL,
            argv_json TEXT NOT NULL DEFAULT '[]',
            expires_at TEXT,
            approved_at TEXT,
            consumed_at TEXT
        )
        """
    )
    migrations = {
        "argv_json": "TEXT NOT NULL DEFAULT '[]'",
        "expires_at": "TEXT",
        "approved_at": "TEXT",
        "consumed_at": "TEXT",
    }
    existing = _columns(db, "approvals_v2")
    for name, definition in migrations.items():
        if name not in existing:
            db.execute(f"ALTER TABLE approvals_v2 ADD COLUMN {name} {definition}")
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS script_runs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            approval_id INTEGER NOT NULL UNIQUE,
            argv_json TEXT NOT NULL,
            exit_code INTEGER NOT NULL,
            result TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(approval_id) REFERENCES approvals_v2(id)
        )
        """
    )
    # Legacy records were not bound to args or an expiry; they must not become
    # runnable under the stricter lifecycle.
    db.execute(
        "UPDATE approvals_v2 SET state='expired' "
        "WHERE state IN ('pending', 'approved') AND expires_at IS NULL"
    )
    db.commit()


def _row(db: sqlite3.Connection, approval_id: int) -> dict[str, object]:
    row = db.execute(
        "SELECT id, path, sha256, purpose, state, argv_json, expires_at, approved_at, consumed_at "
        "FROM approvals_v2 WHERE id=?",
        (approval_id,),
    ).fetchone()
    if not row:
        raise ValueError("Approval request not found")
    keys = ("id", "path", "sha256", "purpose", "state", "argv_json", "expires_at", "approved_at", "consumed_at")
    return dict(zip(keys, row))


def _expired(record: dict[str, object], now: datetime) -> bool:
    expires_at = record["expires_at"]
    return not isinstance(expires_at, str) or now >= datetime.fromisoformat(expires_at)


def _require_argv(argv: list[str]) -> None:
    if not all(isinstance(argument, str) for argument in argv):
        raise ValueError("Script arguments must be strings")


def propose(
    db: sqlite3.Connection,
    *,
    path: str,
    sha256: str,
    purpose: str,
    argv: list[str],
    ttl_seconds: int = DEFAULT_TTL_SECONDS,
    now: datetime | None = None,
) -> dict[str, object]:
    if not 1 <= ttl_seconds <= MAX_TTL_SECONDS:
        raise ValueError(f"Approval TTL must be between 1 and {MAX_TTL_SECONDS} seconds")
    _require_argv(argv)
    created = now or datetime.now(UTC)
    expires = created + timedelta(seconds=ttl_seconds)
    with db:
        cursor = db.execute(
            "INSERT INTO approvals_v2(kind,path,sha256,purpose,state,created_at,argv_json,expires_at) "
            "VALUES(?,?,?,?,?,?,?,?)",
            ("cmd", path, sha256, purpose, "pending", _timestamp(created), json.dumps(argv), _timestamp(expires)),
        )
    return {"id": cursor.lastrowid, "expires_at": _timestamp(expires), "argv": argv}


def approve(db: sqlite3.Connection, approval_id: int, *, now: datetime | None = None) -> dict[str, object]:
    current = now or datetime.now(UTC)
    record = _row(db, approval_id)
    if record["state"] != "pending":
        raise ValueError(f"Approval request is not pending: {record['state']}")
    if _expired(record, current):
        with db:
            db.execute("UPDATE approvals_v2 SET state='expired' WHERE id=?", (approval_id,))
        raise ValueError("Approval request expired")
    with db:
        db.execute(
            "UPDATE approvals_v2 SET state='approved', approved_at=? WHERE id=? AND state='pending'",
            (_timestamp(current), approval_id),
        )
    return _row(db, approval_id)


def claim_for_execution(
    db: sqlite3.Connection, approval_id: int, *, now: datetime | None = None
) -> dict[str, object]:
    current = now or datetime.now(UTC)
    record = _row(db, approval_id)
    if record["state"] == "consumed":
        raise ValueError("Approval request already consumed")
    if record["state"] != "approved":
        raise ValueError(f"Approval request is not approved: {record['state']}")
    if _expired(record, current):
        with db:
            db.execute("UPDATE approvals_v2 SET state='expired' WHERE id=?", (approval_id,))
        raise ValueError("Approval request expired")
    with db:
        changed = db.execute(
            "UPDATE approvals_v2 SET state='consumed', consumed_at=? "
            "WHERE id=? AND state='approved'",
            (_timestamp(current), approval_id),
        ).rowcount
    if changed != 1:
        raise ValueError("Approval request could not be consumed")
    return {
        "id": record["id"],
        "path": record["path"],
        "sha256": record["sha256"],
        "argv": json.loads(str(record["argv_json"])),
    }


def record_execution(
    db: sqlite3.Connection,
    *,
    approval_id: int,
    argv: list[str],
    exit_code: int,
    output: str,
    now: datetime | None = None,
) -> dict[str, object]:
    record = _row(db, approval_id)
    if record["state"] != "consumed":
        raise ValueError("Only a consumed approval can record an execution")
    approved_argv = json.loads(str(record["argv_json"]))
    if argv != approved_argv:
        raise ValueError("Execution arguments do not match approval")
    with db:
        cursor = db.execute(
            "INSERT INTO script_runs(approval_id,argv_json,exit_code,result,created_at) VALUES(?,?,?,?,?)",
            (approval_id, json.dumps(argv), exit_code, output, _timestamp(now)),
        )
    return {"id": cursor.lastrowid, "approval_id": approval_id, "argv": argv, "exit_code": exit_code, "result": output}
