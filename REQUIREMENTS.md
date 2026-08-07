# Requirements

## Runtime Requirements

- Python 3.11 or newer.
- Network access to `https://api.github.com` for remote scans, compare against GitHub URLs, and `create-issues --yes`.
- Network access to PyPI (or a GitHub Release URL) to install the package.
- GitHub token for private repositories, higher rate limits, or creating issues.

**Install package name:** `repopulse-cli` (CLI: `repopulse`). See [INSTALLATION.md](INSTALLATION.md).

## Runtime Python Dependencies

RepoPulse uses:

| Dependency | Purpose |
|---|---|
| `typer` | Command-line interface. |
| `requests` | GitHub API requests. |
| `rich` | Terminal tables and formatting. |
| `pydantic` | Data models and validation. |

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

Token scopes (minimum practical):

| Use case | Access needed |
|---|---|
| Public remote scan | Optional (helps with rate limits) |
| Private remote scan | Read access to that repository |
| `create-issues --yes` | Permission to create issues on the target repository |

Never commit tokens. Prefer env vars / CI secrets. See [USAGE.md](USAGE.md#token-hygiene-important).

`.env` files are **not** loaded automatically: RepoPulse scans repositories that may be untrusted, so it never imports environment files from disk. Pass `--token` or export `GITHUB_TOKEN` in your shell/CI environment.
