# RepoPulse GitHub Action

Run a repository health check in CI: score out of 100, a Markdown report in the run summary, and an optional threshold that fails the build.

```yaml
- uses: 3ssiri/RepoPulse@v1
  with:
    fail-under: "70"
```

No `actions/checkout` step is required — RepoPulse reads the repository through the GitHub API, and the default workflow token covers public repositories and rate limits.

## Quick start

Create `.github/workflows/repopulse.yml`:

```yaml
name: RepoPulse

on:
  pull_request:
  push:
    branches: [main]

jobs:
  health:
    runs-on: ubuntu-latest
    steps:
      - uses: 3ssiri/RepoPulse@v1
        with:
          fail-under: "70"
```

## Inputs

| Input | Default | Description |
|---|---|---|
| `target` | current repository | Repository URL or local path to scan. |
| `fail-under` | *(empty)* | Fail the job below this score percentage (0–100). Empty means report only. |
| `ref` | default branch | Branch, tag, or commit SHA to scan. |
| `config` | *(empty)* | Path to a `.repopulse.yml` config file in the repository. |
| `token` | `github.token` | Token used for API calls. |
| `job-summary` | `true` | Write the Markdown report to the workflow run summary. |
| `version` | pinned | Version of the `repopulse-cli` package to install; empty installs the latest. |
| `python-version` | `3.11` | Python version used to run RepoPulse. |

## Outputs

| Output | Example | Description |
|---|---|---|
| `score` | `82` | Total score. |
| `max-score` | `100` | Maximum for the applied configuration. |
| `percentage` | `82` | `score` as a percentage of `max-score`. |
| `grade` | `Good` | Excellent, Good, Fair, Weak, or Critical. |
| `truncated` | `false` | `true` when the repository was too large to list fully, so the score covers only part of it. |
| `json-report` | `/home/runner/work/_temp/repopulse-report.json` | Full JSON report on the runner. |
| `markdown-report` | `/home/runner/work/_temp/repopulse-report.md` | Markdown report on the runner. |

Outputs are published **before** the threshold gate, so a failing run still exposes the score that caused it.

## Recipes

**Report without ever failing the build** — omit `fail-under`:

```yaml
- uses: 3ssiri/RepoPulse@v1
```

**Use the score in later steps:**

```yaml
- uses: 3ssiri/RepoPulse@v1
  id: health
- run: echo "Scored ${{ steps.health.outputs.score }} (${{ steps.health.outputs.grade }})"
```

**Upload the report as a build artifact:**

```yaml
- uses: 3ssiri/RepoPulse@v1
  id: health
- uses: actions/upload-artifact@v4
  with:
    name: repopulse-report
    path: ${{ steps.health.outputs.json-report }}
```

**Scan a different repository** (for example a nightly check across projects):

```yaml
- uses: 3ssiri/RepoPulse@v1
  with:
    target: https://github.com/owner/other-repo
```

**Apply a stricter profile** from a config file in the repository:

```yaml
- uses: 3ssiri/RepoPulse@v1
  with:
    config: .repopulse.yml
    fail-under: "85"
```

Ready-made profiles live in [examples/profiles/](../examples/profiles/).

## Notes and limits

- **Scope:** heuristics are content-light and strongest for Python and JavaScript/TypeScript layouts. Treat the score as a prompt, not a verdict — see [checks.md](checks.md).
- **Very large repositories:** when the file listing cannot be completed, the action emits a warning annotation and sets `truncated` to `true`. The score then covers only the listed files.
- **Private repositories:** the default token works when the workflow runs inside the repository being scanned. Scanning a *different* private repository needs a token with read access passed via `token`.
- **Pinning:** the action pins the `repopulse-cli` version it installs, so a given action tag always behaves the same way. Override with `version` to track the latest instead.

## Security

- Inputs are passed to the shell through environment variables, never interpolated into the script body, so repository-controlled values cannot inject commands.
- The action installs a pinned release from PyPI and pins its own nested action by full commit SHA.
- RepoPulse never reads `.env` files and never prints the contents of sensitive files — only their names. See [SECURITY.md](../SECURITY.md).

## Maintainers

The action version pinned in `action.yml` (`inputs.version.default`) must be bumped with each release — see [PUBLISHING.md](PUBLISHING.md).
