from pathlib import PurePosixPath

from repopulse.models import CheckResult, FileItem
from repopulse.utils import parse_json_content


def run_tests_check(files: list[FileItem], package_json_content: str | None = None) -> CheckResult:
    paths = [file.path for file in files if file.type == "blob"]
    lower_paths = [path.lower() for path in paths]
    has_test_dir = any(path.startswith(("tests/", "test/", "__tests__/")) for path in lower_paths)
    has_test_file = any(
        PurePosixPath(path).name.startswith("test_")
        or ".test." in PurePosixPath(path).name
        or ".spec." in PurePosixPath(path).name
        for path in lower_paths
    )
    package = parse_json_content(package_json_content)
    scripts = package.get("scripts", {}) if isinstance(package.get("scripts"), dict) else {}
    has_test_command = "test" in scripts and bool(str(scripts.get("test", "")).strip())

    if (has_test_dir or has_test_file) and has_test_command:
        score = 15
    elif has_test_dir and has_test_file:
        score = 12
    elif has_test_dir or has_test_file:
        score = 7
    else:
        score = 0

    if score == 15:
        status = "pass"
        message = "Tests and a test command were detected."
        recommendations: list[str] = []
    elif score:
        status = "warn"
        message = "Some test indicators were detected, but test automation can improve."
        recommendations = ["Add or document a clear test command."]
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
