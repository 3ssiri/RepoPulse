# Plan 005: Issue-ready recommendations output

> Add `--format issues` that prints GitHub-issue-ready Markdown blocks from failed/warn checks.

## Status

- **Priority**: P1 | **Effort**: S | **Risk**: LOW
- **Depends on**: none  
- **Planned at**: `ec34eb0`
- **Agent**: agent-issues

## Why

Maintainers want paste-ready issue bodies from RepoPulse failures.

## Scope

- `repopulse/report.py` — add `render_issues(report: HealthReport) -> str`
- `repopulse/cli.py` — add `"issues"` to `OUTPUT_FORMATS`; wire in `render_output` only (minimal CLI change)
- `tests/test_report.py` — tests for render_issues (create file if missing; else extend)
- `USAGE.md` — document `--format issues`
- `CHANGELOG.md` — Unreleased bullet (if version section exists, put under Unreleased or 0.2.0 as appropriate)

**Out of scope**: local scan, settings/profiles, PyPI, network calls, auto-create GitHub issues via API.

## Design

`render_issues` produces multiple issue templates separated by `---` :

For each check where `status in {"fail", "warn"}` OR recommendations non-empty:

```markdown
## [RepoPulse] {check.title}: {check.status}

**Repository:** {full_name}
**Score impact:** {score}/{max_score}
**Summary:** {message}

### Action items
- {each recommendation}
  (if no recs: `- Review this check and improve the repository.`)

### Labels
`repopulse`, `health-check`, `{check.key}`
```

If nothing to report:

```markdown
No open recommendations from RepoPulse for {full_name} (score {total}/{max} — {grade}).
```

Also list at top a one-line header:

```markdown
# RepoPulse recommendations for {full_name}
Score: {total}/{max} — {grade}
```

## CLI

Only extend:

```python
OUTPUT_FORMATS = {"table", "markdown", "json", "summary", "issues"}
```

and `render_output` branch for issues → `render_issues(report)`.

Do **not** restructure `scan()` beyond what's needed. If another agent changed cli for local paths, merge carefully: preserve path/url support.

## Tests

- Unit test render_issues with sample HealthReport (fail + pass checks).
- Assert fail check appears; pass with empty recs does not generate Action section spam.
- CLI optional: monkeypatch build_health_report and invoke `--format issues`.

## Verify

```bash
python -m pytest tests/ -q
python -m ruff check repopulse/report.py repopulse/cli.py tests/test_report.py
```

## STOP

- test_report.py patterns unknown — follow test_cli/sample_report style.
- Major cli rewrite needed — only touch format list + render_output.
