# Publishing RepoPulse

## Name collision (read first)

| Role | Name |
|---|---|
| **PyPI / `pip install`** | `repopulse-cli` |
| **CLI command** | `repopulse` |
| **Python import** | `repopulse` |

The name `repopulse` on PyPI is already taken by an **unrelated** package ([pypi.org/project/repopulse](https://pypi.org/project/repopulse/) — “GitHub Intelligence Engine”, not this project).  
Hyphenated `repo-pulse` is also **rejected** by PyPI as “too similar” to that name.  
Always install ours with:

```bash
pip install repopulse-cli
repopulse --help
```

Do **not** run `pip install repopulse` expecting this tool.

---

## Status

Package is published as **`repopulse-cli`**: https://pypi.org/project/repopulse-cli/

Users install with `pip install repopulse-cli`. This section is for **maintainers** shipping new versions.

## One-shot checklist: enable PyPI Trusted Publishing

Do this **once** per PyPI project. Agents and CI must **not** invent credentials or set secrets for you.


### On PyPI

1. Account on [pypi.org](https://pypi.org/account/register/) with **2FA** enabled.
2. **Publishing** → **Add a new pending publisher**:
   - **PyPI project name:** `repopulse-cli`
   - **Owner:** `3ssiri`
   - **Repository:** `RepoPulse`
   - **Workflow name:** `release.yml` (filename under `.github/workflows/`)
   - **Environment name:** `pypi`

### On GitHub (`3ssiri/RepoPulse`)

3. **Settings → Environments** → create environment named exactly `pypi`  
   (no protection rules required for a personal project).
4. **Settings → Secrets and variables → Actions → Variables** → add:
   - Name: `PUBLISH_TO_PYPI`
   - Value: `true`

**Do not** set `PUBLISH_TO_PYPI=true` until the pending publisher (steps 1–3) is in place.  
Until the variable is set, tag releases only build and attach GitHub Release assets (safe default).

No long-lived `PYPI_API_TOKEN` secret is required. Publish uses [Trusted Publishing](https://docs.pypi.org/trusted-publishers/) (GitHub OIDC) in job `publish-pypi` of `.github/workflows/release.yml`.

### How the workflow gates publish

From `.github/workflows/release.yml`:

- Job **Publish to PyPI** runs only when:
  - ref is a tag `v*`, **and**
  - repository variable `vars.PUBLISH_TO_PYPI == 'true'`
- Uses environment `pypi` and `permissions: id-token: write`
- Publishes to https://pypi.org/project/repopulse-cli/

---

## Correct release flow (GitHub)

1. Ensure `main` is green (CI).
2. Bump version in `pyproject.toml` and `repopulse/__init__.py`, update `CHANGELOG.md`.
3. Commit and push `main`.
4. Create and push a tag:

```bash
git tag -a v0.3.3 -m "RepoPulse 0.3.3"
git push origin v0.3.3
```

5. The **Release** workflow runs only for `v*` tags:
   - ruff + pytest
   - `python -m build`
   - `twine check`
   - uploads artifacts
   - attaches wheel + sdist to the GitHub Release
   - (optional) publishes to PyPI when `PUBLISH_TO_PYPI=true` and Trusted Publisher is configured

6. Install from the GitHub Release (always works after a successful tag release):

```bash
pip install https://github.com/3ssiri/RepoPulse/releases/download/v0.3.3/repopulse_cli-0.3.3-py3-none-any.whl
```

### GitHub Action release (do this with every version bump)

The action in `action.yml` installs a **pinned** `repopulse-cli` version, and consumers reference a floating major tag (`@v1`). Both need attention at release time:

1. Bump `inputs.version.default` in `action.yml` to the new package version (same commit as the `pyproject.toml` bump).
2. After the version tag is pushed and the Release workflow is green, move the major tag:

```bash
git tag -fa v1 -m "RepoPulse action v1 -> v0.3.6"
git push origin v1 --force
```

Consumers pinned to `@v1` pick the change up automatically; consumers pinned to a full SHA are unaffected.

**Marketplace listing (one time):** open the GitHub Release for the tag, tick *Publish this Action to the GitHub Marketplace*, accept the terms, and pick the category. The listing requires `action.yml` at the repository root with `name`, `description`, and `branding` — all present.

### First / next PyPI publish

After the pending publisher and `PUBLISH_TO_PYPI` variable are set, push a new `v*` tag (or re-run a failed **Publish to PyPI** job after fixing publisher config).

Package page (after first success): https://pypi.org/project/repopulse-cli/

---

## Verify after publish

```bash
# Install from PyPI (not the foreign package named repopulse)
pip install --upgrade repopulse-cli

# CLI entry point
repopulse --help

# Import package + version
python -c "import repopulse; print(repopulse.__version__)"

# Optional: confirm index sees the project
pip index versions repopulse-cli
```

Expect the version you just tagged (e.g. `0.3.3`). If `pip install repopulse` installs something else, you hit the name collision — use `repopulse-cli`.

---

## Local smoke check (before tagging)

```bash
pip install -e ".[dev]" build twine
ruff check .
pytest -q
python -m build
python -m twine check dist/*
pip install dist/repopulse_cli-*.whl --force-reinstall
repopulse --help
python -c "import repopulse; print(repopulse.__version__)"
```

Confirm `pyproject.toml` has `name = "repopulse-cli"` and `[project.scripts]` entry `repopulse = "repopulse.cli:app"`.

---

## What was wrong before (historical)

1. **Broken Release workflow** used `if: secrets.PYPI_API_TOKEN != ''`. GitHub forbids comparing secrets in `if`, so the workflow file was invalid and produced many red **0s** runs labeled "workflow file issue".
2. **License metadata** used the old TOML table form and flooded `python -m build` with Setuptools deprecation warnings.
3. **CI ran on every branch push**, so failed historical merges polluted the Actions list.
4. **No automated attach** of wheel/sdist to the GitHub Release.
5. **PyPI name `repopulse` is taken** — distribution name is **`repopulse-cli`**; CLI/import stay **`repopulse`**.
