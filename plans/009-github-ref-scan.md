# Plan 009 — GitHub ref-aware scan & compare

**Status:** DONE  
**Priority:** P1  
**Agent:** agent-ref  
**Depends on:** —

## Goal

Scan (and therefore compare) a specific GitHub branch or tag without a local checkout.

## Delivered (required)

### URL / target parsing (`repopulse/url_parser.py`)

- Extend parsing so callers get `(owner, repo, ref | None)`.
- Supported forms:
  - `https://github.com/owner/repo`
  - `https://github.com/owner/repo.git`
  - `https://github.com/owner/repo/tree/<ref>` (ref may contain `/`, e.g. `feature/foo`)
  - `https://github.com/owner/repo/releases/tag/<tag>`
- Keep raising clear `ValueError` for non-github hosts.
- Add pure helper if useful: `parse_github_target(target: str) -> tuple[str, str, str | None]` and keep `parse_github_url` as a thin wrapper returning only owner/repo for backward compatibility **or** update all call sites (prefer updating call sites + tests).

### GitHub client (`repopulse/github_client.py`)

- `get_tree(owner, repo, ref)` already takes a ref — ensure errors mention the ref.
- `get_file_content(owner, repo, path, ref: str | None = None)` — when `ref` is set, request with `?ref=<ref>`.

### Analyzer (`repopulse/analyzer.py`)

- `build_health_report(client, owner, repo, config=None, ref: str | None = None)`:
  - Resolve tree ref = `ref or repository.default_branch`.
  - Load file contents with the same ref.
  - When an explicit `ref` is used, set `repository.default_branch` to that ref so reports/labels show which ref was scanned (document this in a short comment).

### CLI wiring (if this agent owns it)

- `scan_target` / `scan` / `compare`: accept optional `--ref` **or** parse ref from URL.
- Prefer URL-embedded ref as primary; optional `--ref` overrides URL ref when both set.
- Progress text should show `owner/repo@ref` when ref is present.

### Tests

- `tests/test_url_parser.py` — tree URL, nested branch, tag URL, plain URL (ref None).
- `tests/test_github_client.py` — `get_file_content` includes `ref` query when provided (mock requests).
- `tests/test_cli.py` or analyzer tests — `build_health_report` passes ref to tree/content (monkeypatch client).

## Out of scope

- Creating GitHub issues (plan 010).
- PyPI (plan 011).
- Cloning git locally.

## Done when

- Full `pytest` green for new tests.
- Compare can take two GitHub URLs with different `/tree/` refs without local paths.
