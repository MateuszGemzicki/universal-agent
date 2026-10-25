# Execution policy
- Configuration uses **JSON syntax in a `.yaml` file** (valid YAML 1.2 subset), so Python standard library can parse it without installing dependencies. Use forward slashes in Windows paths.
- Scanning and documentation write only inside this orchestration folder.
- Source repositories are read-only by default; changes require explicit authorization in the chat.
- Scripts require human approval bound to the exact SHA-256. The user, not the agent, executes `approve`.
- External repo test commands and browser tests may execute code. Obtain permission before running them.
- Generated business documentation is **inferred**, not guaranteed accurate; label assumptions and cite source paths.
- Sensitive files (.env, keys, credentials) are excluded from inventory; no secrets in notes or logs.
- Git state and external service/API dependencies can invalidate semantic analyses even if source hashes match; revalidate where appropriate.
