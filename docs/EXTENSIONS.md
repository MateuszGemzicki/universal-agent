# Implemented extensions (v2)

Commands below run locally and do not call an LLM. Run `python agent.py sync` and `python agent.py scan-all` first.

| Feature | Command / implementation | Limitation |
|---|---|---|
| Impact analysis | `python agent.py intelligence impact REPO PATH` | Python call-name heuristic, not a resolved cross-language call graph |
| Semantic-style search | `python agent.py intelligence search "keywords"` | Lexical ranked search; no embeddings/model required |
| Knowledge provenance | `python agent.py intelligence artifact ID REPO KIND FILE SOURCE...` | Explicit provenance, SHA fingerprints |
| Quality gates | `python agent.py intelligence check TASK REPO unit pass --evidence "..."` then `... gate TASK` | Recorded evidence must be verified by the operator; no automatic enforcement of external Codex execution |
| Task memory | `python agent.py intelligence lesson REPO PROBLEM SOLUTION EVIDENCE` | Local SQLite, no auto-verification |
| Test selection | `intelligence impact` + repository test commands | Suggested by dependencies, not automatic full test mapping |
| Context compiler | `python agent.py intelligence context "query" --budget 3000` | Approximate token budget |
| Stale documentation | `python agent.py intelligence stale` | Detects staleness; regeneration is agent-guided |
| Skill evaluator | `python agent.py intelligence skill-eval SKILL TASK pass` | Tracks results, does not assert causality |
| Benchmark harness | `python agent.py intelligence benchmark TASK PROVIDER 1 12.5 --tokens 1000` | External agents report metrics |
| Worktree isolation | `python agent.py intelligence worktree REPO agent/task /path/to/worktree --confirm` | Creates git branch/worktree; requires explicit confirmation |

`python agent.py intelligence benchmark-report` aggregates runs. `python agent.py intelligence lessons` lists stored lessons.

## Safety
The repository scanner skips common secret files but is **not** a comprehensive secret detector. Do not scan untrusted or sensitive repositories without reviewing access, and never treat generated documentation as authoritative. Script approval is still mandatory for `.cmd` scripts. Worktrees should be created outside the indexed repository directory. The workspace does not enforce provider token quotas.

## Recommended lifecycle
1. Scan and inspect status.
2. Search/context, assess impact, check stale knowledge.
3. Create task, define acceptance tests and worktree.
4. TDD: verify failing test, implement, verify passing test, run regressions.
5. Record evidence and evaluate gate.
6. Update docs, lessons, provenance, benchmark.
