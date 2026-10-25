# Workspace Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make script approvals one-use and time-bounded, make configuration effective, and continuously verify the repository and its skill snapshots.

**Architecture:** Approval state and execution evidence live in SQLite; the CLI accepts only proposal-bound arguments and consumes an approval before launching a script. Configuration supplies the default test command. A committed JSON lock records hashes for every vendored skill and is checked locally and in GitHub Actions.

**Tech Stack:** Python 3.11+, SQLite, unittest, GitHub Actions, JSON.

**Spec:** `tasks/TASK-5.md`

## Global Constraints

- Do not execute untrusted or vendored skill scripts.
- CMD execution stays Windows-only and requires a human approval record.
- Retain compatibility with existing SQLite state through an additive migration.
- Vendored snapshots remain byte-stable; update hashes only after review.
- CI must operate without the external repositories configured on a developer machine.

## Review Focus

- An expired approval must fail closed before a subprocess starts.
- A consumed approval must not be reusable, including after a failed process.
- A caller must not replace proposal-bound arguments at execution time.
- A missing configured test command must not result in an accidental empty execution.
- A modified or missing vendored `SKILL.md` must fail the local verifier and CI.

---

### Task 1: Bounded script approvals

**Files:**
- Create: `src/agent_system/approvals.py`
- Modify: `src/agent_system/cli.py`
- Modify: `tests/test_approvals.py`
- Modify: `docs/ARCHITECTURE.md`
- Modify: `docs/OPERATING_RULES.md`

**Interfaces:**
- Produces: approval records with `argv_json`, `expires_at`, `approved_at`, `consumed_at`, and an execution record.
- Consumes: the existing `scripts/*.cmd` path validation and the SQLite connection.

- [x] **Step 1: Write failing tests for expiry, one-time consumption, and proposal-bound argv.**
- [x] **Step 2: Run `python -m unittest discover -s tests -p test_approvals.py -v` and confirm failure because the approval API is absent.**
- [x] **Step 3: Implement additive schema migration and approval lifecycle helpers in `approvals.py`; wire `propose-script`, `approve`, and `run-script` to them.**
- [x] **Step 4: Run the focused approval tests and confirm pass.**
- [x] **Step 5: Document the one-use, expiry, and argument-binding behavior.**

### Task 2: Effective test configuration

**Files:**
- Modify: `config.yaml`
- Modify: `src/agent_system/cli.py`
- Modify: `tests/test_configured_tests.py`
- Modify: `README.md`

**Interfaces:**
- Produces: `agent.py test REPO` resolves a configured command; explicit argv remains an override.
- Consumes: `repositories[].test_command` from `config.yaml`.

- [x] **Step 1: Write failing tests for configured-command lookup, empty commands, and explicit override precedence.**
- [x] **Step 2: Run `python -m unittest discover -s tests -p test_configured_tests.py -v` and confirm failure because lookup is absent.**
- [x] **Step 3: Implement lookup and remove the unused `allow_external_writes` setting.**
- [x] **Step 4: Run the focused configuration tests and confirm pass.**
- [x] **Step 5: Document the default and override CLI forms.**

### Task 3: Locked skill integrity verification

**Files:**
- Create: `scripts/verify_skill_snapshots.py`
- Create: `skills/skill-lock.json`
- Create: `tests/test_skill_snapshots.py`
- Modify: `skills/README.md`

**Interfaces:**
- Produces: `python scripts/verify_skill_snapshots.py` returning non-zero for a missing or changed vendored `SKILL.md`.
- Consumes: `skills/skills-routing.yaml`, `skills/external/*/SKILL.md`, and the committed JSON lock.

- [x] **Step 1: Write a failing test requiring every routed skill to have an exact locked hash.**
- [x] **Step 2: Run `python -m unittest discover -s tests -p test_skill_snapshots.py -v` and confirm failure because the lock/verifier is absent.**
- [x] **Step 3: Implement the verifier, generate the reviewed lock from the current vendor tree, and document reviewed updates.**
- [x] **Step 4: Run the focused snapshot test and verifier; confirm 68/68 hashes match.**

### Task 4: Continuous integration and final evidence

**Files:**
- Create: `.github/workflows/ci.yml`
- Modify: `tasks/TASK-5.md`

**Interfaces:**
- Produces: a pull-request/push workflow that installs test dependencies, runs unit tests, and verifies skill snapshots.
- Consumes: the new snapshot verifier and existing unittest suite.

- [x] **Step 1: Add a workflow that checks out the repository, installs Python and PyYAML, installs the package, runs tests, and invokes the snapshot verifier.**
- [x] **Step 2: Validate workflow YAML structure and run the equivalent local commands.**
- [x] **Step 3: Record unit, integration, and regression evidence with `agent.py intelligence check`, then run the quality gate.**
- [x] **Step 4: Commit and push the hardened implementation.**
