# Plan 008 — Compare two health scans

**Status:** DONE  
**Priority:** P1  
**Depends on:** 007  

## Goal

Let maintainers diff repository health between two points: PR vs main checkouts, release tags, or two repos.

## Delivered

- `repopulse compare <baseline> <target>`
- Formats: table, markdown, json, summary
- `--fail-on-regression` for CI
- `--baseline-label` / `--target-label`
- Models: `CheckDelta`, `ComparisonReport`
- Module: `repopulse/compare.py`
- Docs: USAGE, roadmap, json-schema, CHANGELOG Unreleased
- Tests: `tests/test_compare.py`

## Out of scope (later)

- Fetching a specific GitHub ref without local checkout
- `gh issue create` from issues format
