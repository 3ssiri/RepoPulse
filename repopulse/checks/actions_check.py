from pathlib import PurePosixPath

from repopulse.models import CheckResult, FileItem


def run_actions_check(files: list[FileItem]) -> CheckResult:
    workflows = [
        file.path
        for file in files
        if file.type == "blob" and file.path.lower().startswith(".github/workflows/")
    ]
    if not workflows:
        return CheckResult(
            key="github_actions",
            title="GitHub Actions",
            status="fail",
            score=0,
            max_score=15,
            message="No GitHub Actions workflows found.",
            recommendations=["Add a CI workflow that runs tests, linting, or builds."],
        )

    names = " ".join(PurePosixPath(path).name.lower() for path in workflows)
    ci = any(token in names for token in ("ci", "test"))
    quality = any(token in names for token in ("lint", "build"))
    score = 15 if ci and quality else 12 if ci else 8
    return CheckResult(
        key="github_actions",
        title="GitHub Actions",
        status="pass" if score >= 12 else "warn",
        score=score,
        max_score=15,
        message="GitHub Actions workflow coverage was detected.",
        recommendations=[] if score == 15 else ["Name or add workflows for CI, tests, linting, and builds."],
    )
