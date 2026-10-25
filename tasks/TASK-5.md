# Task 5: Wzmocnić approval dla skryptów, usunąć pozorną konfigurację, dodać CI i integralność wszystkich vendored skills.

Status: complete

## Requirements
- Make approvals expire, bind exact arguments, consume after one run, and record execution evidence.
- Use `repositories[].test_command` as the safe default for `agent.py test REPO`; remove unused write-policy configuration.
- Add a committed lock and verifier for every routed vendored `SKILL.md`.
- Add GitHub Actions CI for unit tests and skill verification.

## Acceptance criteria
- Approval lifecycle is covered by tests for expiry, argv binding, one-time use, and execution recording.
- Configured test commands work without explicit argv; explicit argv remains an override.
- Every routed skill has an exact hash in the committed lock and the verifier reports a clean result.
- CI runs the same local unit and snapshot checks.

## Affected repositories
- universal-agent-workspace-v3

## TDD evidence
- Red: focused approval, configured-test, and skill-snapshot tests failed before their implementation existed.
- Green: approval lifecycle, configured command lookup, and 68-skill hash verification pass.
- Regression: `python -m unittest discover -s tests -v` — 23/23 passed.

## Decisions and risks
- No external repository tests or vendored scripts will be executed.
- Existing SQLite approval records must migrate additively and fail closed if incomplete.
- Quality gate passed for unit, integration, and regression evidence.
