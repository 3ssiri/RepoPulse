"""Regression coverage for RepoPulse Web shared-state request ordering.

These tests intentionally keep the frontend dependency-free: they verify the
small staleness and registration contracts in app.js without introducing a
JavaScript test stack.
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


def test_failed_scan_puts_the_retained_selection_back_in_the_form():
    """A failed scan keeps the previous selection; the form must show it again.

    Otherwise the form displays the repository the user typed while Compare
    still acts on the retained one, and the two silently disagree.
    """
    scan = _async_function("scanRepository", "async function compareRefs")
    catch = scan.split("} catch (error) {", 1)[1]

    assert "syncScanForm(state.repositoryUrl, state.ref)" in catch
    # Only when a previous scan actually succeeded - a first failed scan must
    # not wipe what the user typed.
    assert catch.find("state.currentReport") < catch.find("syncScanForm(")


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


def test_webmcp_sync_registration_failure_is_handled_before_promise_all():
    """A synchronous registerTool throw must abort partial registrations cleanly."""
    source = _source()
    registration = source.split("function registerWebMCPTools", 1)[1].split(
        "function main", 1
    )[0]
    before_promise = registration.split("Promise.all(registrations)", 1)[0]

    assert "let registrations;" in before_promise
    assert "try {" in before_promise
    assert "registrations = tools.map" in before_promise
    assert "Promise.resolve(" in before_promise

    sync_catch = before_promise.split("} catch", 1)[1]
    assert "registration.abort()" in sync_catch
    assert "state.webmcpAvailable = false" in sync_catch
    assert "renderWebMCPStatus()" in sync_catch
    assert "return;" in sync_catch
