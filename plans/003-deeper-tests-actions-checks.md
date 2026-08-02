# Plan 003: Deeper tests and GitHub Actions checks

> **Executor instructions**: Follow step by step. Keep checks pure (no network). Preserve sensitive-file safety rules (not in your files). Report DONE with test counts.
>
> **Drift check**: planned at `bc427a8`. Re-read both check modules before editing.

## Status

- **Priority**: P1
- **Effort**: M
- **Risk**: MED (score changes may affect default grades for same repos)
- **Depends on**: none
- **Category**: direction | tests
- **Planned at**: commit `bc427a8`, 2026-08-02
- **Agent id**: agent-checks

## Why this matters

`tests` and `github_actions` are high-weight (15 each) but shallow: directory names and keyword presence. Slightly deeper heuristics make the score more trustworthy without turning RepoPulse into a full static analyzer.

## Current state

### tests_check.py

- Detects dirs: `tests/`, `test/`, `__tests__/`
- Detects files: `test_*`, `*.test.*`, `*.spec.*`
- Node: `package.json` scripts.test
- Python: `pytest` string or `[tool.pytest.ini_options]` in pyproject
- Scores: 15 / 12 / 7 / 0

### actions_check.py

- Requires workflows under `.github/workflows/`
- Signals in names+content: ci/test/pytest/npm test/unittest → “ci”
- lint/ruff/flake8/eslint/build/mypy → “quality”
- Scores: 15 if both, 12 if ci only, 8 if workflows but neither, 0 if none

### Conventions

- Each check returns `CheckResult` with stable `key` (`tests`, `github_actions`).
- No network inside checks.
- Tests live in `tests/test_checks.py` using helper `item(path)`.

## Commands you will need

| Purpose | Command | Expected |
|---------|---------|----------|
| Install | `pip install -e ".[dev]"` | exit 0 |
| Check tests | `python -m pytest tests/test_checks.py -q` | all pass |
| Full suite | `python -m pytest tests/ -q` | all pass |
| Lint | `python -m ruff check repopulse/checks tests/test_checks.py` | exit 0 |

## Scope

**In scope**:

- `repopulse/checks/tests_check.py`
- `repopulse/checks/actions_check.py`
- `tests/test_checks.py` (add/update tests)
- `docs/checks.md` (update scoring notes for these two checks)
- `CHANGELOG.md` Unreleased bullet

**Out of scope**:

- `settings.py` / profiles (agent-profiles)
- CI example YAML (agent-ci)
- Other checks (readme, security, etc.)
- Changing default `max_score` totals away from 15 unless unavoidable — **keep max_score=15** for both.

## Design (implement exactly)

### A) tests_check — framework awareness (still content-light)

Add detection helpers (private functions OK):

1. **Python frameworks** (from pyproject text lowercased and/or file tree):
   - pytest: existing signals + `pytest.ini` / `conftest.py` presence in tree
   - unittest: files matching `*_test.py` classic pattern OR `unittest` in pyproject deps (optional light)
   - Prefer: `conftest.py` or `pytest.ini` or `tox.ini` with pytest → strengthens “has test command/setup”

2. **JS frameworks** (from package.json scripts/devDependencies if parsed):
   - Use existing `parse_json_content`
   - Detect test runners in `scripts.test` or deps keys: `jest`, `vitest`, `mocha`, `ava`, `node:test`
   - File patterns already cover `.test.` / `.spec.`

3. **Scoring refinement** (keep max 15):

| Condition | Score |
|-----------|------:|
| (test dir or test files) AND test command AND framework signal | 15 |
| (test dir or test files) AND test command | 15 (unchanged — framework optional boost only for message) |
| test dir AND test files, no command | 12 |
| only dir or only files | 7 |
| only framework config without files (e.g. pytest in pyproject but no tests) | 4 (new) |
| nothing | 0 |

Messages should mention detected framework when known, e.g. `Tests (pytest) and a test command were detected.`

Recommendations stay actionable: “Add automated tests…”, “Wire pytest into CI…”, etc.

**Do not break** existing tests:

- `test_tests_check_scores_python_pytest_configuration` expects score 15 — must still pass.

Add new tests for:

- vitest/jest via package.json
- conftest.py / pytest.ini signal
- score 4 path if you implement it
- unittest-style `test_foo.py` already covered by `test_` prefix

### B) actions_check — real CI substance

Keep max_score 15. Improve content signals:

1. **Has workflows** (required)
2. **Runs tests**: tokens expanded:
   - `pytest`, `python -m pytest`, `npm test`, `npm run test`, `pnpm test`, `yarn test`, `vitest`, `jest`, `cargo test`, `go test`, `unittest`
3. **Runs quality**: `ruff`, `eslint`, `flake8`, `mypy`, `lint`, `prettier`, `black`, `format`
4. **Install/setup present** (light): `actions/setup-python`, `actions/setup-node`, `pip install`, `npm ci`, `pnpm install`
5. **Triggers on PR or push** (from content): `pull_request`, `push:`

Scoring proposal:

| Condition | Score |
|-----------|------:|
| workflows + tests + quality | 15 |
| workflows + tests, no quality | 12 |
| workflows + quality only | 10 |
| workflows only (no test/quality signal) | 6 |
| no workflows | 0 |

Status:

- pass if score >= 12
- warn if 1–11
- fail if 0

Update message to briefly list what was detected (“tests + lint”).

**Must keep** existing `test_actions_check_reads_workflow_content` passing (pytest + ruff → 15).

Add tests for:

- workflows only → score 6
- tests without quality → 12
- quality only → 10

## Steps

### Step 1: Expand tests_check with helpers + tests

### Step 2: Expand actions_check with refined scoring + tests

### Step 3: Update docs/checks.md tables/notes for these checks

### Step 4: CHANGELOG + full pytest + ruff

## Test plan

- Extend `tests/test_checks.py` following `item()` helper pattern.
- Run full suite — other modules may import these checks only via analyzer (no snapshot of scores elsewhere expected).

```bash
python -m pytest tests/ -q
python -m ruff check repopulse/checks/tests_check.py repopulse/checks/actions_check.py tests/test_checks.py
```

## Done criteria

- [ ] Deeper heuristics implemented without network I/O
- [ ] `max_score` remains 15 for both checks
- [ ] Existing related tests still pass
- [ ] At least 4 new assertions/tests covering new branches
- [ ] docs/checks.md reflects new behavior
- [ ] CHANGELOG updated
- [ ] Full pytest green

## STOP conditions

- Existing tests fail and fixing them requires changing max_score totals or other checks’ keys — report.
- You need analyzer.py changes to pass extra data — only do so if absolutely required; prefer deriving from existing file list + contents already passed in.
- Conflict with simultaneous edits on same files — report.

## Maintenance notes

- Keyword lists will rot; keep them small and documented in module constants at top of each file.
- When local scan lands, these checks should still work on the same FileItem + content inputs.
