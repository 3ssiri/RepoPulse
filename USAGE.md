# Usage Guide

RepoPulse exposes one main command:

```bash
repopulse scan <github_repo_url>
```

## Basic Scan

```bash
repopulse scan https://github.com/psf/requests
```

This prints a Rich table with repository metadata, checks, score, grade, and recommendations.

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
```

Available formats:

| Format | Purpose |
|---|---|
| `table` | Human-readable terminal report. |
| `summary` | Compact output for automation. |
| `markdown` | Markdown report text. |
| `json` | Machine-readable JSON. |

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
| `profile` | Named preset: `strict`, `library`, or `docs`. Optional. |
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

Ready-made files: `examples/profiles/strict.yml`, `library.yml`, `docs.yml`.

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

## Exit Codes

| Exit Code | Meaning |
|---:|---|
| `0` | Scan completed successfully and passed any threshold. |
| `1` | Invalid input or GitHub API error. |
| `2` | Scan completed but score was below `--fail-under`. |
