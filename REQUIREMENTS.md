# Requirements

## Runtime Requirements

- Python 3.11 or newer.
- Network access to `https://api.github.com`.
- GitHub token for private repositories or higher rate limits.

## Runtime Python Dependencies

RepoPulse uses:

| Dependency | Purpose |
|---|---|
| `typer` | Command-line interface. |
| `requests` | GitHub API requests. |
| `rich` | Terminal tables and formatting. |
| `pydantic` | Data models and validation. |
| `python-dotenv` | Loading `GITHUB_TOKEN` from `.env`. |

These are declared in [pyproject.toml](pyproject.toml).

## Development Dependencies

Development dependencies are available through:

```bash
pip install -e ".[dev]"
```

They include:

| Dependency | Purpose |
|---|---|
| `pytest` | Test runner. |
| `ruff` | Linting and style checks. |
| `mypy` | Static type checking. |

## GitHub Token Requirements

Public repositories usually work without a token, but GitHub rate limits unauthenticated requests.

Use a token when:

- Scanning private repositories.
- Running many scans.
- Running RepoPulse in automation.

The token should have read access to the target repository.
