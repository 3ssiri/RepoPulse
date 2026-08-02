from pathlib import PurePosixPath
from typing import Literal

from repopulse.models import CheckResult, FileItem
from repopulse.utils import parse_json_content

# Small keyword lists — keep documented and content-light (no network).
JS_TEST_RUNNERS = ("jest", "vitest", "mocha", "ava", "node:test")
PYTHON_FRAMEWORK_MARKERS = ("pytest", "unittest", "nose2", "nose")
TEST_DIR_PREFIXES = ("tests/", "test/", "__tests__/")
FRAMEWORK_CONFIG_NAMES = frozenset({"pytest.ini", "conftest.py", "tox.ini", "setup.cfg", "jest.config.js", "jest.config.ts", "vitest.config.ts", "vitest.config.js"})


def _is_test_file(name: str) -> bool:
    """Detect common test file name patterns across Python and JS ecosystems."""
    lower = name.lower()
    if lower.startswith("test_") or lower.endswith("_test.py"):
        return True
    return ".test." in lower or ".spec." in lower


def _detect_python_framework(lower_paths: list[str], pyproject_lower: str) -> str | None:
    """Return a known Python test framework name, or None."""
    has_pytest_config = any(
        PurePosixPath(path).name in {"pytest.ini", "conftest.py"} for path in lower_paths
    )
    has_tox = any(PurePosixPath(path).name == "tox.ini" for path in lower_paths)
    if (
        "pytest" in pyproject_lower
        or "[tool.pytest.ini_options]" in pyproject_lower
        or has_pytest_config
        or (has_tox and "pytest" in pyproject_lower)
    ):
        return "pytest"
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
        "pytest" in pyproject_lower
        or "[tool.pytest.ini_options]" in pyproject_lower
        or any(PurePosixPath(path).name in {"pytest.ini", "tox.ini"} for path in lower_paths)
    )
    has_test_command = has_node_test_command or has_python_test_command

    python_fw = _detect_python_framework(lower_paths, pyproject_lower)
    js_fw = _detect_js_framework(package, scripts)
    framework = python_fw or js_fw
    has_framework_signal = bool(framework) or _has_framework_config_files(lower_paths)

    if (has_test_dir or has_test_file) and has_test_command:
        score = 15
    elif has_test_dir and has_test_file:
        score = 12
    elif has_test_dir or has_test_file:
        score = 7
    elif has_framework_signal or has_test_command:
        # Framework/tooling configured but no test files or dirs yet.
        score = 4
    else:
        score = 0

    status: Literal["pass", "warn", "fail"]
    fw_label = f" ({framework})" if framework else ""
    if score == 15:
        status = "pass"
        message = f"Tests{fw_label} and a test command were detected."
        recommendations: list[str] = []
    elif score == 12:
        status = "warn"
        message = f"Test directory and files{fw_label} were detected, but no test command."
        recommendations = ["Wire a documented test command (for example pytest or npm test)."]
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
