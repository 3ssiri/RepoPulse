# Changelog

## Unreleased

- Added GitHub Actions example for CI health gates (`examples/github-action-repopulse.yml`).
- Added named scoring profiles (`strict`, `library`, `docs`) via `profile` in `.repopulse.yml`, with user overrides for weights, disabled checks, and fail_under.
- Deepened Tests and GitHub Actions checks with framework-aware and CI-substance heuristics (still content-light, max 15 each).
- Added optional `.repopulse.yml` configuration for disabled checks, custom weights, and default CI thresholds.
- Added `schema_version` and config metadata to JSON reports.
- Updated Typer, pytest, and Ruff dependency ranges.

## 0.1.0 - 2026-06-01

- Initial RepoPulse CLI release.
- Added GitHub repository scanning.
- Added health checks, scoring, Rich terminal output, Markdown export, and JSON output.
- Added `--format`, `--output`, `--fail-under`, `--quiet`, and `--verbose`.
- Added advisory dependency and security baseline checks.
- Added project CI, Dependabot, CodeQL, and security policy.
- Added pytest coverage for parser, scoring, checks, and Markdown reporting.
- Expanded public documentation with installation, usage, requirements, architecture, contribution, Arabic README, and check reference guides.
