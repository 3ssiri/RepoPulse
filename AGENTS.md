# AGENTS.md

## Shared Developer Memory (optional)

- If a shared memory service is configured for this project, its identifiers live in the untracked local file `AGENTS.local.md` (see `.gitignore`). Do not put real service IDs in tracked files.
- Store only architecture decisions, recurring fixes, project conventions, and developer preferences.
- Do not store secrets, API keys, tokens, passwords, PII, or raw private app-user content.
- Do not verify memory-service credentials by reading MCP config/auth fields; use MCP tools directly.
