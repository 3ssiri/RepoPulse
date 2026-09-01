"""Regression coverage for RepoPulse Web shared-state request ordering.

These tests intentionally keep the frontend dependency-free: they verify the
small staleness contract in app.js without introducing a JavaScript test stack.
"""

from pathlib import Path

APP_JS = Path(__file__).resolve().parents[1] / "webapp" / "static" / "app.js"


def _source() -> str:
    return APP_JS.read_text(encoding="utf-8")


def _async_function(name: str, next_marker: str) -> str:
    source = _source()
    return source.split(f"async function {name}", 1)[1].split(next_marker, 1)[0]


def test_fresh_scan_can_switch_from_repository_a_to_b():
    """A fresh scan must ignore the previously selected repository identity."""
    scan = _async_function("scanRepository", "async function compareRefs")

    stale_check = "isStaleResult(started.generation, requestGeneration, null, null)"
    assert stale_check in scan
    assert scan.find(stale_check) < scan.find("state.repositoryUrl = repositoryUrl")


def test_late_compare_cannot_commit_after_repository_switch():
    """A comparison remains pinned to the repository selected when it started."""
    compare = _async_function("compareRefs", "/* All GitHub-derived data")

    assert "startedUrl, state.repositoryUrl" in compare
    assert "isStaleResult(" in compare
    assert compare.find("isStaleResult(") < compare.find("state.currentComparison = comparison")


def test_stale_helper_separates_generation_from_optional_repository_identity():
    """Generation always matters; repository identity is checked only when supplied."""
    source = _source()
    helper = source.split("function isStaleResult", 1)[1].split("function beginRequest", 1)[0]

    assert "startedGeneration !== currentGeneration" in helper
    assert "startedUrl !== null && currentUrl !== null" in helper
    assert "startedUrl !== currentUrl" in helper


def test_newer_request_still_supersedes_older_scan_and_compare():
    """Generation ordering remains the common stale-result boundary."""
    scan = _async_function("scanRepository", "async function compareRefs")
    compare = _async_function("compareRefs", "/* All GitHub-derived data")

    assert "started.generation !== requestGeneration" in scan
    assert "started.generation !== requestGeneration" in compare
