# Installation Guide

This guide explains how to install RepoPulse for normal use and for development.

## Requirements

- Python 3.11 or newer.
- Git.
- Internet access to reach `api.github.com`.
- A GitHub token for private repositories or higher API limits.

## Install from PyPI (recommended after first publish)

```bash
pip install repo-pulse
```

The **PyPI project name** is `repo-pulse` because `repopulse` is already used by an unrelated package. After install, the CLI command is still:

```bash
repopulse --help
```

If the package is not on PyPI yet, use a GitHub Release wheel or the source install below.

## Install from a GitHub Release

```bash
pip install https://github.com/3ssiri/RepoPulse/releases/download/v0.2.3/repo_pulse-0.2.3-py3-none-any.whl
```

See [docs/PUBLISHING.md](docs/PUBLISHING.md) for tagging, GitHub Releases, and PyPI Trusted Publishing.

Verify:

```bash
repopulse --help
```

## Install From Source

```bash
git clone https://github.com/3ssiri/RepoPulse.git
cd RepoPulse
pip install -e .
```

Verify the command is available:

```bash
repopulse --help
```

## Development Install

```bash
pip install -e ".[dev]"
```

Or use the development requirements file:

```bash
pip install -r requirements-dev.txt
```

Run tests:

```bash
pytest
```

## Private Repositories

RepoPulse reads private repositories when a token with repository access is provided:

```bash
repopulse scan https://github.com/username/private-repo --token YOUR_GITHUB_TOKEN
```

You can also set `GITHUB_TOKEN`:

```bash
GITHUB_TOKEN=YOUR_GITHUB_TOKEN repopulse scan https://github.com/username/private-repo
```

On Windows PowerShell:

```powershell
$env:GITHUB_TOKEN="YOUR_GITHUB_TOKEN"
repopulse scan https://github.com/username/private-repo
```

## Troubleshooting

If `repopulse` is not found, confirm the package was installed in the same Python environment you are using:

```bash
python -m pip install -e .
python -m repopulse.cli --help
```

If GitHub returns rate-limit errors, set `GITHUB_TOKEN`.
