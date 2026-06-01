from pathlib import PurePosixPath

from repopulse.models import CheckResult, FileItem


def run_actions_check(files: list[FileItem], workflow_contents: dict[str, str] | None = None) -> CheckResult:
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

    workflow_contents = workflow_contents or {}
    names = " ".join(PurePosixPath(path).name.lower() for path in workflows)
    content = " ".join(workflow_contents.get(path, "") for path in workflows).lower()
    signal = f"{names} {content}"
    ci = any(token in signal for token in ("ci", "test", "pytest", "npm test", "unittest"))
    quality = any(token in signal for token in ("lint", "ruff", "flake8", "eslint", "build", "mypy"))
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
