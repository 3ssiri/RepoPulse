# Plan 011 — Finish PyPI readiness

**Status:** DONE  
**Priority:** P1  
**Agent:** agent-pypi  
**Depends on:** —

## Goal

Complete packaging/docs so the only remaining human step is the one-time PyPI Trusted Publisher (if not already done). Do not invent credentials.

## Delivered

1. Verify `pyproject.toml` name is `repopulse-cli`, scripts entry `repopulse`.
2. `docs/PUBLISHING.md` clear one-shot checklist (already mostly done — tighten + add verify commands).
3. `INSTALLATION.md` / `README.md` / `USAGE.md` use `pip install repopulse-cli`.
4. `examples/github-action-repopulse.yml` uses `repopulse-cli`.
5. Optional: small test or assertion that package metadata name is `repopulse-cli` (read pyproject via tomllib in a tiny test).
6. Do **not** set `PUBLISH_TO_PYPI=true` unless pending publisher is confirmed working.
7. CHANGELOG Unreleased / version notes for batch 009–011 (orchestrator may own final version bump).

## Out of scope

- Creating a PyPI account for the user.
- Publishing without Trusted Publisher.

## Done when

- Docs consistent.
- Metadata test green if added.
