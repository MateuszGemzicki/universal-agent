# Task 4: Zweryfikować, przypiąć i zintegrować 20 nowych Agent Skills z routingiem ról oraz zasadami premium frontend bez przebudowy systemu.

Status: complete

## Requirements
- Verify the supplied 20 skills against current upstream paths and commit snapshots.
- Install each available skill for Codex, Claude Code and the audited workspace mirror without running upstream scripts.
- Extend role routing, role-prompt pointers and premium frontend selection without changing existing role definitions.
- Add integration documentation and executable routing validation.

## Acceptance criteria
- All 20 supplied skills map to real `SKILL.md` files and pinned source commits.
- All 20 are installed in Codex, `.claude/skills` and `skills/external`.
- Routing resolves every role reference, limits active selection to three, and records premium frontend validation evidence.
- Workspace tests and the routing integration test pass.

## Affected repositories
- universal-agent-workspace-v3

## TDD evidence
- Red: not applicable (configuration and vendored skill integration; upstream code is not executed).
- Green: 20/20 pinned `SKILL.md` Git-blob hashes match in Codex, `.claude/skills` and `skills/external`; routing integration assertions pass.
- Regression: `python -m unittest discover -s tests -v` — 16/16 passed.

## Decisions and risks
- Two OpenAI plugin skill directories lack a plugin-local licence file; they are documented for local use and need licence confirmation before redistribution.
- High-risk skill commands remain subject to existing approval and tool-permission rules.
- Workspace quality gate passed for unit, integration and regression evidence.
