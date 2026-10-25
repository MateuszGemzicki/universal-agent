# Provider-independent operating workflow

Start with `python agent.py doctor`, `sync`, `scan-all`, then `intelligence context "TASK" --budget 3000`.
Read only relevant files and request more context if necessary. Never claim an inferred business rule as fact.
Before editing, inspect impact and create an isolated branch/worktree for risky work; ask for approval before mutating git state.
Use red-green-refactor TDD. Record concrete commands and results in task file and `intelligence check`.
Quality gate is required before declaring completion; skipped tests are not passes.
Run `intelligence stale`, refresh affected documentation, store source-linked artifacts and lessons only when verified.
Never execute unapproved .cmd scripts. Never paste secrets into context or logs. Minimize output: result, evidence, blockers, next action.
