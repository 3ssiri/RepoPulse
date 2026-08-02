# Implementation Plans

Generated 2026-08-02 against commit `bc427a8`. Three parallel workstreams for RepoPulse improvement.

## Execution order & status

| Plan | Title | Priority | Effort | Depends on | Agent | Status |
|------|-------|----------|--------|------------|-------|--------|
| 001 | Add GitHub Actions example + CI usage docs | P1 | S | — | agent-ci | DONE |
| 002 | Named scoring profiles in config | P1 | M | — | agent-profiles | DONE |
| 003 | Deeper tests + actions checks | P1 | M | — | agent-checks | DONE |
| 004 | Release / publish readiness 0.2.0 | P1 | S | — | agent-publish | DONE |
| 005 | Issue-ready recommendations format | P1 | S | — | agent-issues | DONE |
| 006 | Local path scan | P1 | L | — | agent-local | DONE |
| 007 | Richer reports, security, release profile | P1 | M | 001–006 | orchestrator | DONE |
| 008 | Compare two scans (branch/path score delta) | P1 | M | 007 | orchestrator | DONE |

Status values: `TODO` | `IN PROGRESS` | `DONE` | `BLOCKED` | `REJECTED`

## Parallelism

Plans **001**, **002**, and **003** are intentionally independent:

- 001 only touches `examples/`, docs, and optionally a sample workflow path under `examples/`
- 002 only touches `repopulse/settings.py`, scoring helpers if needed, tests for settings, `examples/*.yml`, docs
- 003 only touches `repopulse/checks/tests_check.py`, `repopulse/checks/actions_check.py`, and `tests/test_checks.py`

Do not edit each other's files. After all agents finish, the orchestrator merges and runs full `pytest` + `ruff check .`.

## Dependency notes

- None between 001/002/003.
- Optional later: publish package release (not in this batch).

## Findings considered and rejected (this batch)

- Full plugin system — too early for alpha.
- Local disk scan (`scan .`) — high value later; larger scope than this batch.
- Issue-ready export format — deferred after profiles land.
- Publishing to PyPI — needs maintainer credentials; document only if needed later.
