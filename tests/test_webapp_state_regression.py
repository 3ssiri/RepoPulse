"""Regression coverage for RepoPulse Web shared-state request ordering.

These tests intentionally keep the frontend dependency-free: they verify the
small staleness contract in app.js without introducing a JavaScript test stack.
"""

from pathlib import Path

APP_JS = Path(__file__).resolve().parents[1] / "webapp" / "static" / "app.js"


def _source() -> str:
    return APP_JS.read_text(encoding="utf-8")


def _function(name: str, next_name: str) -> str:
    source = _source()
    return source.split(f"function {name}", 1)[1].split(f"function {next_name}", 1)[0]


def _async_function(name: str, next_marker: str) -> str:
    source = _source()
    return source.split(f"async function {name}", 1)[1].split(next_marker, 1)[0]


def test_fresh_scan_can_switch_from_repository_a_to_b():
    """A fresh scan must depend only on request generation, not the old selected URL."""
    helper = _function("isStaleRequest", "isStaleComparison")
    scan = _async_function("scanRepository", "async function compareRefs")

    assert "startedGeneration !== requestGeneration" in helper
    assert "repositoryUrl" not in helper
    assert "state.repositoryUrl" not in helper

    stale_check = "if (isStaleRequest(started.generation))"
    assert stale_check in scan
    assert scan.find(stale_check) < scan.find("state.repositoryUrl = repositoryUrl")
    assert "isStaleComparison(" not in scan


def test_late_compare_cannot_commit_after_repository_switch():
    """A comparison is valid only while its starting repository remains selected."""
    helper = _function("isStaleComparison", "beginRequest")
    compare = _async_function("compareRefs", "/* All GitHub-derived data")

    assert "isStaleRequest(startedGeneration)" in helper
    assert "startedUrl !== state.repositoryUrl" in helper

    stale_check = "if (isStaleComparison(started.generation, startedUrl))"
    assert stale_check in compare
    assert compare.find(stale_check) < compare.find("state.currentComparison = comparison")


def test_newer_request_still_supersedes_older_scan_and_compare():
    """Generation ordering remains the common stale-result boundary."""
    scan = _async_function("scanRepository", "async function compareRefs")
    compare = _async_function("compareRefs", "/* All GitHub-derived data")

    assert "started.generation !== requestGeneration" in scan
    assert "started.generation !== requestGeneration" in compare
