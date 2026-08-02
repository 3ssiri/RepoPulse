# Plan 006: Local path scan (`repopulse scan .`)

> Support scanning a local directory without GitHub API when target is a filesystem path.

## Status

- **Priority**: P1 | **Effort**: L | **Risk**: MED
- **Depends on**: none (merge carefully with cli changes from agent-issues)
- **Planned at**: `ec34eb0`
- **Agent**: agent-local

## Why

Local scan avoids rate limits, works offline, and enables pre-push checks on uncommitted trees.

## Scope

- **Create** `repopulse/local_source.py` — walk directory → FileItem list; read file text; build RepositoryInfo
- **Modify** `repopulse/analyzer.py` — extract check-running into shared function used by GitHub and local paths; e.g. `build_report_from_files(repository, files, content_loader, config)` or `build_local_health_report(path, config)`
- **Modify** `repopulse/cli.py` — if argument is existing path (`.` or `./foo` or absolute), use local scan; else parse as GitHub URL
- **Tests**: `tests/test_local_source.py` and/or extend test_cli / test analyzer
- **Docs**: USAGE.md, README features, CHANGELOG, examples optional
- Update `examples/github-action-repopulse.yml` comment only if needed (Actions still URL-based is fine)

**Out of scope**: PyPI, issues format (other agent), rewriting all checks, reading binary secrets contents into recommendations (still don't print secrets — only pass content to checks that already use content for readme/gitignore/etc.; sensitive_files check remains name-only).

## Design details

### Detect local vs remote in CLI

```python
target = url  # existing param name; help text: "GitHub URL or local path"
path = Path(target)
if path.exists() and path.is_dir():
    report = build_local_health_report(path.resolve(), scan_config)
else:
    owner, repo = parse_github_url(target)
    report = build_health_report(...)
```

Update typer help for the first argument to mention local path.

### local_source.py

```python
IGNORE_DIRS = {".git", ".hg", ".svn", "node_modules", ".venv", "venv", "__pycache__", ".tox", ".mypy_cache", ".ruff_cache", "dist", "build", ".eggs"}

def iter_local_files(root: Path) -> list[FileItem]:
    # relative posix paths, type blob for files, tree optional
    # skip IGNORE_DIRS
    # cap total files at e.g. 5000 to avoid huge monorepos — if exceeded, still return first N and OK

def read_local_text(root: Path, rel_path: str, max_bytes: int = 200_000) -> str | None:
    # read utf-8 ignore errors; skip if too large or not a file

def repository_info_from_path(root: Path) -> RepositoryInfo:
    # name = root.name
    # full_name = f"local/{name}" or try git remote get-url origin for owner/repo
    # url = root.as_uri() or github url if remote is github
    # private=False, stars=0, forks=0, open_issues=0
    # default_branch: git rev-parse --abbrev-ref HEAD or "main"
    # last_pushed_at: git log -1 --format=%cI or None
    # Use subprocess with timeout for git; if git missing, defaults OK
```

### analyzer.py refactor

Keep `build_health_report` working as today.

Add:

```python
def build_health_report_from_inputs(
    repository: RepositoryInfo,
    files: list[FileItem],
    *,
    readme_content: str | None,
    gitignore_content: str | None,
    package_content: str | None,
    pyproject_content: str | None,
    workflow_contents: dict[str, str],
    config: RepoPulseConfig | None = None,
) -> HealthReport:
    # existing checks list + scoring — shared body
```

Then GitHub builder fetches then calls this; local builder reads then calls this.

```python
def build_local_health_report(root: Path, config: RepoPulseConfig | None = None) -> HealthReport:
    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"Not a directory: {root}")
    files = iter_local_files(root)
    repository = repository_info_from_path(root)
    # find files + read contents via read_local_text
    return build_health_report_from_inputs(...)
```

### Activity check for local

If git last commit date available, activity works; else score may be low — acceptable.

### Tests

- tmp_path with README.md, LICENSE, .gitignore, tests/test_x.py, pyproject.toml → local report score > 0
- CLI: `scan` with str(tmp_path) works without network (monkeypatch not needed if pure local)
- Existing URL tests still pass

### Security

- Do not print file contents of `.env` in recommendations
- Do not follow symlinks outside root if easy (`follow_symlinks=False` on walk)

## Verify

```bash
python -m pytest tests/ -q
python -m ruff check repopulse/local_source.py repopulse/analyzer.py repopulse/cli.py tests/
repopulse scan .
```

Expect local scan prints report for this repo without GitHub token.

## STOP

- Need to change check contracts — stop
- Cannot detect path vs URL reliably on Windows — use `Path.exists()` for dirs only; bare `owner/repo` remains invalid URL (existing behavior)
- Merge conflict with issues format in cli — support both `"issues"` in OUTPUT_FORMATS and local paths

## Done criteria

- [ ] `repopulse scan .` works offline
- [ ] URL scan still works
- [ ] Shared analyzer path for checks
- [ ] Tests for local tree
- [ ] Docs updated
