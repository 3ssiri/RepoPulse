# RepoPulse

[![CI](https://github.com/3ssiri/RepoPulse/actions/workflows/ci.yml/badge.svg)](https://github.com/3ssiri/RepoPulse/actions/workflows/ci.yml)
[![CodeQL](https://github.com/3ssiri/RepoPulse/actions/workflows/codeql.yml/badge.svg)](https://github.com/3ssiri/RepoPulse/actions/workflows/codeql.yml)
[![PyPI version](https://img.shields.io/pypi/v/repopulse-cli.svg)](https://pypi.org/project/repopulse-cli/)
[![Python](https://img.shields.io/pypi/pyversions/repopulse-cli.svg)](https://pypi.org/project/repopulse-cli/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

```bash
pip install repopulse-cli
repopulse scan .
```

RepoPulse is a Python CLI that scans GitHub repositories (or a local folder) and produces a practical **health report**: score out of 100, pass/warn/fail checks, and actionable recommendations.

It is built for developers who want a quick quality review from the terminal, and for maintainers who want a small tool in CI, release prep, or issue triage.

| | Name |
|---|---|
| **Install from PyPI** | `repopulse-cli` |
| **CLI command** | `repopulse` |
| **Python import** | `repopulse` |

> **Important:** Do **not** run `pip install repopulse`. That installs an **unrelated** package on PyPI. Always use **`repopulse-cli`**.

## Install (for users)

```bash
pip install repopulse-cli
repopulse --help
```

Upgrade:

```bash
pip install -U repopulse-cli
```

Optional isolated environment (recommended if other tools pin different dependency versions):

```bash
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# macOS / Linux:
# source .venv/bin/activate
pip install repopulse-cli
```

From a GitHub Release wheel (if you prefer not to use PyPI):

```bash
pip install https://github.com/3ssiri/RepoPulse/releases/download/v0.3.4/repopulse_cli-0.3.4-py3-none-any.whl
```

Full install notes: [INSTALLATION.md](INSTALLATION.md).

## Quick start

```bash
# Local directory (offline — no GitHub API)
repopulse scan .

# Public GitHub repository
repopulse scan https://github.com/psf/requests

# Specific branch or tag (no local checkout)
repopulse scan https://github.com/psf/requests/tree/main
repopulse scan https://github.com/psf/requests --ref v2.32.0

# CI gate
repopulse scan https://github.com/username/repository --fail-under 75 --format summary --quiet

# Compare two refs or checkouts
repopulse compare \
  https://github.com/owner/repo/tree/main \
  https://github.com/owner/repo/tree/feature/pr-42 \
  --fail-on-regression

# Preview GitHub issues from fail/warn checks
repopulse create-issues https://github.com/owner/repo --dry-run
```

Private repos: pass `--token` or set `GITHUB_TOKEN`. Details: [USAGE.md](USAGE.md).

## Features (current)

### Scanning

- Scan **public GitHub** repositories by URL.
- Scan a **local directory** offline: `repopulse scan .` (no API, no rate limits).
- Scan a specific **branch, tag, or commit** via URL (`/tree/<ref>`, `/releases/tag/<tag>`) or `--ref`.
- Scan **private** repositories with `--token` or `GITHUB_TOKEN`.
- Shared check pipeline for remote and local sources.

### Reports and output

- Score out of **100** with grades (Excellent → Critical).
- Rich **terminal table** (default).
- Formats: `table`, `summary`, `markdown`, `json`, `issues`.
- Export Markdown (`--export`) and write any format to a file (`--output`).
- Stable JSON contract (`schema_version` 1.0) — see [docs/json-schema.md](docs/json-schema.md).
- Richer Markdown: pass/warn/fail counts, attention sections, applied config.

### Compare

- `repopulse compare <baseline> <target>` — local paths and/or GitHub URLs.
- Per-side refs: tree URLs or `--baseline-ref` / `--target-ref`.
- Formats: `table`, `markdown`, `json`, `summary`.
- CI gate: `--fail-on-regression` (exit code `2` if score drops or any check regresses).

### Issues and automation

- `--format issues` — paste-ready Markdown for fail/warn checks.
- `repopulse create-issues` — open real GitHub issues (`--dry-run` or `--yes`).
- CI example: [examples/github-action-repopulse.yml](examples/github-action-repopulse.yml).
- Optional config `.repopulse.yml` with profiles: `strict`, `library`, `docs`, `release`.

### Safety

- Detects common **sensitive file names** (`.env`, keys, credentials) without printing file contents.
- Advisory dependency and security baseline checks (recommendations; do not change the 100-point score by default).

## Commands

| Command | Purpose |
|---|---|
| `repopulse scan <url-or-path>` | Health report for one repository or folder. |
| `repopulse compare <baseline> <target>` | Diff two health reports. |
| `repopulse create-issues <url-or-path>` | Create GitHub issues from fail/warn checks. |

## Configuration

RepoPulse reads `.repopulse.yml` from the current directory when present, or via `--config`:

```bash
repopulse scan . --config examples/repopulse.yml
```

```yaml
profile: release   # optional: strict | library | docs | release
fail_under: 90
disabled_checks:
  - activity
weights:
  tests: 25
  github_actions: 20
```

Ready-made profiles: [examples/profiles/](examples/profiles/).

## Scoring (default weights)

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

| Score | Grade |
|---|---|
| 90–100 | Excellent |
| 75–89 | Good |
| 60–74 | Fair |
| 40–59 | Weak |
| 0–39 | Critical |

Dependency and security baseline checks are **advisory**: they add recommendations without changing the scored total.

Full check reference: [docs/checks.md](docs/checks.md).

## Example output

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

## Install for contributors / from source

```bash
git clone https://github.com/3ssiri/RepoPulse.git
cd RepoPulse
pip install -e ".[dev]"
pytest
```

See [CONTRIBUTING.md](CONTRIBUTING.md) and [INSTALLATION.md](INSTALLATION.md).

## Documentation

| Doc | Contents |
|---|---|
| [INSTALLATION.md](INSTALLATION.md) | PyPI, wheel, source, tokens, troubleshooting |
| [USAGE.md](USAGE.md) | All commands, flags, CI, config, exit codes |
| [REQUIREMENTS.md](REQUIREMENTS.md) | Runtime and dev dependencies |
| [docs/checks.md](docs/checks.md) | What each check evaluates |
| [docs/json-schema.md](docs/json-schema.md) | JSON report contract |
| [docs/PUBLISHING.md](docs/PUBLISHING.md) | Releases and PyPI publishing (maintainers) |
| [docs/roadmap.md](docs/roadmap.md) | Product roadmap |
| [docs/dogfood.md](docs/dogfood.md) | Real-repo score snapshots |
| [ARCHITECTURE.md](ARCHITECTURE.md) | How the code is structured |
| [CHANGELOG.md](CHANGELOG.md) | Version history |
| [README.ar.md](README.ar.md) | Arabic summary |
| [README.es-ES.md](README.es-ES.md) | Spanish summary |

## Requirements

- Python **3.11+**
- Network access to `api.github.com` for remote scans
- GitHub token for private repos, higher rate limits, or `create-issues --yes`

## Contributing

Contributions are welcome — especially **false-positive reports** from real repos, small check improvements, and docs.

```bash
git clone https://github.com/3ssiri/RepoPulse.git
cd RepoPulse
pip install -e ".[dev]"
pytest
ruff check .
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for check guidelines and how to report scoring issues.

## License

MIT — see [LICENSE](LICENSE).

## Links

- PyPI: https://pypi.org/project/repopulse-cli/
- Releases: https://github.com/3ssiri/RepoPulse/releases
- Issues: https://github.com/3ssiri/RepoPulse/issues
