# Architecture

RepoPulse is intentionally small and modular. The CLI accepts a target (GitHub URL or local path), loads repository data from the API or disk, runs independent checks, scores the result, and renders output. Optional commands compare two reports or open GitHub issues.

## Data Flow (scan)

```text
User Input (URL | path | ref)
  |
  v
CLI (scan / compare / create-issues)
  |
  +-- local directory? --> local_source (walk + read files)
  |
  +-- GitHub URL? ------> url_parser (owner, repo, ref)
                              |
                              v
                         GitHubClient (repo, tree@ref, contents@ref)
  |
  v
analyzer (shared check pipeline)
  |
  v
scoring + HealthReport
  |
  v
report (table | summary | markdown | json | issues)
```

## Commands

| Command | Role |
|---|---|
| `scan` | Build one `HealthReport` and render it. |
| `compare` | Scan baseline + target, diff via `compare.build_comparison`. |
| `create-issues` | Scan once, build issue payloads, optionally POST issues. |

## Main Modules

| Module | Responsibility |
|---|---|
| `repopulse/cli.py` | Typer commands and options. |
| `repopulse/url_parser.py` | Parse github.com URLs into `(owner, repo, ref)`. |
| `repopulse/github_client.py` | GitHub API: repo, tree, file contents, create issue. |
| `repopulse/local_source.py` | Offline directory walk and git metadata. |
| `repopulse/analyzer.py` | Shared pipeline: inputs → checks → `HealthReport`. |
| `repopulse/compare.py` | Diff two `HealthReport` values. |
| `repopulse/issue_export.py` | Issue title/body/labels from checks. |
| `repopulse/models.py` | Pydantic models. |
| `repopulse/scoring.py` | Totals, grades, config weights. |
| `repopulse/settings.py` | `.repopulse.yml` and named profiles. |
| `repopulse/report.py` | All human/machine renderers. |
| `repopulse/checks/` | One independent check per file. |
| `webapp/` | Optional FastAPI + WebMCP layer (extra `web`); thin adapter over the core, not packaged. |

## Check Design

Each check should:

- Live in its own file under `repopulse/checks/`.
- Return a `CheckResult`.
- Avoid network calls.
- Avoid printing secrets or sensitive file **contents** (names only).
- Add recommendations a maintainer can act on.

Core checks contribute to the 100-point score. Advisory checks use `max_score=0` when they should guide without changing the main score.

## Packaging

| Surface | Name |
|---|---|
| PyPI distribution | `repopulse-cli` |
| Import package / CLI entry | `repopulse` |

Defined in `pyproject.toml` (`[project].name` vs `[project.scripts]`).

## Error Handling

GitHub API and network failures are wrapped in `GitHubAPIError` so the CLI shows concise messages instead of raw tracebacks.
