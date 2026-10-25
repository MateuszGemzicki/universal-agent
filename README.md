# Universal Multi-Repo AI Workspace

**Unpack → configure `config.yaml` → run Codex, Claude Code, Gemini CLI or another agent from this directory.** Python 3.11+, Git and Node.js assumed. Optional agent CLIs require their own installation/authentication.

```powershell
python agent.py doctor
python agent.py sync
python agent.py scan-all
python agent.py docs
codex   # or: claude / gemini
```

The `config.yaml` file is JSON-compatible YAML 1.2 (no extra parser needed). Set `enabled: true` (JSON syntax: `"enabled": true`) and correct paths for your repositories. Instructions for Codex are in `AGENTS.md`, Claude Code in `CLAUDE.md`, Gemini CLI in `GEMINI.md`, GitHub Copilot in `.github/copilot-instructions.md`, with shared rules in `docs/SHARED_POLICY.md`.

## Capabilities and limitations

Local deterministic features: repository scanning, SHA-256 incremental indexing, basic Python/JS/TS inventory, SQLite state, generated graph and docs, task notes, script approvals, test-run recording, optional local browser smoke test. The AI client performs actual semantic interpretation and coding; this package does **not** independently run a multi-agent service or guarantee a full semantic call graph, business docs or token budget enforcement. The `ai_budget` configuration is advisory, not a provider-side billing limit.

See `docs/PROVIDERS.md`, `docs/ARCHITECTURE.md`, `docs/OPERATING_RULES.md` and `docs/SHARED_POLICY.md`. Explicit authorization is required before edits outside this workspace or execution of untrusted code. `python agent.py approve` is intended for the human only.

## Quick verification

```powershell
python -m pip install -e .
python -m unittest discover -s tests -v
```

## Version 2 extensions
See `docs/EXTENSIONS.md` for 11 local workflows and their limits, and `docs/NEXT_10_IDEAS.md` for ten further proposals. New commands: `python agent.py intelligence --help`.

## v3: Advanced code intelligence and verification

The following commands are available from the workspace root (run `python agent.py sync` first):

```sh
# 1. Tree-sitter symbols (optional package; Python AST fallback)
python -m pip install tree-sitter-language-pack
python agent.py advanced parse example-app src/main.py

# 2. LSP definition / references (install language server separately)
python agent.py advanced lsp example-app src/main.py 12 5 --server python --operation references

# 3. Test coverage mapping (coverage.py JSON or Istanbul JSON)
python agent.py advanced coverage coverage.json src/main.py

# 4. OpenAPI 3 JSON contract compatibility checks
python agent.py advanced contracts old-openapi.json new-openapi.json

# 5. Secrets and email PII redaction (best effort)
python agent.py advanced redact input.txt --output redacted.txt

# 7. Single Python mutation smoke test in isolated temporary copy
python agent.py advanced mutate example-app src/main.py --confirm -- python -m pytest -q
```

**Limits:** Tree-sitter is syntax parsing, not type resolution; LSP requires a separately installed language server and may depend on project setup. Coverage maps only previously generated coverage reports. OpenAPI diff checks a subset of breaking changes (JSON OpenAPI 3, no `$ref` resolution). Redaction is not a substitute for DLP or secret isolation. Mutation testing is one deterministic mutant per invocation, not a full mutation-testing platform. No arbitrary external code execution is performed by scanning or parsing; test execution requires explicit `--confirm`.

The YAML config uses JSON syntax (valid YAML 1.2). `lsp_servers` maps server names to argv arrays; only configure trusted executables.
