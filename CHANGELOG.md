# Changelog

## Unreleased

- Added `repopulse compare <baseline> <target>` to diff two health scans (local paths and/or GitHub URLs).
- Comparison formats: `table`, `markdown`, `json`, `summary`; labels via `--baseline-label` / `--target-label`.
- CI gate: `--fail-on-regression` exits with code 2 when the score drops or any check regresses.

## 0.2.1 - 2026-08-02

- Fixed broken Release workflow (invalid `secrets` in `if` caused cascading "workflow file issue" failures).
- Release now runs **only on `v*` tags**: lint, test, build, twine check, attach assets to GitHub Release.
- CI limited to `main` + pull requests; matrix Python 3.11/3.12; package build smoke on 3.11.
- Modern packaging metadata: SPDX `license = "MIT"`, `license-files`, setuptools>=77 (removes license deprecation noise).
- Richer Markdown reports (pass/warn/fail counts, attention sections, applied config).
- Expanded security baseline recommendations and extra scanner signals.
- Added `release` scoring profile and JSON contract docs.
- Documented publishing steps in `docs/PUBLISHING.md`.

## 0.2.0 - 2026-08-02

- Added offline local path scanning (`repopulse scan .` or any existing directory) with a shared check pipeline for GitHub and local sources.
- Added `--format issues` for GitHub-issue-ready Markdown blocks from fail/warn checks.
- Added GitHub Actions example for CI health gates (`examples/github-action-repopulse.yml`).
- Added named scoring profiles (`strict`, `library`, `docs`) via `profile` in `.repopulse.yml`, with user overrides for weights, disabled checks, and fail_under.
- Deepened Tests and GitHub Actions checks with framework-aware and CI-substance heuristics (still content-light, max 15 each).
- Added optional `.repopulse.yml` configuration for disabled checks, custom weights, and default CI thresholds.
- Added `schema_version` and config metadata to JSON reports.
- Updated Typer, pytest, and Ruff dependency ranges.
- Release packaging prep: version `0.2.0`, `python -m build` support, and GitHub release workflow for sdist/wheel artifacts (optional PyPI publish when `PYPI_API_TOKEN` is set).

## 0.1.0 - 2026-06-01

- Initial RepoPulse CLI release.
- Added GitHub repository scanning.
- Added health checks, scoring, Rich terminal output, Markdown export, and JSON output.
- Added `--format`, `--output`, `--fail-under`, `--quiet`, and `--verbose`.
- Added advisory dependency and security baseline checks.
- Added project CI, Dependabot, CodeQL, and security policy.
- Added pytest coverage for parser, scoring, checks, and Markdown reporting.
- Expanded public documentation with installation, usage, requirements, architecture, contribution, Arabic README, and check reference guides.
