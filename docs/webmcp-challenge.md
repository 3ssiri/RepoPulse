# RepoPulse Web + WebMCP (OpenAI WebMCP Challenge)

A thin web layer over the existing RepoPulse engine. The same `HealthReport`
and `ComparisonReport` the CLI produces are served over HTTP, and the same
functions that drive the visible dashboard are registered as WebMCP tools —
so a human and an agent always share the same application state.

## Architecture

```text
Browser (index.html + app.js, vanilla JS)
  |  fetch()                      |  document.modelContext.registerTool()
  v                               v
FastAPI app (webapp/app.py)  <----+
  |  parse_github_url → GitHubClient → build_health_report / build_comparison
  v
repopulse engine (unchanged core)
```

- `webapp/` is a **top-level adapter**, outside the `repopulse` package. The
  PyPI distribution (`repopulse-cli`) does not include it and does not depend
  on FastAPI.
- The web layer contains no business logic; it parses, validates, delegates
  to the core, and maps errors.
- Frontend state (`state.currentReport`, `state.currentComparison`) is the
  single source of truth for both the UI and the WebMCP tools. The Scan
  button and `scan_repository` call the same `scanRepository()`; the Compare
  button and `compare_refs` call the same `compareRefs()`.

## How to run

```bash
pip install -e ".[dev,web]"
uvicorn webapp.app:app --host 127.0.0.1 --port 8000 --reload
```

Open http://127.0.0.1:8000. Optional: set `GITHUB_TOKEN` in the server
environment to raise GitHub rate limits. The token is server-side only —
it never appears in HTML, JS, responses, or error messages.

## API

| Endpoint | Body | Response |
|---|---|---|
| `GET /api/health` | — | `{"status","service","version"}` (no GitHub request) |
| `POST /api/scan` | `{"repository_url", "ref"?}` | `HealthReport.model_dump()` |
| `POST /api/compare` | `{"repository_url", "baseline_ref", "target_ref"}` | `ComparisonReport.model_dump()` |

Validation and precedence:

- Only `github.com` URLs are accepted, exclusively via
  `repopulse.url_parser.parse_github_url` (SSRF boundary).
- `repository_url` max 512 chars; refs max 256 chars.
- If the URL embeds a ref (`/tree/<ref>`) and the body also has `ref`, the
  body `ref` wins.

Error contract — `{"detail": {"code", "message"}}`, no tracebacks, no raw
GitHub payloads, no tokens:

| Code | HTTP |
|---|---|
| `invalid_repository_url` | 400 |
| `invalid_ref` | 400 |
| `private_repository_not_supported` | 403 |
| `repository_not_found` / `ref_not_found` | 404 |
| `github_rate_limited` | 429 |
| `github_unavailable` | 502 / 503 |
| `internal_error` | 500 |

Note: the core client collapses "repo missing" and "private repo without a
token" into one 404; they are indistinguishable without credentials.

## WebMCP tools

Registered via `document.modelContext.registerTool()` (imperative API,
current W3C WebMCP draft) with `annotations: {readOnlyHint: true,
untrustedContentHint: true}`. WebMCP is progressive enhancement: without
`document.modelContext` the page works normally and shows
"WebMCP Unavailable".

| Tool | Input | Behavior |
|---|---|---|
| `scan_repository` | `repository_url`, `ref?` | Runs the shared scan path, updates the dashboard, returns the report summary. |
| `get_attention_items` | `{}` | FAIL then WARN checks from the **current** report; no new GitHub request. |
| `get_check_details` | `check_key` | One check from the current report; returns available keys on a miss. |
| `compare_refs` | `baseline_ref`, `target_ref` | Runs the shared compare path for the currently scanned repository, updates the dashboard. |

All four are read-only against GitHub. Tool execution receives an
`AbortSignal` (per the spec's `ToolExecuteCallbackOptions`) which is forwarded
to `fetch`, so agent-cancelled calls abort the HTTP request and reset the
loading state.

## Security boundaries

- **Public repositories only.** If a server-side token can see a private
  repo, the repo is rejected with 403 *before* any tree/file reads.
- **No tokens from the client.** No PAT input, no token in request bodies;
  `GITHUB_TOKEN` is read server-side only.
- **XSS:** all GitHub-derived data renders via `textContent`/`createElement`;
  no `innerHTML`, no Markdown rendering, no raw README display.
- **Prompt injection:** WebMCP results contain RepoPulse analysis results
  only — never raw repository content; tools are static and never derived
  from repository data.
- **SSRF:** repository URLs pass only through `parse_github_url`
  (`github.com` only); the client talks only to `api.github.com`.
- **Headers:** `X-Content-Type-Options: nosniff`, `Referrer-Policy:
  no-referrer`. Same-origin frontend/API; no CORS, no framing rules added
  (WebMCP compatibility untested for those).

## Testing

`tests/test_webapp.py` covers: health, index, error mapping
(invalid URL/host, 404 repo vs ref, rate limit, network failure, 502),
ref precedence, `scan_truncated` passthrough, private-repo rejection,
token/traceback leak checks, the compare contract, whitespace/blank compare
refs, overlong URL-derived refs, reused GitHub metadata, stale
scan/compare results, Compare-before-Scan UI errors, and partial WebMCP
registration abort. All network and core calls are mocked — tests never
touch real GitHub.

## Demo flow

Using `https://github.com/3ssiri/RepoPulse` (tags `v0.3.5`/`v0.3.6` exist):

1. "Scan this repository and tell me the three things that deserve the most
   attention before a release." → `scan_repository` → `get_attention_items`
2. "Explain the most important warning and what I should verify manually."
   → `get_check_details`
3. "Compare v0.3.5 with v0.3.6 and tell me whether repository health
   regressed." → `compare_refs`

## Known limitations / future work

- Public github.com repositories only; no OAuth, accounts, or private repos.
- No caching, history, or persistence; each scan hits the GitHub API live.
- Repo-404 vs private-repo is indistinguishable without a token.
- Deferred: OAuth/private repos, saved history, issue creation via WebMCP,
  GitLab/Bitbucket, background jobs, caching.
