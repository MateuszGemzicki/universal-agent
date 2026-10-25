# Architecture

## Target system
User -> CEO orchestrator -> code analyst / business analyst / architect / TDD engineer / developer / QA browser agent.

## Knowledge graph
Nodes: repository, entrypoint, route, file, function, class, business rule, test, document, external service.
Edges: calls, imports, reads, writes, emits, handles, verifies, documents, depends_on.
Every derived edge must store evidence, confidence, source hashes and extractor version.

## Cache invalidation
Merkle-style SHA-256 hashes of directory entries; file hashes of bytes; future AST structural fingerprints and dependency fingerprints. Source hash + analyzer version + prompt version + model ID + relevant dependency fingerprints = cache key. Any changed dependency invalidates affected derived records. SHA is not a substitute for runtime verification.

## Storage
Git-tracked Markdown, prompts, skills and scripts; SQLite for initial state and audit trail; migrate to PostgreSQL when concurrency requires it. File content is not persisted in SQLite.

## Approvals
Generated CMD scripts must be reviewed and approved before each execution (unless the user explicitly creates a narrower repeat-approval policy). Store exact script SHA-256, arguments, requesting agent, expiry and result. Never run unapproved scripts. Secrets never enter prompts or logs.

## Browser
Use one controlled browser service; record routes as reproducible Playwright scripts. On first successful visit record stable locators and assertions; on subsequent runs replay until failure, then propose a repair. Browser execution requires an isolated profile and domain allowlist.

## TDD
Requirement -> failing test -> minimal implementation -> passing unit/integration/contract/E2E tests -> independent adversarial review -> documentation update -> commit. Record test evidence and limitations.
