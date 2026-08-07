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

- JSON output is a stable contract (`schema_version` 1.1, `docs/json-schema.md`): any field change requires a `schema_version` bump.
- No silent large shifts of default scoring — `CHANGELOG.md` entry required; keep weights in sync across README, `docs/checks.md`, and `scoring.py`.
- Prefer reducing false positives over adding noisy recommendations.

## Security review (2026-08-07) — closed in v0.3.6

An external security review produced 5 findings; all were fixed test-first and shipped in v0.3.6. What remains are the **standing rules** that came out of it:

- **No env-file auto-loading, ever.** The tool scans untrusted repos; `python-dotenv` was removed because its `.env` search can land inside the scanned repo (e.g. injecting `HTTPS_PROXY` to exfiltrate the token). The GitHub token comes only from `--token` or the process environment.
- **Truncation must stay visible.** `HealthReport.scan_truncated` carries the local max-files cap and the GitHub tree API `truncated` flag; renderers warn. Any new file-listing path must propagate it.
- **Never claim unverifiable facts.** Offline scans report `repository.private` as `null`/"Unknown" (this forced the `schema_version` 1.0 → 1.1 bump), not a guessed boolean.
- **Pin actions by full commit SHA** with the `@<sha> # vX` comment convention (Dependabot updates the SHAs). Keep workflow permissions read-only by default; grant write per job only.

Confirmed strengths from the same review (preserve them): no `eval`/`exec`/`shell=True`, URL validation restricted to `github.com`, API calls only to `api.github.com`, path-traversal and symlink care in local scans.

## Reviewing external pull requests

Merging a PR permanently writes its author into this repository's history and contributor list (git keeps the PR author as commit `author`; the merge button only sets `committer`). Treat every outside PR as untrusted input and read it in full before merging — the friendly ones look identical to the hostile ones.

Check, in order:

1. **Workflow and CI files** — a changed `.github/workflows/*` can exfiltrate secrets or run arbitrary code on merge. Any action added must be SHA-pinned. Highest risk; check first even in a "docs-only" PR.
2. **Every URL and install command**, including inside docs and translations — links must point at this repo or well-known registries; reject anything that pipes a remote script to a shell or redirects installs elsewhere.
3. **Dependency and packaging changes** — a new or bumped dependency in `pyproject.toml` / lockfiles deserves the same scrutiny as code.
4. **Documented behavior must match the code** — translations of README/USAGE go stale silently and can end up promising behavior the security rules above removed (e.g. `.env` loading).
5. **Author pattern** — bulk drive-by PRs from automated accounts (very new account, thousands of public repos, one-line body, no follow-up) are usually promotional. That alone is not a reason to reject, but it removes any benefit of the doubt: judge the diff on its own merits, and never fast-merge on the assumption that "it is only docs".

Precedent: PR #24 (Spanish README, merged 2026-08-02) came from such an account; the content was verified clean and the file has since been rewritten twice.

## Hygiene rules for agents

- Never put internal service IDs, tokens, or personal identifiers in tracked files. Local-only values go in `*.local.md` / `docs/*.local` files (gitignored) — e.g. `AGENTS.local.md`.
- Do not reference private matters (funding, personal notes) in commit messages or tracked file names.
