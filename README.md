# RepoPulse

RepoPulse is a Python CLI tool that scans GitHub repositories, evaluates repository health, detects missing project essentials, warns about risky file names, and generates a clear quality report with a score out of 100.

## What is RepoPulse?

RepoPulse helps developers review the public quality signals of a GitHub repository from the terminal. It uses the GitHub API to fetch repository metadata and the recursive file tree, then runs independent checks for documentation, license, tests, CI, activity, structure, and package commands.

## Features

- Scan public GitHub repositories by URL.
- Scan private repositories with `--token` or `GITHUB_TOKEN`.
- Score repository health out of 100.
- Render a Rich terminal report.
- Print compact summaries for automation.
- Export Markdown reports with `--export`.
- Print or write machine-readable JSON.
- Fail CI jobs with `--fail-under`.
- Advisory dependency and security baseline checks.
- Avoid printing secret contents; sensitive-file checks inspect file names only.

## Installation

```bash
pip install -e .
```

For development:

```bash
pip install -e ".[dev]"
```

## Usage

```bash
repopulse scan https://github.com/username/repository
repopulse scan https://github.com/username/repository --export report.md
repopulse scan https://github.com/username/repository --json
repopulse scan https://github.com/username/repository --format markdown --output report.md
repopulse scan https://github.com/username/repository --format json --output report.json
repopulse scan https://github.com/username/repository --fail-under 75
repopulse scan https://github.com/username/repository --quiet
repopulse scan https://github.com/username/repository --verbose
repopulse scan https://github.com/username/private-repo --token YOUR_GITHUB_TOKEN
```

You can also set a token in the environment:

```bash
GITHUB_TOKEN=YOUR_GITHUB_TOKEN repopulse scan https://github.com/username/private-repo
```

## Example Output

```text
RepoPulse Health Report for psf/requests
Score: 89 / 100 - Good

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

## Supported Checks

- README completeness: description, installation, usage, features, and tech stack.
- License presence.
- `.gitignore` presence and common ignore patterns.
- Test directories, test files, and package test commands.
- GitHub Actions workflows for CI, tests, linting, and builds.
- Recent activity based on `pushed_at`.
- Sensitive file names such as `.env`, `credentials.json`, and private keys.
- Project structure directories and root clutter.
- Package scripts or Python project configuration.
- Dependency hygiene through lockfiles and Dependabot.
- Security baseline through `SECURITY.md`, Dependabot, and CodeQL.

Dependency and security checks are advisory in v0.1.0, so they add recommendations without changing the 100-point core score.

## Roadmap

- GitHub Action for automatic repository checks.
- Score badge generation.
- Web dashboard.
- Dependency freshness and security checks.
- GitLab support.

## Contributing

Contributions are welcome. Keep checks independent, return `CheckResult`, and add focused tests for new behavior.

## License

MIT
