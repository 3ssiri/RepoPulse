# Plan 002: Named scoring profiles in config

> **Executor instructions**: Follow step by step. Verify after each step. STOP conditions are hard stops. Report DONE with files changed and test output summary.
>
> **Drift check**: planned at `bc427a8`. Re-read `repopulse/settings.py` and `repopulse/scoring.py` before editing.

## Status

- **Priority**: P1
- **Effort**: M
- **Risk**: LOW–MED
- **Depends on**: none
- **Category**: direction | dx
- **Planned at**: commit `bc427a8`, 2026-08-02
- **Agent id**: agent-profiles

## Why this matters

Users can already set custom `weights` and `disabled_checks` in `.repopulse.yml`, but they must invent sensible presets. Named profiles (`strict`, `library`, `docs`) make CI adoption instant and match the project roadmap (“named profiles for strict CI, library projects, and documentation-heavy repositories”).

## Current state

`repopulse/settings.py`:

```python
class RepoPulseConfig(BaseModel):
    disabled_checks: list[str] = Field(default_factory=list)
    weights: dict[str, int] = Field(default_factory=dict)
    fail_under: int | None = Field(default=None, ge=0, le=100)
```

`load_config` reads YAML and validates with Pydantic.

Check keys used in code (must match profile weights keys):

- `readme`, `license`, `gitignore`, `tests`, `github_actions`, `activity`, `sensitive_files`, `structure`, `package_scripts`
- Advisory (max_score 0): `dependencies`, `security` — may appear in disabled list but not as scored weights

`apply_score_config` in `repopulse/scoring.py` applies `disabled_checks` and `weights` by `check.key.lower()`.

`config_to_public_dict` dumps non-empty config into the report.

Exemplar tests: `tests/test_settings.py`.

Example config: `examples/repopulse.yml`.

## Commands you will need

| Purpose | Command | Expected |
|---------|---------|----------|
| Install | `pip install -e ".[dev]"` | exit 0 |
| Tests | `python -m pytest tests/ -q` | all pass |
| Settings tests | `python -m pytest tests/test_settings.py -q` | all pass |
| Lint | `python -m ruff check repopulse tests` | exit 0 |

## Scope

**In scope**:

- `repopulse/settings.py` — add `profile` field + built-in profile definitions + merge logic
- `tests/test_settings.py` — new tests
- `examples/repopulse.yml` and/or new files:
  - `examples/profiles/strict.yml`
  - `examples/profiles/library.yml`
  - `examples/profiles/docs.yml`
- `docs/checks.md` — short “Profiles” subsection
- `USAGE.md` — how to set `profile:`
- `CHANGELOG.md` Unreleased bullet
- Optionally expose applied profile name in `config_to_public_dict` via including `profile` when set

**Out of scope**:

- Do NOT change individual check scoring logic in `repopulse/checks/*` (agent-checks owns that).
- Do NOT change `examples/github-action-repopulse.yml` (agent-ci).
- Do NOT break existing configs that omit `profile` (must remain valid and behave identically).
- Do NOT push/PR.

## Design (implement exactly)

### 1. Built-in profiles

Define a module-level dict `PROFILES: dict[str, dict]` in `settings.py`:

**`strict`** — high bar for CI gates:

```yaml
# conceptual
fail_under: 85
weights:
  readme: 20
  license: 10
  gitignore: 10
  tests: 20
  github_actions: 20
  activity: 5
  sensitive_files: 10
  structure: 3
  package_scripts: 2
# no disabled checks
```

Note: weights should still sum roughly ~100 for scored checks (20+10+10+20+20+5+10+3+2 = 100).

**`library`** — favor packaging, tests, license over recent activity:

```yaml
fail_under: 75
disabled_checks: []  # keep activity but lower weight
weights:
  readme: 15
  license: 15
  gitignore: 10
  tests: 25
  github_actions: 15
  activity: 5
  sensitive_files: 10
  structure: 5
  package_scripts: 0  # optional: use disabled or weight 0
```

Prefer **disabling** `activity` for library profile OR weight 5 — pick one and document. Recommended:

- `disabled_checks: []`
- lower activity weight as above; boost tests + license
- sum weights of non-zero = 100 (adjust structure/package_scripts)

**`docs`** — docs-heavy:

```yaml
fail_under: 70
weights:
  readme: 35
  license: 10
  gitignore: 10
  tests: 10
  github_actions: 10
  activity: 10
  sensitive_files: 10
  structure: 5
  package_scripts: 0
```

If `package_scripts: 0`, either omit key or treat weight 0 like disable via `apply_score_config` (weight 0 sets max_score 0). Current code:

```python
if weight is None or check.max_score == 0:
    adjusted.append(check)
    continue
ratio = check.score / check.max_score
adjusted.append(check.model_copy(update={"score": round(ratio * weight), "max_score": weight}))
```

Weight `0` is valid (validator allows >=0) and will zero that check’s contribution. Good.

### 2. Config field

```python
profile: str | None = None
```

Validator: normalize to lowercase strip; if set, must be one of `PROFILES` keys else raise `ValueError` with clear message listing allowed names.

### 3. Merge order (critical)

When loading config:

1. Start from empty defaults.
2. If `profile` set, apply profile’s `weights`, `disabled_checks`, `fail_under` as base.
3. Overlay explicit YAML fields on top (user overrides win):
   - explicit `weights` keys override profile weights key-by-key (merge dicts)
   - explicit `disabled_checks` **replace or extend**? Use **union** (set merge) so profile disables remain unless user re-enables… Simpler rule for alpha:
   - **If user provides `disabled_checks` list in YAML, replace profile’s list entirely** (documented).
   - **If user provides `weights`, merge over profile weights** (user keys win).
   - **If user provides `fail_under`, override profile fail_under**.

Implement a function:

```python
def resolve_config(raw: dict) -> RepoPulseConfig:
    ...
```

Or resolve inside `load_config` after yaml load, before/after model_validate.

Recommended approach:

1. Parse YAML to dict.
2. Peek `profile` value.
3. Build base dict from profile if any.
4. Merge user dict with rules above.
5. `RepoPulseConfig.model_validate(merged)`.

Keep `profile` field on the model so JSON report can show `"profile": "strict"`.

### 4. Examples

Create:

- `examples/profiles/strict.yml` with only `profile: strict`
- `examples/profiles/library.yml` with only `profile: library`
- `examples/profiles/docs.yml` with only `profile: docs`

Keep `examples/repopulse.yml` as a custom override example (can add a comment that profiles exist).

## Steps

### Step 1: Implement PROFILES + merge in settings.py

### Step 2: Tests in test_settings.py

Required cases:

1. `profile: strict` alone loads expected fail_under and weights keys.
2. User weight override: profile strict + `weights: {readme: 50}` → readme is 50, other strict weights remain.
3. Unknown profile raises ValueError (via load_config).
4. No profile → identical empty defaults as before.
5. `apply_score_config` still works with resolved profile config (optional integration assert).

### Step 3: Docs + examples + CHANGELOG

### Step 4: Run full pytest and ruff

## Test plan

Pattern after existing `test_load_config_reads_yaml` in `tests/test_settings.py`.

Verification:

```bash
python -m pytest tests/test_settings.py tests/ -q
python -m ruff check repopulse/settings.py tests/test_settings.py
```

## Done criteria

- [ ] `profile` supported in `.repopulse.yml`
- [ ] Built-ins: `strict`, `library`, `docs`
- [ ] Overrides documented and tested
- [ ] Backward compatible when profile omitted
- [ ] Examples under `examples/profiles/`
- [ ] CHANGELOG + USAGE/docs updated
- [ ] All tests pass; ruff clean on touched Python files

## STOP conditions

- Merge rules conflict with existing behavior of valid configs without profile — must not change that path.
- You need to change check keys to make profiles work — stop (keys are fixed).
- `apply_score_config` cannot handle weight 0 correctly for your design — fix design or report; do not hack checks.

## Maintenance notes

- Future profiles: add to `PROFILES` only; keep names stable.
- JSON `schema_version` stays `1.0` if only additive config field.
