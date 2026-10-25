# Task 3: Przejrzeć przypięte snapshoty 49 zewnętrznych skillów, zainstalować dostępne bez wykonywania ich kodu oraz zapisać bezpieczeństwo, licencje i integralność.

Status: complete

## Requirements
- Resolve every supplied catalog entry to an exact upstream `SKILL.md` at a pinned commit.
- Review instruction bodies and included scripts without executing upstream code.
- Install reviewed copies in Codex and vendor matching copies in `skills/external/`.
- Record provenance, integrity evidence, unavailable candidates, safety limits and licence observations.

## Acceptance criteria
- 48 available snapshots have matching `SKILL.md` hashes in both installation locations.
- The routing catalog records full source commits and no longer routes to unavailable candidates.
- No external skill command, package installation, test, browser automation or deployment is run during the process.

## Affected repositories
- universal-agent-workspace-v3

## TDD evidence
- Red: not applicable (third-party snapshot installation; no upstream code is executed).
- Green: routing validation passed: 48 installed skills, 15 roles and 10 pinned source commits; 48/48 `SKILL.md` hashes match in both installation locations.
- Regression: `python -m unittest discover -s tests -v` — 12 tests passed.

## Decisions and risks
- `insecure-defaults` was unavailable in the reviewed source revision and deliberately not substituted.
- High-risk skills remain subject to task-specific authorization; installation grants no tool permissions.
- Quality gate `TASK-3`: passed (unit, integration and regression evidence recorded).
