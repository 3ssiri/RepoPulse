# Roadmap

RepoPulse is an early-stage maintainer tool. The roadmap focuses on making repository health checks more useful in real open source workflows.

## Near Term

- ~~Publish installation-ready releases.~~ Done — GitHub Releases on `v*` tags **and** PyPI package [`repopulse-cli`](https://pypi.org/project/repopulse-cli/) (CLI `repopulse`). Maintainers: [docs/PUBLISHING.md](PUBLISHING.md).
- ~~Expand check coverage for common Python, JavaScript, and documentation patterns.~~ Done for Actions + Tests heuristics (tox/nox/hatch/jest/…); further ecosystems still welcome as contributions.
- ~~Add richer Markdown reports for maintainers and contributors.~~ Done — attention sections, pass/warn/fail counts, applied config.
- ~~Improve JSON output stability for automation.~~ Done — sorted keys + [json-schema.md](json-schema.md) contract for `schema_version` 1.0.
- ~~Add examples for running RepoPulse in GitHub Actions.~~ Done — see `examples/github-action-repopulse.yml` and USAGE.md CI section.

## Maintainer Automation

- ~~Generate issue-ready recommendations from failed checks.~~ Done — `--format issues`.
- ~~Create GitHub issues from recommendations.~~ Done — `repopulse create-issues` (`--dry-run` / `--yes`; dedupe open titles by default, `--no-dedupe` to force).
- ~~Expand configurable score weights with named profiles.~~ Done — `strict` \| `library` \| `docs` \| `release`.
- ~~Add comparison reports across releases or branches.~~ Done — `repopulse compare <baseline> <target>` with `--fail-on-regression`.
- ~~GitHub ref-aware scan/compare without local checkout.~~ Done — `/tree/<ref>`, `/releases/tag/<tag>`, `--ref` / `--baseline-ref` / `--target-ref`.
- ~~Provide templates for release readiness checks.~~ Done — `profile: release` and `examples/profiles/release.yml`.

## Security and Quality

- Keep sensitive file detection content-safe by reporting file names only.
- ~~Expand security baseline checks around Dependabot, CodeQL, and security policy setup.~~ Done — per-gap recommendations + extra scanners (Trivy, Semgrep, gitleaks, …).
- ~~Document responsible usage for private repositories and tokens.~~ Done — USAGE token hygiene section.

## Community

- ~~Keep contributor setup lightweight.~~ Done — [CONTRIBUTING.md](../CONTRIBUTING.md) with false-positive reporting.
- Label beginner-friendly issues (`good first issue`) when filing small keyword/test tasks.
- Use public issues for roadmap discussion and private advisories for vulnerabilities ([SECURITY.md](../SECURITY.md)).

## Later ideas

- Ecosystem-specific plugins or optional deeper parsers (e.g. full Makefile targets).
- Dedupe create-issues by label + check key as well as title.
- GitHub API rate-limit wait/retry only if production scans hit quota pain (errors are already clear).
