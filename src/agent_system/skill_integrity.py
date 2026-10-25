"""Verification helpers for reviewed, vendored Agent Skill snapshots."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml


LOCK_RELATIVE_PATH = Path("skills/skill-lock.json")
ROUTING_RELATIVE_PATH = Path("skills/skills-routing.yaml")


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def routed_skill_names(root: Path) -> set[str]:
    routing = yaml.safe_load((root / ROUTING_RELATIVE_PATH).read_text(encoding="utf-8"))
    skills = routing.get("skills", {})
    if not isinstance(skills, dict):
        raise ValueError("Routing skills must be a mapping")
    return set(skills)


def build_lock(root: Path) -> dict[str, object]:
    names = routed_skill_names(root)
    hashes: dict[str, str] = {}
    for name in sorted(names):
        skill_file = root / "skills" / "external" / name / "SKILL.md"
        if not skill_file.is_file():
            raise ValueError(f"Missing vendored skill: {skill_file}")
        hashes[name] = _hash(skill_file)
    return {"version": 1, "algorithm": "sha256", "skills": hashes}


def write_lock(root: Path) -> Path:
    lock_path = root / LOCK_RELATIVE_PATH
    lock_path.write_text(json.dumps(build_lock(root), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return lock_path


def verify(root: Path) -> dict[str, object]:
    expected = routed_skill_names(root)
    lock_path = root / LOCK_RELATIVE_PATH
    if not lock_path.is_file():
        return {"ok": False, "expected_count": len(expected), "errors": [f"Missing lock: {lock_path}"]}
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    locked = lock.get("skills", {})
    if lock.get("version") != 1 or lock.get("algorithm") != "sha256" or not isinstance(locked, dict):
        return {"ok": False, "expected_count": len(expected), "errors": ["Invalid skill lock format"]}
    errors: list[str] = []
    for name in sorted(expected - set(locked)):
        errors.append(f"Missing lock entry: {name}")
    for name in sorted(set(locked) - expected):
        errors.append(f"Stale lock entry: {name}")
    for name in sorted(expected & set(locked)):
        skill_file = root / "skills" / "external" / name / "SKILL.md"
        if not skill_file.is_file():
            errors.append(f"Missing vendored skill: {name}")
        elif _hash(skill_file) != locked[name]:
            errors.append(f"Hash mismatch: {name}")
    return {"ok": not errors, "expected_count": len(expected), "errors": errors}
