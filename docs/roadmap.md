# Roadmap

RepoPulse is an early-stage maintainer tool. The roadmap focuses on making repository health checks more useful in real open source workflows.

## Near Term

- Publish installation-ready releases. (Partial: version `0.2.0`, GitHub Release assets, and packaging docs ready; first PyPI upload still pending — needs `PYPI_API_TOKEN`.)
- Expand check coverage for common Python, JavaScript, and documentation patterns. (Partial: deeper tests/Actions heuristics shipped.)
- ~~Add richer Markdown reports for maintainers and contributors.~~ Done — attention sections, pass/warn/fail counts, applied config.
- ~~Improve JSON output stability for automation.~~ Done — sorted keys + [json-schema.md](json-schema.md) contract for `schema_version` 1.0.
- ~~Add examples for running RepoPulse in GitHub Actions.~~ Done — see `examples/github-action-repopulse.yml` and USAGE.md CI section.

## Maintainer Automation

- ~~Generate issue-ready recommendations from failed checks.~~ Done — `--format issues`.
- ~~Expand configurable score weights with named profiles.~~ Done — `strict` \| `library` \| `docs` \| `release`.
- Add comparison reports across releases or branches.
- ~~Provide templates for release readiness checks.~~ Done — `profile: release` and `examples/profiles/release.yml`.

## Security and Quality

- Keep sensitive file detection content-safe by reporting file names only.
- ~~Expand security baseline checks around Dependabot, CodeQL, and security policy setup.~~ Done — per-gap recommendations + extra scanners (Trivy, Semgrep, gitleaks, …).
- ~~Document responsible usage for private repositories and tokens.~~ Done — USAGE token hygiene section.

## Community

- Keep contributor setup lightweight.
- Label beginner-friendly issues.
- Use public issues for roadmap discussion and private advisories for vulnerabilities.

## Later ideas

- Publish to PyPI (`pip install repopulse`).
- Optional `gh issue create` integration from issues format.
- Branch/tag score comparison (`scan` A vs B).
