# Plan 010 — Create GitHub issues from recommendations

**Status:** DONE  
**Priority:** P1  
**Agent:** agent-issues  
**Depends on:** —

## Goal

Turn fail/warn recommendations into real GitHub issues via the API (no manual paste).

## Delivered (required)

### Pure module `repopulse/issue_export.py` (new)

- `issue_payloads_from_report(report: HealthReport, *, labels: list[str] | None = None, statuses: set[str] | None = None) -> list[dict]`
  - One payload per actionable check (same selection spirit as `render_issues`: fail/warn or has recommendations).
  - Each payload: `{"title": str, "body": str, "labels": list[str]}`.
  - Title format: `[RepoPulse] {check.title}: {status}` (keep short; truncate if needed ~80 chars).
  - Body: Markdown action items (reuse logic from `render_issues` blocks — extract shared helper in `report.py` if cleaner).
  - Default labels: `["repopulse", "health-check", check.key]` plus any user labels.
- `filter` by statuses if provided (default fail+warn; include pure-recommendation-only checks when status is pass but has recs — match current `render_issues`).

### GitHub client create issue (`repopulse/github_client.py` only if not conflicting)

- Prefer putting HTTP create in this module if agent-ref is not owning client heavily; otherwise implement `create_issue` in `issue_export.py` using requests with the same headers pattern **or** add `GitHubClient.create_issue(owner, repo, title, body, labels)`.

**Coordination:** Prefer `GitHubClient.create_issue` method. If agent-ref is editing `github_client.py`, add only the new method at the end of the class in a way that merges cleanly.

### CLI command

- `repopulse create-issues <github-url-or-path>`
  - Options:
    - `--token`
    - `--config`
    - `--dry-run` (print titles/bodies, create nothing)
    - `--label` (repeatable, extra labels)
    - `--statuses` default `fail,warn` (comma-separated); if empty use fail+warn; document that recommendation-only pass checks still included when matching `render_issues` OR only status-filter strictly — **choose: statuses filter on check.status; default fail,warn; do not open for pure pass without those statuses**.
    - `--yes` required for real creates (safety); without `--yes` and without `--dry-run`, error asking for one of them.
  - Exit 0 on success; print count created.
  - Exit 1 on API/URL errors.

### Tests

- Unit tests for `issue_payloads_from_report` (counts, titles, labels, status filter).
- CLI dry-run test with monkeypatched scan + no network.
- CLI create test monkeypatches `create_issue` and asserts call count with `--yes`.

## Out of scope

- Deduplicating against existing open issues (nice-to-have later).
- Editing existing issues.

## Done when

- `pytest` covers the module + CLI dry-run/create paths.
- `repopulse create-issues --help` works.
