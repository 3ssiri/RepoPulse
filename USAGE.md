# Usage Guide

RepoPulse exposes two main commands:

```bash
repopulse scan <github_repo_url_or_local_path>
repopulse compare <baseline> <target>
```

## Basic Scan

```bash
repopulse scan https://github.com/psf/requests
```

This prints a Rich table with repository metadata, checks, score, grade, and recommendations.

## Local Path Scan

Scan a directory on disk without calling the GitHub API (works offline, no token, no rate limits):

```bash
repopulse scan .
repopulse scan ./my-project
repopulse scan /path/to/repo --format summary --quiet
```

When the argument is an existing directory, RepoPulse walks the tree, reads key files, and reuses the same health checks as remote scans. Git metadata (default branch, last commit date, GitHub remote) is used when available; otherwise safe defaults apply.

If the argument is not an existing directory, it is treated as a GitHub URL (same as before).

## Markdown Export

```bash
repopulse scan https://github.com/psf/requests --export report.md
```

`--export` always writes Markdown and keeps the normal terminal output.

## Output Formats

Use `--format` to choose output:

```bash
repopulse scan https://github.com/psf/requests --format table
repopulse scan https://github.com/psf/requests --format summary
repopulse scan https://github.com/psf/requests --format markdown
repopulse scan https://github.com/psf/requests --format json
repopulse scan https://github.com/psf/requests --format issues
repopulse scan . --format issues
```

Available formats:

| Format | Purpose |
|---|---|
| `table` | Human-readable terminal report. |
| `summary` | Compact output for automation. |
| `markdown` | Markdown report text. |
| `json` | Machine-readable JSON. |
| `issues` | GitHub-issue-ready Markdown blocks for fail/warn checks (paste into new issues). |

## Write Output to a File

```bash
repopulse scan https://github.com/psf/requests --format json --output report.json
repopulse scan https://github.com/psf/requests --format markdown --output report.md
```

## JSON Shortcut

```bash
repopulse scan https://github.com/psf/requests --json
```

`--json` is a shortcut for JSON output.

## Compare two scans

Diff health between two checkouts, branches, tags, or repositories. Useful for PR gates and release readiness:

```bash
# Two local checkouts (e.g. main vs PR worktree)
repopulse compare ./checkout-main ./checkout-pr

# Labels for readable output
repopulse compare ./main ./pr --baseline-label main --target-label pr-42

# Machine-readable
repopulse compare ./main ./pr --format json --output delta.json
repopulse compare ./main ./pr --format markdown --output delta.md
repopulse compare ./main ./pr --format summary --quiet

# Fail CI when health got worse
repopulse compare ./main ./pr --fail-on-regression --quiet
```

| Flag | Purpose |
|---|---|
| `--format` | `table` (default), `markdown`, `json`, or `summary`. |
| `--baseline-label` / `--target-label` | Display names in the report. |
| `--fail-on-regression` | Exit code `2` if total score dropped or any check regressed. |
| `--config` | Same YAML config applied to both sides. |
| `--token` | GitHub token when either side is a remote URL. |

Tip: check out two worktrees or clone two refs, then pass the directories to `compare`. Remote GitHub URLs compare each repo's default branch (ref-aware remote compare is on the later roadmap).

## CI Threshold

Use `--fail-under` to make the command exit with code `2` when the score is below a threshold:

```bash
repopulse scan https://github.com/username/repository --fail-under 75
```

This is useful in GitHub Actions or other CI systems.

### Using RepoPulse in GitHub Actions

Copy the ready-made workflow from [examples/github-action-repopulse.yml](examples/github-action-repopulse.yml) into:

```text
.github/workflows/repopulse.yml
```

Key points for CI:

- **`--fail-under`**: fail the job when the health score is below your gate (exit code `2`).
- **`GITHUB_TOKEN`**: set via the job environment so private repos and higher rate limits work. GitHub Actions provides `secrets.GITHUB_TOKEN` automatically; you can also pass `--token` instead of the env var.
- **Scan target**: the CLI scans a GitHub URL (API), not the runner checkout. Use `https://github.com/${{ github.repository }}` for the current repo.
- **Logs**: prefer summary output so CI logs stay compact:

```bash
repopulse scan "https://github.com/${REPO}" \
  --fail-under 70 \
  --format summary \
  --quiet
```

Optional: pass a config file if the repo has one:

```bash
repopulse scan "https://github.com/${REPO}" \
  --config .repopulse.yml \
  --fail-under 70 \
  --format summary \
  --quiet
```

Install in the workflow with `pip install repopulse`. While the package is not on PyPI yet, use `pip install -e .` (or `pip install -e ".[dev]"`) from a checkout of this project.

## Configuration File

RepoPulse reads `.repopulse.yml` from the current directory when the file exists. Use `--config` to pass a different path:

```bash
repopulse scan https://github.com/psf/requests --config examples/repopulse.yml
```

Supported keys:

| Key | Purpose |
|---|---|
| `profile` | Named preset: `strict`, `library`, `docs`, or `release`. Optional. |
| `fail_under` | Default percentage threshold used when `--fail-under` is not provided. |
| `disabled_checks` | List of check keys to exclude from the report and score. |
| `weights` | Mapping of scored check keys to custom point values. |

### Named profiles

Use a built-in profile for instant CI-friendly defaults:

```yaml
profile: strict
```

| Profile | fail_under | Focus |
|---|---:|---|
| `strict` | 85 | High bar for CI gates (tests + Actions weighted higher). |
| `library` | 75 | Packaging and tests over recent activity; `package_scripts` weight 0. |
| `docs` | 70 | Documentation-heavy repos; README weight 35; `package_scripts` weight 0. |
| `release` | 90 | Release readiness: tests, CI, and license weighted highest. |

Ready-made files: `examples/profiles/strict.yml`, `library.yml`, `docs.yml`, `release.yml`.

### Override rules (when `profile` is set)

1. Profile supplies base `weights`, `disabled_checks`, and `fail_under`.
2. Explicit `weights` merge key-by-key (your keys win; other profile weights stay).
3. Explicit `disabled_checks` **replaces** the profile list entirely.
4. Explicit `fail_under` overrides the profile threshold.

Example — strict profile with a custom README weight:

```yaml
profile: strict
weights:
  readme: 50
```

Example — fully custom config without a profile:

```yaml
fail_under: 85
disabled_checks:
  - activity
weights:
  readme: 25
  tests: 20
  github_actions: 20
```

Configs that omit `profile` behave as before (empty defaults until you set keys).

CLI `--fail-under` takes precedence over `fail_under` in the config file.

## Quiet and Verbose Modes

Quiet mode prints compact output:

```bash
repopulse scan https://github.com/psf/requests --quiet
```

Verbose mode shows all recommendations in table output:

```bash
repopulse scan https://github.com/psf/requests --verbose
```

## Private Repository Scan

```bash
repopulse scan https://github.com/username/private-repo --token YOUR_GITHUB_TOKEN
```

Or:

```bash
GITHUB_TOKEN=YOUR_GITHUB_TOKEN repopulse scan https://github.com/username/private-repo
```

### Token hygiene (important)

- Prefer environment variables or CI secrets over pasting tokens into shell history.
- Use a token with the **minimum** scope needed (private repo read; avoid admin scopes).
- Never commit tokens to the repository or put them in issue reports.
- For local offline checks of a checked-out private repo, use `repopulse scan .` — no GitHub token required.
- RepoPulse never prints sensitive file **contents**; it only reports matching file **names**.

## JSON contract

Machine-readable reports use a stable top-level `schema_version` field (currently `1.0`).

See [docs/json-schema.md](docs/json-schema.md) for the field list and compatibility rules.

## Exit Codes

| Exit Code | Meaning |
|---:|---|
| `0` | Scan completed successfully and passed any threshold. |
| `1` | Invalid input or GitHub API error. |
| `2` | Scan completed but score was below `--fail-under`. |
