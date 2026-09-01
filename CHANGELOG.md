# Changelog

## Unreleased

### Added

- **Optional web app + WebMCP** (`webapp/`, extra `web`): one-page dashboard over the existing scan/compare engine, plus four read-only tools (`scan_repository`, `get_attention_items`, `get_check_details`, `compare_refs`) so a human and an agent share the same page state. Public github.com repositories only; `GITHUB_TOKEN` is server-side. Not packaged in `repopulse-cli`. Docs: [docs/webmcp-challenge.md](docs/webmcp-challenge.md).
- **GitHub Action** (`action.yml` at the repository root): run a health check in CI with `uses: 3ssiri/RepoPulse@v1`. Writes the Markdown report to the workflow run summary, exposes `score` / `max-score` / `percentage` / `grade` / `truncated` / report paths as outputs, and optionally fails the build via `fail-under`. Inputs are passed through environment variables (no shell interpolation), and the installed package version is pinned. Docs: [docs/github-action.md](docs/github-action.md).
- CI dogfoods the action on every push.
- Vercel deployment config for the optional web layer (`vercel.json`, root `requirements.txt`, `[tool.vercel] entrypoint`). Deployment-only: scoring, checks, report schemas, CLI contracts, the GitHub Action and the published `repopulse-cli` package are unchanged.

### Fixed

- Web dashboard keeps the last successful repository selected when a later scan fails, so compare and the on-screen report stay aligned.
- Compare form error tells humans to scan a repository first (no tool-name jargon). Whitespace-only compare refs are rejected.
- Compare-before-scan now shows the error in the page instead of failing silently.
- In-flight scan/compare results are discarded when a newer request has already changed the selected repository.
- URL-derived refs use the same 256-character limit as body refs.
- Partial WebMCP tool registration is aborted if any `registerTool` call fails.
- The web adapter reuses the privacy-check repository payload so scan/compare do not call `get_repo` twice.

## 0.3.6 - 2026-08-07

Security/trust release: all five findings from an external security review are addressed.

### CI / supply chain

- All GitHub Actions are pinned to full commit SHAs (with `# vX` comments for readability; Dependabot keeps them updated). Full-length SHAs are the only immutable action reference.
- Release workflow default permission narrowed to `contents: read`; only the job that creates the GitHub Release keeps `contents: write`.

### Trust / accuracy

- **Truncated scans are now visible.** Large repositories no longer get a complete-looking score silently: the local max-files cap and the GitHub tree API `truncated` flag now surface as a new additive JSON field `scan_truncated` plus an explicit warning in table, summary, and markdown output.
- **`.env` files are no longer auto-loaded** (trust boundary). RepoPulse scans repositories that may be untrusted, and python-dotenv's search could land inside the scanned repo (its working directory or a venv parent), letting a scanned project inject variables such as `HTTPS_PROXY` into the tool. Export `GITHUB_TOKEN` in your shell/CI or pass `--token` instead. The `python-dotenv` dependency is removed.
- **Local scans no longer claim the repository is public.** Offline scans cannot verify visibility, so `repository.private` is now `null` (rendered as "Unknown") instead of a hardcoded `false`. This changes the field's type in the JSON contract, so `schema_version` is bumped **`1.0` → `1.1`** (scan report only; comparison report stays `1.0`).

### Internal

- `mypy` is fully clean: check modules annotate `status` as the `Literal` type at first assignment; `types-requests` added to dev dependencies (#32).

## 0.3.5 - 2026-08-06

### Trust / heuristics

- **Structure:** monorepo-aware layouts (`apps/`, `packages/`, `services/`, …), higher root-clutter allowance, more known workspace/tooling root files.
- **Package scripts:** soft pass on project metadata alone; recognize task entrypoints (Makefile, tox/nox/hatch, `[project.scripts]`, …).
- **Tests:** CI workflow test steps count as a documented test command; score-13 framework path no longer nags for an extra root command.
- **Dependencies (advisory):** lockfile alone passes; Renovate accepted; dual “must have Dependabot + lockfile” nag removed.
- **Scope:** human reports (table/summary/markdown) state Python/JS-weighted content-light scope; docs updated (`README`, `USAGE`, `docs/checks.md`).
- **Release rules:** scoring/JSON stability documented in `docs/json-schema.md` and `CONTRIBUTING.md` (no silent contract or scale breaks).

### CLI reliability

- Plain formats (`json` / `markdown` / `summary` / `issues`) print without Rich markup/highlight so brackets and JSON stay intact.
- `create-issues` dry-run/created titles print as plain text so titles like `[RepoPulse] …` stay intact.

### Notes

- GitHub API rate-limit retries remain deferred (clear quota errors already).
- JSON `schema_version` stays **`1.0`** (additive docs only; no field removals).

## 0.3.4 - 2026-08-04

- Deeper **Tests** check: `noxfile.py`, `hatch.toml`, broader pyproject markers; score **13 pass** when tests + framework config exist without a separate command file.
- CONTRIBUTING / bug template: false-positive reporting guidance.
- Roadmap community notes; [docs/dogfood.md](docs/dogfood.md) score snapshot.

## 0.3.3 - 2026-08-04

- `create-issues` skips open GitHub issues with the same exact title (default); use `--no-dedupe` to force create.
- Deeper GitHub Actions check: more test/quality/setup tokens, workflow basename hints, fairer scores, gap-specific recommendations.
- License check accepts root `LICENSE.txt` / `LICENCE*` / `COPYING*`.
- Sensitive files: fixture paths under `tests/`/`examples/` warn instead of fail.
- README: broader keywords; skip low-value tech-stack nag when install+usage present.
- Structure check: recognize package layouts (not only `src/`), ignore common OSS root docs as clutter.

## 0.3.2 - 2026-08-04

- Documentation refresh: install as `repopulse-cli` for end users, full feature list (scan/ref/compare/create-issues), updated README (en/ar/es), INSTALLATION, USAGE, REQUIREMENTS, ARCHITECTURE, and publishing notes.

## 0.3.1 - 2026-08-04

- PyPI distribution name is **`repopulse-cli`** (`pip install repopulse-cli`); CLI/import remain `repopulse`.
- `repo-pulse` was rejected by PyPI as too similar to the existing unrelated package `repopulse`.

## 0.3.0 - 2026-08-04

- GitHub ref-aware scan: `/tree/<ref>`, `/releases/tag/<tag>`, and `--ref` (no local checkout required).
- Compare supports per-side refs via tree URLs or `--baseline-ref` / `--target-ref`.
- New command `repopulse create-issues` to open GitHub issues from fail/warn checks (`--dry-run` / `--yes`).
- Packaging/docs for PyPI install path (name finalized in 0.3.1 as `repopulse-cli`).

## 0.2.3 - 2026-08-04

- Packaging prep for PyPI under a non-colliding distribution name; CLI/import remain `repopulse`.
- Release workflow can publish to PyPI via Trusted Publishing when repository variable `PUBLISH_TO_PYPI=true` and the PyPI pending publisher are configured (see `docs/PUBLISHING.md`).

## 0.2.2 - 2026-08-04

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
