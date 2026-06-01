# RepoPulse

RepoPulse is a Python CLI tool that scans GitHub repositories and produces a practical health report with a score out of 100, clear warnings, and actionable recommendations.

It is built for developers who want a quick repository quality review from the terminal, and for maintainers who want a small tool they can later run in CI.

## Quick Links

- [Arabic README](README.ar.md)
- [Installation Guide](INSTALLATION.md)
- [Usage Guide](USAGE.md)
- [Requirements](REQUIREMENTS.md)
- [Supported Checks](docs/checks.md)
- [Architecture](ARCHITECTURE.md)
- [Contributing](CONTRIBUTING.md)
- [Security Policy](SECURITY.md)
- [License](LICENSE)
- [Changelog](CHANGELOG.md)

## Features

- Scan public GitHub repositories by URL.
- Scan private repositories with `--token` or `GITHUB_TOKEN`.
- Fetch repository metadata and recursive file tree through the GitHub API.
- Score repository health out of 100.
- Render a Rich terminal report.
- Export Markdown reports.
- Print or write JSON reports.
- Produce compact summaries for automation.
- Fail CI jobs with `--fail-under`.
- Detect common sensitive file names without printing secret contents.
- Add advisory dependency and security baseline recommendations.

## Tech Stack

RepoPulse is built with:

| Technology | Purpose |
|---|---|
| Python 3.11+ | Core runtime. |
| Typer | CLI commands and options. |
| Requests | GitHub API calls. |
| Rich | Terminal tables and formatted output. |
| Pydantic | Typed report and check models. |
| python-dotenv | Optional `GITHUB_TOKEN` loading. |
| Pytest | Test suite. |
| Ruff | Linting in CI. |

## Installation

Clone the repository and install it in editable mode:

```bash
git clone https://github.com/3ssiri/RepoPluse.git
cd RepoPluse
pip install -e .
```

For development:

```bash
pip install -e ".[dev]"
```

See [INSTALLATION.md](INSTALLATION.md) for full setup notes.

## Basic Usage

```bash
repopulse scan https://github.com/username/repository
repopulse scan https://github.com/username/repository --export report.md
repopulse scan https://github.com/username/repository --format json --output report.json
repopulse scan https://github.com/username/repository --fail-under 75
repopulse scan https://github.com/username/private-repo --token YOUR_GITHUB_TOKEN
```

You can also set a token in the environment:

```bash
GITHUB_TOKEN=YOUR_GITHUB_TOKEN repopulse scan https://github.com/username/private-repo
```

See [USAGE.md](USAGE.md) for all options and examples.

## Example Output

```text
RepoPulse Health Report for psf/requests
Score: 91 / 100 - Excellent

Checks
README Quality      PASS   16/20
License             PASS   10/10
.gitignore          PASS   10/10
Tests               WARN   12/15
GitHub Actions      PASS   15/15
```

## Scoring System

| Check | Points |
|---|---:|
| README Quality | 20 |
| License | 10 |
| .gitignore | 10 |
| Tests | 15 |
| GitHub Actions | 15 |
| Recent Activity | 10 |
| Sensitive Files | 10 |
| Project Structure | 5 |
| Package Scripts | 5 |

Grades:

| Score | Grade |
|---|---|
| 90-100 | Excellent |
| 75-89 | Good |
| 60-74 | Fair |
| 40-59 | Weak |
| 0-39 | Critical |

Dependency and security baseline checks are advisory in `v0.1.0`; they add recommendations without changing the 100-point score.

## Supported Checks

- README completeness.
- License presence.
- `.gitignore` presence and common patterns.
- Test folders, test files, and package test commands.
- GitHub Actions workflows for CI, tests, linting, and builds.
- Recent activity based on `pushed_at`.
- Sensitive file names such as `.env`, `credentials.json`, and private keys.
- Project structure and root clutter.
- Package scripts or Python project configuration.
- Dependency hygiene through lockfiles and Dependabot.
- Security baseline through `SECURITY.md`, Dependabot, and CodeQL.

Full details are in [docs/checks.md](docs/checks.md).

## Requirements

- Python 3.11 or newer.
- Network access to `api.github.com`.
- GitHub token for private repositories or higher API rate limits.

See [REQUIREMENTS.md](REQUIREMENTS.md) for runtime and development requirements.

## Contributing

Contributions are welcome. Keep checks independent, return `CheckResult`, and add focused tests for new behavior.

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, testing, and contribution workflow.

## License

RepoPulse is released under the MIT License. See [LICENSE](LICENSE).
