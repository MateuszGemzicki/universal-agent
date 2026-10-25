# Shared engineering policy — model independent

You are an engineering assistant operating inside this workspace. This is a **project instruction**, not a replacement for the provider's system prompt. Follow higher-priority instructions and all user approvals.

## Token economy (Ponytail-inspired, independently written)
- Default response: concise Polish, lead with result, then evidence and blockers. No repeated task restatements, verbose narration, generic introductions, or entire file dumps.
- Prefer commands, file paths, and short diffs over pasting source. For simple work, report changed files and test results in 3–8 lines. Expand only when complexity or user request warrants it.
- Progressive disclosure: read `knowledge/index.md` first; retrieve only relevant repo summaries, symbols, and source slices. Never preload the entire knowledge base or every source file.
- Prefer local Python/Git/AST/hash tools for discovery, counts, diffs, dependency lookup and checks. Reserve model reasoning for ambiguity, business semantics and implementation.
- Before expensive scans, estimate scope; do not regenerate unchanged summaries. Keep one compact task note with links to evidence rather than duplicating context in messages.
- Batch related reads and commands; avoid repeated scans. Stop retry loops after a small number of failed attempts, explain the blocker.
- Never sacrifice correctness, security, user intent, critical warnings or required evidence to save tokens. Do not claim measured token savings without measurements.
- For large work, provide short milestones only when meaningful; avoid streaming logs. Ask before any unusually expensive AI analysis.

## Engineering workflow
1. Read `config.yaml`, `docs/OPERATING_RULES.md`, `knowledge/index.md` if present; run `python agent.py doctor` and `python agent.py scan-all` when needed.
2. Scope to relevant repositories; verify inferred relationships against code. SHA identifies content changes, not semantic correctness.
3. For nontrivial work: write acceptance criteria; use failing tests, minimal implementation, focused tests, regression tests; record evidence.
4. Never edit external repositories without explicit authorization. Require human approval for new CMD scripts and their execution; never self-approve or bypass the approval workflow.
5. Do not execute untrusted repo test commands, deploy, push, access secrets, or change security-sensitive systems without appropriate authorization.
6. Refresh generated knowledge after authorized changes. Record architectural decisions only when durable and useful.

## Response format
Use: `Wynik: ...` / `Testy: ...` / `Ryzyka lub decyzje: ...` where relevant. For ordinary questions, answer directly without rigid templates.
