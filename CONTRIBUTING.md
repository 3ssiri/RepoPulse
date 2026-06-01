# Contributing

Thank you for considering a contribution to RepoPulse.

## Local Setup

```bash
git clone https://github.com/3ssiri/RepoPluse.git
cd RepoPluse
pip install -e ".[dev]"
```

Run the test suite:

```bash
pytest
```

## Project Structure

```text
repopulse/
  cli.py
  analyzer.py
  github_client.py
  models.py
  report.py
  scoring.py
  url_parser.py
  checks/
tests/
examples/
docs/
```

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

## Development Commands

```bash
pytest
repopulse scan https://github.com/psf/requests --format summary --quiet
```
