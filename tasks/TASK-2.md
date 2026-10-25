# Task 2: Zweryfikować bezpieczeństwo katalogu zewnętrznych Agent Skills i dodać do workspace bez automatycznej instalacji lub nadawania uprawnień.

Status: complete

## Requirements
- Parse both supplied files as untrusted input and identify installation, execution, privilege and supply-chain risks.
- Add a metadata-only routing catalog for all mapped roles and candidates.
- Do not install, download or activate external skill bodies.
- Record provenance, controls and residual risk.

## Acceptance criteria
- `skills/skills-routing.yaml` safely parses and contains all 49 supplied candidates and 15 roles.
- Every role-to-skill reference resolves; no source is marked ready to execute or imported as `SKILL.md`.
- The catalog documents pinning, hashing, licence review and explicit approval requirements.

## Affected repositories
- universal-agent-workspace-v3

## TDD evidence
- Red: not applicable (metadata and documentation change).
- Green: `safe_load` validation passed: 49 candidates, 15 roles, 10 sources; all references resolve and sources remain explicitly unpinned.
- Regression: `python -m unittest discover -s tests -v` — 12 tests passed.

## Decisions and risks
- External sources are intentionally unpinned and unreviewed. They remain catalog entries only until individually imported under the safe import protocol.
- Quality gate `TASK-2`: passed (unit, integration and regression evidence recorded).
