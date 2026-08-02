# Plan 001: Add GitHub Actions example and CI usage docs

> **Executor instructions**: Follow step by step. Run every verification. If a STOP condition hits, stop and report — do not improvise. Update your status in `plans/README.md` only if you are not worktree-isolated; otherwise report DONE in your final message.
>
> **Drift check (run first)**: `git rev-parse --short HEAD` — plan written at `bc427a8`. If HEAD differs, re-read in-scope files before editing.

## Status

- **Priority**: P1
- **Effort**: S
- **Risk**: LOW
- **Depends on**: none
- **Category**: dx | docs
- **Planned at**: commit `bc427a8`, 2026-08-02
- **Agent id**: agent-ci

## Why this matters

RepoPulse already supports `--fail-under` and config files, but maintainers still have to invent CI wiring. A copy-paste GitHub Actions example plus USAGE docs turns “nice CLI” into something teams can drop into a pipeline in minutes.

## Current state

- CLI: `repopulse/cli.py` — `scan` with `--fail-under`, `--config`, `--format`, `--quiet`, token via `--token` or `GITHUB_TOKEN`.
- Existing CI for this repo: `.github/workflows/ci.yml` runs ruff + pytest only (does NOT run RepoPulse on itself).
- Docs: `USAGE.md` has a “CI Threshold” section (read it and extend, do not replace unrelated sections).
- Examples: `examples/repopulse.yml`, `examples/sample-report.md`.
- README Quick Links include USAGE and docs; add a short CI pointer if natural.

## Commands you will need

| Purpose | Command | Expected |
|---------|---------|----------|
| Tests | `python -m pytest tests/ -q` | all pass |
| Lint | `python -m ruff check .` | exit 0 (if ruff installed) |
| Install | `pip install -e ".[dev]"` | exit 0 |

## Scope

**In scope** (ONLY these paths):

- `examples/github-action-repopulse.yml` (create)
- `USAGE.md` (add CI / GitHub Actions section)
- `README.md` and/or `README.ar.md` — one short bullet or link under Features or Usage pointing to the example (optional but preferred)
- `docs/roadmap.md` — mark “Add examples for running RepoPulse in GitHub Actions” as done or partially done with one line (optional)
- `CHANGELOG.md` under Unreleased — one bullet

**Out of scope**:

- Do NOT modify `.github/workflows/ci.yml` for this repo unless you only add an optional comment — prefer example under `examples/` so consumers copy it.
- Do NOT change Python package code under `repopulse/`.
- Do NOT publish to PyPI.
- Do NOT touch `plans/002*` or `plans/003*` scope files.

## Git workflow

- Prefer commits on current branch if worktree already branched; message style from log: short imperative, e.g. `Add GitHub Actions usage example`.
- Do NOT push or open a PR.

## Steps

### Step 1: Create example workflow

Create `examples/github-action-repopulse.yml` as a **template others copy**, with comments at the top:

```yaml
# Copy this workflow into .github/workflows/repopulse.yml in your repository.
# Requires GITHUB_TOKEN (provided by Actions) for private repos / higher rate limits.
name: RepoPulse

on:
  pull_request:
  push:
    branches: [main, master]

jobs:
  health:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install RepoPulse
        run: pip install repopulse
        # Local/dev alternative while unreleased:
        # run: pip install -e ".[dev]"
      - name: Scan this repository on GitHub
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          REPO="${{ github.repository }}"
          repopulse scan "https://github.com/${REPO}" \
            --fail-under 70 \
            --format summary \
            --quiet
```

Notes for comments in the file:

- Explain that scan targets the GitHub URL (current design), not the local checkout.
- Mention optional `--config .repopulse.yml` if present.
- Mention `pip install -e .` fallback if package not on PyPI yet.

### Step 2: Document in USAGE.md

After the existing CI Threshold section (or extend it), add:

- How to use `--fail-under` in CI
- How to set `GITHUB_TOKEN`
- Link/path to `examples/github-action-repopulse.yml`
- Example command for summary format suitable for logs

### Step 3: Changelog + light README pointer

- `CHANGELOG.md` Unreleased: “Added GitHub Actions example for CI health gates.”
- README: one line under Features or a “CI” note linking to the example.

### Step 4: Verify

Run:

```bash
python -m pytest tests/ -q
```

Expected: all pass (docs-only change should not break tests).

If ruff available: `python -m ruff check examples USAGE.md` not required; ruff is for Python.

## Test plan

- No new unit tests required (docs + example YAML only).
- Manually ensure YAML is valid structure (name/on/jobs present).

## Done criteria

- [ ] `examples/github-action-repopulse.yml` exists and is copy-paste ready
- [ ] `USAGE.md` documents CI usage and points at the example
- [ ] CHANGELOG Unreleased updated
- [ ] `pytest` still passes
- [ ] No Python source under `repopulse/` modified

## STOP conditions

- You believe the CLI cannot scan `https://github.com/${{ github.repository }}` without extra flags — verify against `repopulse/cli.py` and `url_parser.py` first; if truly blocked, stop and report.
- Another agent already created a conflicting example path — stop and report.

## Maintenance notes

- When PyPI publish lands, remove or demote the “install from source” comment.
- When local `scan .` lands, update this example.
