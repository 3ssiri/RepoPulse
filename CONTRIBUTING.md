# Contributing

Thank you for considering a contribution to RepoPulse.

## Local Setup

```bash
git clone https://github.com/3ssiri/RepoPulse.git
cd RepoPulse
pip install -e ".[dev]"
```

Run the test suite:

```bash
pytest
```

## Project Structure

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

## User-facing package name

End users install from PyPI as **`repopulse-cli`**. The import package and CLI remain **`repopulse`**. Do not document `pip install repopulse` for this project.

## Adding a New Check

1. Add a new file under `repopulse/checks/`.
2. Return a `CheckResult`.
3. Export the function from `repopulse/checks/__init__.py`.
4. Call the check from `repopulse/analyzer.py`.
5. Add focused tests in `tests/test_checks.py` or a new test file.
6. Update [docs/checks.md](docs/checks.md).

## Check Guidelines

- Keep checks deterministic and independent.
- Do not make network calls inside check modules.
- Do not print or return secret file contents.
- Prefer clear recommendations over vague warnings.
- Keep the score weights aligned with README and docs.

## Commit and Pull Request Guidelines

- Keep changes focused.
- Include tests for behavior changes.
- Update documentation when commands, checks, scoring, or outputs change.
- Run `pytest` before opening a pull request.
- Use the pull request template and describe user-visible behavior changes.

## Development Commands

```bash
pytest
repopulse scan https://github.com/psf/requests --format summary --quiet
```
