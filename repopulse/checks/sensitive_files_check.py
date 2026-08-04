from pathlib import PurePosixPath

from repopulse.models import CheckResult, FileItem

SENSITIVE_NAMES = {
    ".env",
    ".env.local",
    "credentials.json",
    "service-account.json",
    "firebase-key.json",
    "private-key.pem",
    "id_rsa",
}

# First path segment: treated as sample/fixture trees, not production secrets by default.
FIXTURE_ROOTS = {
    "tests",
    "test",
    "testing",
    "testdata",
    "test_data",
    "fixtures",
    "fixture",
    "examples",
    "example",
    "samples",
    "sample",
    "__tests__",
    "spec",
    "specs",
}


def _is_fixture_path(path: str) -> bool:
    parts = PurePosixPath(path).parts
    if not parts:
        return False
    return parts[0].lower() in FIXTURE_ROOTS


def run_sensitive_files_check(files: list[FileItem]) -> CheckResult:
    matches = [
        file.path
        for file in files
        if file.type == "blob" and PurePosixPath(file.path).name.lower() in SENSITIVE_NAMES
    ]
    production = sorted(p for p in matches if not _is_fixture_path(p))
    fixtures = sorted(p for p in matches if _is_fixture_path(p))

    if production:
        shown = ", ".join(production[:5])
        extra = f" (also fixture paths: {', '.join(fixtures[:3])})" if fixtures else ""
        return CheckResult(
            key="sensitive_files",
            title="Sensitive Files",
            status="fail",
            score=0,
            max_score=10,
            message=f"Potential sensitive file names detected: {shown}.{extra}",
            recommendations=[
                "Remove sensitive files from the repository and rotate any exposed credentials."
            ],
        )

    if fixtures:
        shown = ", ".join(fixtures[:5])
        return CheckResult(
            key="sensitive_files",
            title="Sensitive Files",
            status="warn",
            score=7,
            max_score=10,
            message=(
                f"Sensitive-looking names under test/example paths: {shown}. "
                "Treated as fixtures (not a production secret layout)."
            ),
            recommendations=[
                "Confirm fixture files do not contain real secrets; prefer dummy values in tests/examples."
            ],
        )

    return CheckResult(
        key="sensitive_files",
        title="Sensitive Files",
        status="pass",
        score=10,
        max_score=10,
        message="No common sensitive file names detected.",
    )
