# Installation Guide

How to install RepoPulse for end users, CI, and development.

## Requirements

- **Python 3.11 or newer**
- **Git** (for source install or local scans that enrich git metadata)
- **Internet** to reach `api.github.com` for remote scans and PyPI install
- **GitHub token** for private repositories, higher API rate limits, or creating issues (`create-issues --yes`)

Local-only scans (`repopulse scan .`) work offline after the package is installed.

---

## Names (read this first)

| Role | Correct value |
|---|---|
| **pip package** | `repopulse-cli` |
| **CLI command** | `repopulse` |
| **Python import** | `import repopulse` |

```bash
# Correct
pip install repopulse-cli

# Wrong — unrelated package on PyPI
pip install repopulse
```

The project name on GitHub is **RepoPulse**; the PyPI distribution is **`repopulse-cli`** because the shorter name `repopulse` (and similar names like `repo-pulse`) are already taken or blocked.

---

## Install for end users (recommended)

### From PyPI

```bash
pip install repopulse-cli
repopulse --help
```

Confirm version:

```bash
python -c "import repopulse; print(repopulse.__version__)"
# or
pip show repopulse-cli
```

### Upgrade

```bash
pip install -U repopulse-cli
```

### Isolated virtual environment (recommended)

Avoids conflicts with other tools that pin different versions of `requests`, `rich`, etc.

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -U pip
pip install repopulse-cli
repopulse --help
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install repopulse-cli
repopulse --help
```

### From a GitHub Release wheel

Useful if PyPI is blocked or you want a specific release asset:

```bash
pip install https://github.com/3ssiri/RepoPulse/releases/download/v0.3.6/repopulse_cli-0.3.6-py3-none-any.whl
```

Browse all releases: https://github.com/3ssiri/RepoPulse/releases

---

## Install for contributors (from source)

```bash
git clone https://github.com/3ssiri/RepoPulse.git
cd RepoPulse
python -m venv .venv
# activate .venv (see above)
pip install -U pip
pip install -e ".[dev]"
pytest
repopulse --help
```

Or without a venv:

```bash
pip install -e .
pip install -e ".[dev]"   # tests, ruff, mypy
```

Alternatively:

```bash
pip install -r requirements-dev.txt
```

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Install in CI / GitHub Actions

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: "3.11"
- run: pip install repopulse-cli
- run: |
    repopulse scan "https://github.com/${{ github.repository }}" \
      --fail-under 70 \
      --format summary \
      --quiet
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

Ready-made workflow: [examples/github-action-repopulse.yml](examples/github-action-repopulse.yml).

More CI patterns: [USAGE.md](USAGE.md#using-repopulse-in-github-actions).

---

## After install — try it

```bash
# This project (or any folder)
repopulse scan .

# A public repository
repopulse scan https://github.com/psf/requests --format summary

# Branch without cloning
repopulse scan https://github.com/psf/requests/tree/main

# Compare two refs
repopulse compare \
  https://github.com/3ssiri/RepoPulse/tree/main \
  https://github.com/3ssiri/RepoPulse/releases/tag/v0.3.3 \
  --format summary
```

Full command reference: [USAGE.md](USAGE.md).

---

## Private repositories

```bash
repopulse scan https://github.com/username/private-repo --token YOUR_GITHUB_TOKEN
```

Or environment variable:

```bash
# bash / zsh
export GITHUB_TOKEN=YOUR_GITHUB_TOKEN
repopulse scan https://github.com/username/private-repo
```

```powershell
# PowerShell
$env:GITHUB_TOKEN="YOUR_GITHUB_TOKEN"
repopulse scan https://github.com/username/private-repo
```

Token tips: [USAGE.md — Token hygiene](USAGE.md#token-hygiene-important).

For a private repo already checked out on disk:

```bash
repopulse scan .
```

No token required for that path.

---

## Troubleshooting

### `repopulse` is not found

The package may be installed in a different Python than the one on your `PATH`:

```bash
python -m pip install repopulse-cli
python -m repopulse.cli --help
```

On Windows, ensure Scripts is on PATH, or use the active venv’s `repopulse.exe`.

### Wrong package installed

If `pip install repopulse` worked but the CLI is not this project:

```bash
pip uninstall repopulse
pip install repopulse-cli
```

### GitHub rate limit

```text
GitHub API rate limit exceeded
```

Set `GITHUB_TOKEN` (or pass `--token`). Authenticated requests have a much higher limit.

### Dependency conflicts with other tools

Use a dedicated virtual environment (see above) instead of installing into a global Python that other apps share.

### Verify package metadata

```bash
pip show repopulse-cli
python -c "import repopulse; print(repopulse.__version__)"
```

---

## Maintainers: publishing new versions

GitHub Releases and optional PyPI uploads are documented in [docs/PUBLISHING.md](docs/PUBLISHING.md).

End users only need:

```bash
pip install -U repopulse-cli
```
