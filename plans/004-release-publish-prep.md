# Plan 004: Release and publish readiness (0.2.0)

> Execute fully. Do not push to PyPI (no token assumed). Prepare GitHub release workflow + version bump + docs. Verify `python -m build` if build package installable.

## Status

- **Priority**: P1 | **Effort**: S–M | **Risk**: LOW
- **Depends on**: none
- **Planned at**: `ec34eb0`
- **Agent**: agent-publish

## Why

Repo is installable from source only. Maintainers need versioned release machinery and docs before `pip install repopulse` works on PyPI.

## Scope (ONLY)

- `pyproject.toml` — bump `version` to `0.2.0`
- `CHANGELOG.md` — move Unreleased bullets for shipped features into `## 0.2.0 - 2026-08-02` (use today's date), keep Unreleased for future
- `.github/workflows/release.yml` — on tag `v*` or `workflow_dispatch`: build sdist/wheel, upload artifacts; optional publish job that only runs if `PYPI_API_TOKEN` secret exists (use `pypa/gh-action-pypi-publish` with `if: secrets.PYPI_API_TOKEN != ''` or separate manual job)
- `INSTALLATION.md` — section "Install from PyPI" (note: available after first publish) + keep source install
- `README.md` — one line install from PyPI when published
- `docs/roadmap.md` — mark publish item partially done if appropriate
- Optional: add `build` to dev optional-deps in pyproject

**Out of scope**: actual `twine upload`, changing check logic, local scan, issues format, force-push.

## Steps

1. Bump version in pyproject to 0.2.0
2. Write release.yml
3. Update CHANGELOG structure for 0.2.0 including prior Unreleased feature bullets (profiles, deeper checks, CI example) plus note "release packaging prep"
4. Docs INSTALLATION/README
5. Verify:
   ```bash
   pip install -e ".[dev]"
   pip install build
   python -m build
   python -m pytest tests/ -q
   ```
   Expect: dist/*.whl and dist/*.tar.gz created; tests pass.

## Done criteria

- [ ] version 0.2.0
- [ ] release workflow present
- [ ] build succeeds
- [ ] pytest green
- [ ] no check/local/issues code changes

## STOP

- Cannot install `build` — document and still leave workflow.
- Conflicting version already 0.2.0 — keep and only add workflow/docs.
