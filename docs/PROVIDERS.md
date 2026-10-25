# Provider-agnostic usage

This is a local workspace/tooling layer, **not** a universal plugin API or an override of provider system prompts. Model clients vary in their instruction-file discovery and workspace permission models.

- **Codex CLI**: open terminal here, run `codex`; `AGENTS.md` contains entry instructions.
- **Claude Code**: open terminal here, run `claude`; `CLAUDE.md` contains entry instructions.
- **Gemini CLI**: open terminal here, run `gemini`; `GEMINI.md` contains entry instructions.
- **GitHub Copilot**: `.github/copilot-instructions.md` may be picked up in supported repository contexts; confirm the active workspace is this folder and that custom instructions are enabled. If not, attach/paste `docs/SHARED_POLICY.md` as project instructions.
- **Other agents**: configure their project-instruction mechanism to load `docs/SHARED_POLICY.md`, and provide Python CLI access. Do not assume automatic discovery.

These CLIs are optional and may require separate installation/authentication. The Python indexing tools work without them. Repository access outside the working folder depends on the provider's sandbox and must be explicitly authorized.
