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
