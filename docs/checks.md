# Supported Checks

RepoPulse produces a 100-point score from core checks and adds advisory recommendations from supplemental checks.

The default score is 100 points. Projects can customize scored check weights or disable checks with `.repopulse.yml`.

## Profiles

Named profiles apply ready-made `weights`, optional `disabled_checks`, and `fail_under` in `.repopulse.yml`:

```yaml
profile: strict
```

| Profile | fail_under | Notes |
|---|---:|---|
| `strict` | 85 | CI gate preset; tests and GitHub Actions at 20 each. |
| `library` | 75 | Higher tests/license; lower activity; `package_scripts` weight 0. |
| `docs` | 70 | README at 35; `package_scripts` weight 0. |

Overrides when a profile is set:

- `weights`: merge over the profile (your keys win).
- `disabled_checks`: your list replaces the profile list.
- `fail_under`: your value replaces the profile threshold.

Weight `0` keeps the check in the report but zeros its score contribution. Omitting `profile` leaves empty defaults (unchanged behavior). See [USAGE.md](../USAGE.md) and `examples/profiles/`.

## Core Scored Checks

| Check | Points | What It Looks For |
|---|---:|---|
| README Quality | 20 | README file, clear description, installation, usage, features, and tech stack. |
| License | 10 | `LICENSE`, `LICENSE.md`, or `COPYING`. |
| .gitignore | 10 | `.gitignore` plus common patterns such as `.env`, caches, dependencies, and build outputs. |
| Tests | 15 | Test directories/files, framework signals (pytest, jest, vitest, …), and a test command. |
| GitHub Actions | 15 | Workflows that run tests and quality tools (lint/format/type-check). |
| Recent Activity | 10 | Recent `pushed_at` timestamp from GitHub. |
| Sensitive Files | 10 | Common sensitive file names such as `.env`, `credentials.json`, `private-key.pem`, and `id_rsa`. |
| Project Structure | 5 | Organized source/docs directories and limited root clutter. |
| Package Scripts | 5 | Node scripts or Python project/tooling configuration. |

## Advisory Checks

Advisory checks currently use `max_score=0`. They do not change the 100-point score, but they add recommendations.

| Check | What It Looks For |
|---|---|
| Dependencies | Dependency manifest, lockfile, and Dependabot configuration. |
| Security Baseline | `SECURITY.md`, Dependabot, and CodeQL workflow. |

## Sensitive File Safety

RepoPulse checks sensitive file names only. It does not print sensitive file contents.

If a sensitive file name is detected, the recommendation is to remove the file from the repository history when needed and rotate any exposed credentials.

## README Quality Scoring

| Signal | Points |
|---|---:|
| README exists | 8 |
| Clear description | 3 |
| Installation section | 3 |
| Usage section | 3 |
| Features section | 2 |
| Tech stack section | 1 |

## Activity Scoring

| Last Push | Points |
|---|---:|
| Last 30 days | 10 |
| Last 6 months | 7 |
| Last year | 4 |
| More than a year | 1 |
| Unknown | 0 |

## Tests Scoring

Content-light heuristics only (no network, no test execution). Max remains 15.

| Condition | Points |
|---|---:|
| Test dir or files **and** a test command (optional framework label in message) | 15 |
| Test dir **and** test files, no command | 12 |
| Only dir **or** only files | 7 |
| Framework config only (e.g. pytest in pyproject, no test files) | 4 |
| Nothing | 0 |

**Signals considered:**

- Directories: `tests/`, `test/`, `__tests__/`
- Files: `test_*`, `*_test.py`, `*.test.*`, `*.spec.*`
- Python: `pytest` / `[tool.pytest.ini_options]` in pyproject, `pytest.ini`, `conftest.py`, `tox.ini`
- Node: `scripts.test` in package.json; runners `jest`, `vitest`, `mocha`, `ava`, `node:test` in scripts or deps

## GitHub Actions Scoring

Workflows under `.github/workflows/` only. Max remains 15.

| Condition | Points |
|---|---:|
| Workflows + tests + quality | 15 |
| Workflows + tests, no quality | 12 |
| Workflows + quality only | 10 |
| Workflows only (no test/quality signal) | 6 |
| No workflows | 0 |

Status: pass if score ≥ 12, warn if 1–11, fail if 0.

**Test tokens (examples):** `pytest`, `python -m pytest`, `npm test`, `npm run test`, `pnpm test`, `yarn test`, `vitest`, `jest`, `cargo test`, `go test`, `unittest`

**Quality tokens (examples):** `ruff`, `eslint`, `flake8`, `mypy`, `lint`, `prettier`, `black`, `format`

**Also noted in the message when present:** setup steps (`actions/setup-python`, `actions/setup-node`, `pip install`, `npm ci`, `pnpm install`) and triggers (`pull_request`, `push:`).
