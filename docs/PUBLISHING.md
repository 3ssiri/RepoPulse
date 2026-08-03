# Publishing RepoPulse

## What was wrong before

1. **Broken Release workflow** used `if: secrets.PYPI_API_TOKEN != ''`. GitHub forbids comparing secrets in `if`, so the workflow file was invalid and produced many red **0s** runs labeled "workflow file issue".
2. **License metadata** used the old TOML table form and flooded `python -m build` with Setuptools deprecation warnings.
3. **CI ran on every branch push**, so failed historical merges polluted the Actions list.
4. **No automated attach** of wheel/sdist to the GitHub Release.
5. **PyPI name `repopulse` is taken** by an unrelated project ([pypi.org/project/repopulse](https://pypi.org/project/repopulse/) — “GitHub Intelligence Engine”, author Manjunath, 0.6.0). Our distribution name is **`repo-pulse`**. The import package and CLI command stay **`repopulse`**.

## Correct release flow (GitHub)

1. Ensure `main` is green (CI).
2. Bump version in `pyproject.toml` and `repopulse/__init__.py`, update `CHANGELOG.md`.
3. Commit and push `main`.
4. Create and push a tag:

```bash
git tag -a v0.2.3 -m "RepoPulse 0.2.3"
git push origin v0.2.3
```

5. The **Release** workflow runs only for `v*` tags:
   - ruff + pytest
   - `python -m build`
   - `twine check`
   - uploads artifacts
   - attaches wheel + sdist to the GitHub Release
   - (optional) publishes to PyPI when enabled

6. Install from the release:

```bash
pip install https://github.com/3ssiri/RepoPulse/releases/download/v0.2.3/repo_pulse-0.2.3-py3-none-any.whl
```

## PyPI (`repo-pulse`)

Install (after first successful publish):

```bash
pip install repo-pulse
repopulse --help
```

### Why Trusted Publishing (no long-lived token)

We use [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/) with GitHub OIDC. No `PYPI_API_TOKEN` secret is required once configured.

### One-time setup (you must do this once)

1. Create a free account on [pypi.org](https://pypi.org/account/register/).
2. Enable 2FA on the account (required for publishing).
3. Open **Publishing** → **Add a new pending publisher**:
   - **PyPI project name:** `repo-pulse`
   - **Owner:** `3ssiri`
   - **Repository:** `RepoPulse`
   - **Workflow name:** `release.yml`
   - **Environment name:** `pypi`
4. In the GitHub repo **Settings → Environments**, create environment `pypi` (no protection rules required for a personal project).
5. In the GitHub repo **Settings → Secrets and variables → Actions → Variables**, add:
   - Name: `PUBLISH_TO_PYPI`
   - Value: `true`

Until step 5 is done, tag releases only build GitHub assets (safe default).

### First publish

After the pending publisher and variable are set:

```bash
git tag -a v0.2.3 -m "RepoPulse 0.2.3"
git push origin v0.2.3
```

Or re-run a failed **Publish to PyPI** job after fixing publisher config.

Package page: https://pypi.org/project/repo-pulse/

## Local smoke check

```bash
pip install -e ".[dev]" build twine
ruff check .
pytest -q
python -m build
python -m twine check dist/*
pip install dist/repo_pulse-*.whl --force-reinstall
repopulse --help
```
