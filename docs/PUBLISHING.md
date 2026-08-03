# Publishing RepoPulse

## What was wrong before

1. **Broken Release workflow** used `if: secrets.PYPI_API_TOKEN != ''`. GitHub forbids comparing secrets in `if`, so the workflow file was invalid and produced many red **0s** runs labeled "workflow file issue" — including on normal branch pushes when the file was present.
2. **License metadata** used the old TOML table form and a license classifier, which floods `python -m build` with Setuptools deprecation warnings.
3. **CI ran on every branch push**, so failed historical merges polluted the Actions list.
4. **No automated attach** of wheel/sdist to the GitHub Release (manual upload only).

## Correct release flow (GitHub)

1. Ensure `main` is green (CI).
2. Bump version in `pyproject.toml` and `repopulse/__init__.py`, update `CHANGELOG.md`.
3. Commit and push `main`.
4. Create and push a tag:

```bash
git tag -a v0.2.2 -m "RepoPulse 0.2.2"
git push origin v0.2.2
```

5. The **Release** workflow runs only for `v*` tags:
   - ruff + pytest
   - `python -m build`
   - `twine check`
   - uploads artifacts
   - attaches wheel + sdist to the GitHub Release

6. Install from the release:

```bash
pip install https://github.com/3ssiri/RepoPulse/releases/download/v0.2.2/repopulse-0.2.2-py3-none-any.whl
```

## Optional: PyPI

PyPI is **not** required for GitHub Releases.

When ready:

1. Create a PyPI API token.
2. Add repository secret `PYPI_API_TOKEN` (or use Trusted Publishing).
3. After a green tag build, download artifacts and run:

```bash
twine upload dist/*
```

Or add a separate manual `workflow_dispatch` job that publishes only when you choose.

## Local smoke check

```bash
pip install -e ".[dev]" build twine
ruff check .
pytest -q
python -m build
python -m twine check dist/*
pip install dist/repopulse-*.whl --force-reinstall
repopulse --help
```
