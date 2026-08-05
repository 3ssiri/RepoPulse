# Contributing

Thank you for considering a contribution to RepoPulse.

## Ways to help

| Area | Ideas |
|---|---|
| **Bug reports** | False positives/negatives from real repos (include score + check key + repo URL). |
| **Checks** | Deeper heuristics for a single ecosystem (Python, JS, docs). |
| **Docs** | Install/usage clarity, translations (`README.ar.md`, `README.es-ES.md`). |
| **Good first issues** | Small test cases, keyword lists, docs typos — label `good first issue` when filing. |

Please open an issue before large features so we can align on scope.

## Local setup

```bash
git clone https://github.com/3ssiri/RepoPulse.git
cd RepoPulse
python -m venv .venv
# Windows: .\.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -U pip
pip install -e ".[dev]"
```

## Development commands

```bash
# Tests
pytest

# Lint
ruff check .

# Try the CLI on a public repo
repopulse scan https://github.com/psf/requests --format summary --quiet
repopulse scan . --format summary --quiet
```

End users install from PyPI as **`repopulse-cli`** (CLI remains `repopulse`). Do not document `pip install repopulse` for this project.

## Project structure

```text
repopulse/
  cli.py              # scan, compare, create-issues
  analyzer.py         # shared report pipeline (GitHub + local)
  github_client.py    # GitHub API (tree, contents, issues)
  local_source.py     # offline directory walk
  compare.py          # report diffs
  issue_export.py     # issue payloads from checks
  models.py
  report.py
  scoring.py
  settings.py         # .repopulse.yml + profiles
  url_parser.py       # owner/repo/ref from GitHub URLs
  checks/             # one module per health check
tests/
examples/             # CI workflow + config profiles
docs/
```

## Adding a new check

1. Add a new file under `repopulse/checks/`.
2. Return a `CheckResult`.
3. Export the function from `repopulse/checks/__init__.py`.
4. Call the check from `repopulse/analyzer.py`.
5. Add focused tests in `tests/test_checks.py` or a new test file.
6. Update [docs/checks.md](docs/checks.md) and [CHANGELOG.md](CHANGELOG.md) under Unreleased.

## Check guidelines

- Keep checks deterministic and independent.
- Do not make network calls inside check modules.
- Do not print or return secret file contents (names only for sensitive files).
- Prefer clear, gap-specific recommendations over vague warnings.
- Prefer **warn** over **fail** for fixture/example paths and keyword misses on mature OSS.
- Heuristics are strongest for **Python** and **JS/TS**; do not pretend full multi-language coverage.

## Release / contract rules

See [docs/json-schema.md](docs/json-schema.md#scoring-and-release-rules-do-not-break-ci-quietly):

- No silent breaks of JSON fields (`schema_version` bump required).
- No silent large shifts of default scoring without `CHANGELOG.md`.
- Prefer reducing false positives over adding noisy recommendations.
- Keep score weights aligned with README and docs.

## Reporting false positives

When a check is unfair on a real repository, please include:

1. Repo URL (and ref if relevant)
2. `repopulse` version (`python -c "import repopulse; print(repopulse.__version__)"`)
3. Check key (e.g. `github_actions`, `license`)
4. Why you believe the finding is wrong
5. Optional: score before/after a suggested fix

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md) and prefix the title with `False positive:` when applicable.

## Commit and pull request guidelines

- Keep changes focused.
- Include tests for behavior changes.
- Update documentation when commands, checks, scoring, or outputs change.
- Run `pytest` and `ruff check .` before opening a pull request.
- Use the pull request template and describe user-visible behavior changes.

## Code of conduct

Be respectful and constructive. Maintainers may close issues or PRs that are hostile or spammy. Security issues: see [SECURITY.md](SECURITY.md).
