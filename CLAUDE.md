# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

RepoPulse — a Python CLI (`repopulse`) that scans a GitHub repository or a local directory and produces a health report: score out of 100, pass/warn/fail checks, and recommendations. Python 3.11+.

**Naming rule:** the PyPI distribution is `repopulse-cli`; the import package and CLI command are `repopulse`. Never document `pip install repopulse` — that is an unrelated package.

## Commands

```bash
pip install -e ".[dev]"        # dev setup

pytest                          # all tests
pytest tests/test_checks.py     # one file
pytest -k test_name             # one test

ruff check .                    # lint (config in pyproject.toml)
mypy repopulse                  # type check

# Try the CLI
repopulse scan . --format summary --quiet
repopulse scan https://github.com/psf/requests
```

Run `pytest` and `ruff check .` before any PR.

## Architecture

Single shared pipeline for both sources (see ARCHITECTURE.md):

```
cli.py (Typer: scan | compare | create-issues)
  ├─ local path  → local_source.py   (offline walk + git metadata, no API)
  └─ GitHub URL  → url_parser.py → github_client.py (api.github.com: repo, tree@ref, contents@ref)
        ↓
analyzer.py (shared check pipeline) → checks/* → scoring.py → models.HealthReport
        ↓
report.py (table | summary | markdown | json | issues)
```

- `compare.py` diffs two `HealthReport`s; `--fail-on-regression` exits 2.
- `issue_export.py` builds GitHub issue payloads from fail/warn checks.
- `settings.py` loads `.repopulse.yml` + named profiles (`strict`, `library`, `docs`, `release`).
- Core checks feed the 100-point score; advisory checks (dependencies, security baseline) use `max_score=0` — recommendations only, score unchanged.
- GitHub/network failures are wrapped in `GitHubAPIError` so the CLI prints concise messages.

## Adding a check

1. New module under `repopulse/checks/` returning a `CheckResult`.
2. Export from `checks/__init__.py`, call from `analyzer.py`.
3. Tests in `tests/test_checks.py`; update `docs/checks.md` and `CHANGELOG.md` (Unreleased).

Check rules: deterministic, no network calls, never print sensitive file **contents** (names only). Prefer **warn** over **fail** for fixture/example paths and keyword misses on mature OSS. Heuristics target Python and JS/TS — do not pretend full multi-language coverage.

## Contract rules (do not break silently)

- JSON output is a stable contract (`schema_version` 1.0, `docs/json-schema.md`): any field change requires a `schema_version` bump.
- No silent large shifts of default scoring — `CHANGELOG.md` entry required; keep weights in sync across README, `docs/checks.md`, and `scoring.py`.
- Prefer reducing false positives over adding noisy recommendations.

## Known issues (external security review, 2026-08-07)

Accepted findings, not yet fixed — good candidates for next work:

1. `repopulse/local_source.py:28` — `MAX_FILES = 5000` silently caps local scans, and the GitHub tree path does not propagate the API's `truncated` flag. A huge repo can get a complete-looking score. Fix direction: carry a `scan_truncated` flag into the report and warn explicitly.
2. `repopulse/local_source.py:162` — local scans hardcode `private=False` even for clones of private repos; should be "unknown" unless verifiable.
3. `repopulse/config.py` — `load_dotenv()` reads `.env` from the CWD. Since the tool scans untrusted repos, a scanned project's `.env` can influence the tool's environment. Prefer reading `GITHUB_TOKEN` explicitly from the process environment.
4. `.github/workflows/*` — actions are pinned by tag (`@v7`, `@v3`…), not full commit SHA; GitHub recommends full-length SHA pinning. `release.yml` grants `contents: write` at workflow level — scope it to the job that needs it.

Confirmed strengths from the same review: no `eval`/`exec`/`shell=True`, URL validation restricted to `github.com`, API calls only to `api.github.com`, path-traversal and symlink care in local scans, `python-dotenv>=1.2.2` (post-CVE).

## Hygiene rules for agents

- Never put internal service IDs, tokens, or personal identifiers in tracked files. Local-only values go in `*.local.md` / `docs/*.local` files (gitignored) — e.g. `AGENTS.local.md`.
- Do not reference private matters (funding, personal notes) in commit messages or tracked file names.
