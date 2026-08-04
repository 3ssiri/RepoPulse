from pathlib import PurePosixPath
from typing import Literal

from repopulse.models import CheckResult, FileItem
from repopulse.utils import parse_json_content

# Content-light heuristics only (file names + pyproject/package.json text). No network.

JS_TEST_RUNNERS = ("jest", "vitest", "mocha", "ava", "node:test", "tap", "jasmine")
PYTHON_FRAMEWORK_MARKERS = ("pytest", "unittest", "nose2", "nose", "hypothesis")
TEST_DIR_PREFIXES = ("tests/", "test/", "__tests__/", "spec/", "specs/")

# Presence of these files counts as a documented / runnable test entrypoint signal.
COMMAND_CONFIG_NAMES = frozenset(
    {
        "pytest.ini",
        "tox.ini",
        "noxfile.py",
        "hatch.toml",
        "setup.cfg",
        "phpunit.xml",
        "phpunit.xml.dist",
        "jest.config.js",
        "jest.config.ts",
        "jest.config.mjs",
        "vitest.config.ts",
        "vitest.config.js",
        "vitest.config.mjs",
        "karma.conf.js",
        "cypress.config.js",
        "cypress.config.ts",
        "playwright.config.ts",
        "playwright.config.js",
    }
)

FRAMEWORK_CONFIG_NAMES = COMMAND_CONFIG_NAMES | frozenset(
    {
        "conftest.py",
        ".coveragerc",
        "coverage.ini",
    }
)

# Substrings in pyproject.toml that imply a test runner / task is wired.
PYPROJECT_TEST_MARKERS = (
    "pytest",
    "[tool.pytest",
    "tool.pytest",
    "[tool.tox",
    "tool.tox",
    "[tool.nox",
    "tool.nox",
    "[tool.hatch",
    "tool.hatch",
    "[tool.coverage",
    "tool.coverage",
    "[tool.poe",
    "tool.poe",
    "taskipy",
    "invoke",
    "nose2",
    "unittest",
)


def _is_test_file(name: str) -> bool:
    """Detect common test file name patterns across Python and JS ecosystems."""
    lower = name.lower()
    if lower.startswith("test_") or lower.endswith("_test.py"):
        return True
    return ".test." in lower or ".spec." in lower


def _detect_python_framework(lower_paths: list[str], pyproject_lower: str) -> str | None:
    """Return a known Python test framework name, or None."""
    names = {PurePosixPath(path).name for path in lower_paths}
    if (
        "pytest" in pyproject_lower
        or "[tool.pytest" in pyproject_lower
        or "pytest.ini" in names
        or "conftest.py" in names
    ):
        return "pytest"
    if "noxfile.py" in names or "tool.nox" in pyproject_lower:
        return "nox"
    if "tox.ini" in names or "tool.tox" in pyproject_lower:
        return "tox"
    if "hatch.toml" in names or "tool.hatch" in pyproject_lower:
        return "hatch"
    if "unittest" in pyproject_lower or any(
        PurePosixPath(path).name.endswith("_test.py") for path in lower_paths
    ):
        return "unittest"
    for marker in PYTHON_FRAMEWORK_MARKERS:
        if marker in pyproject_lower:
            return marker
    return None


def _detect_js_framework(package: dict, scripts: dict) -> str | None:
    """Return a known JS test runner from package.json scripts or deps."""
    test_script = str(scripts.get("test", "")).lower()
    dep_keys: set[str] = set()
    for field in ("dependencies", "devDependencies", "peerDependencies"):
        deps = package.get(field)
        if isinstance(deps, dict):
            dep_keys.update(str(key).lower() for key in deps)

    for runner in JS_TEST_RUNNERS:
        if runner in test_script or runner in dep_keys:
            return runner
    return None


def _has_framework_config_files(lower_paths: list[str]) -> bool:
    return any(PurePosixPath(path).name in FRAMEWORK_CONFIG_NAMES for path in lower_paths)


def _has_command_config_files(lower_paths: list[str]) -> bool:
    return any(PurePosixPath(path).name in COMMAND_CONFIG_NAMES for path in lower_paths)


def _pyproject_has_test_command(pyproject_lower: str) -> bool:
    if not pyproject_lower:
        return False
    return any(marker in pyproject_lower for marker in PYPROJECT_TEST_MARKERS)


def run_tests_check(
    files: list[FileItem],
    package_json_content: str | None = None,
    pyproject_content: str | None = None,
) -> CheckResult:
    paths = [file.path for file in files if file.type == "blob"]
    lower_paths = [path.lower() for path in paths]
    has_test_dir = any(path.startswith(TEST_DIR_PREFIXES) for path in lower_paths)
    has_test_file = any(_is_test_file(PurePosixPath(path).name) for path in lower_paths)

    package = parse_json_content(package_json_content)
    scripts = package.get("scripts", {}) if isinstance(package.get("scripts"), dict) else {}
    has_node_test_command = "test" in scripts and bool(str(scripts.get("test", "")).strip())

    pyproject_lower = (pyproject_content or "").lower()
    has_python_test_command = (
        _pyproject_has_test_command(pyproject_lower) or _has_command_config_files(lower_paths)
    )
    has_test_command = has_node_test_command or has_python_test_command

    python_fw = _detect_python_framework(lower_paths, pyproject_lower)
    js_fw = _detect_js_framework(package, scripts)
    framework = python_fw or js_fw
    has_framework_signal = bool(framework) or _has_framework_config_files(lower_paths)

    if (has_test_dir or has_test_file) and has_test_command:
        score = 15
    elif has_test_dir and has_test_file and has_framework_signal:
        # Tests exist with clear framework (e.g. conftest/pytest) but no explicit command file.
        score = 13
    elif has_test_dir and has_test_file:
        score = 12
    elif has_test_dir or has_test_file:
        score = 7
    elif has_framework_signal or has_test_command:
        score = 4
    else:
        score = 0

    status: Literal["pass", "warn", "fail"]
    fw_label = f" ({framework})" if framework else ""
    if score == 15:
        status = "pass"
        message = f"Tests{fw_label} and a test command were detected."
        recommendations: list[str] = []
    elif score == 13:
        status = "pass"
        message = (
            f"Test directory and files{fw_label} were detected with framework config; "
            "document a one-line test command if not already obvious."
        )
        recommendations = [
            "Optionally document a root test command (pytest, tox, nox, npm test, or hatch test)."
        ]
    elif score == 12:
        status = "warn"
        message = f"Test directory and files{fw_label} were detected, but no test command."
        recommendations = [
            "Wire a documented test command (pytest, tox, nox, hatch test, npm test, or similar)."
        ]
    elif score == 7:
        status = "warn"
        message = f"Some test indicators{fw_label} were detected, but test automation can improve."
        recommendations = ["Add automated tests and a documented test command."]
    elif score == 4:
        status = "warn"
        message = f"Test framework config{fw_label} was detected, but no test files or directories."
        recommendations = ["Add automated tests under tests/ or matching *.test.* / test_* files."]
    else:
        status = "fail"
        message = "No test indicators were detected."
        recommendations = ["Add automated tests and a documented test command."]

    return CheckResult(
        key="tests",
        title="Tests",
        status=status,
        score=score,
        max_score=15,
        message=message,
        recommendations=recommendations,
    )
