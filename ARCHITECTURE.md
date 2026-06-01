# Architecture

RepoPulse is intentionally small and modular. The CLI gathers input, the GitHub client fetches repository data, independent checks evaluate the repository, and the reporting layer renders the result.

## Data Flow

```text
User Input
  |
  v
CLI Layer
  |
  v
GitHub URL Parser
  |
  v
GitHub Client
  |
  v
Repository Metadata + File Tree
  |
  v
Checks Engine
  |
  v
Scoring Engine
  |
  v
Terminal / Markdown / JSON Output
```

## Main Modules

| Module | Responsibility |
|---|---|
| `repopulse/cli.py` | Typer command definitions and user-facing options. |
| `repopulse/url_parser.py` | GitHub repository URL parsing and validation. |
| `repopulse/github_client.py` | GitHub API requests and API error handling. |
| `repopulse/analyzer.py` | Builds a full `HealthReport` from API data and checks. |
| `repopulse/models.py` | Pydantic models for repository info, files, checks, and reports. |
| `repopulse/scoring.py` | Total score and grade calculation. |
| `repopulse/report.py` | Terminal, Markdown, JSON, and summary rendering. |
| `repopulse/checks/` | Independent repository health checks. |

## Check Design

Each check should:

- Live in its own file under `repopulse/checks/`.
- Return a `CheckResult`.
- Avoid network calls.
- Avoid printing secrets or file contents from sensitive files.
- Add recommendations that a maintainer can act on.

Core checks contribute to the 100-point score. Advisory checks can use `max_score=0` when they should provide guidance without changing the main score.

## Error Handling

GitHub API and network failures are wrapped in `GitHubAPIError` so the CLI can show concise user-facing messages instead of raw tracebacks.

## Testing Strategy

Tests cover:

- URL parsing.
- Scoring.
- Individual checks.
- Report rendering.
- CLI behavior.
- GitHub client error wrapping.

Run tests with:

```bash
pytest
```
