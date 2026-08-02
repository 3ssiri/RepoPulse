from pathlib import PurePosixPath

from repopulse.models import CheckResult, FileItem

# Small keyword lists — keep documented and content-light (no network).
TEST_TOKENS = (
    "pytest",
    "python -m pytest",
    "npm test",
    "npm run test",
    "pnpm test",
    "yarn test",
    "vitest",
    "jest",
    "cargo test",
    "go test",
    "unittest",
)
QUALITY_TOKENS = (
    "ruff",
    "eslint",
    "flake8",
    "mypy",
    "lint",
    "prettier",
    "black",
    "format",
)
SETUP_TOKENS = (
    "actions/setup-python",
    "actions/setup-node",
    "pip install",
    "npm ci",
    "pnpm install",
)
TRIGGER_TOKENS = (
    "pull_request",
    "push:",
)


def _signal_hits(signal: str, tokens: tuple[str, ...]) -> list[str]:
    return [token for token in tokens if token in signal]


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

    test_hits = _signal_hits(signal, TEST_TOKENS)
    quality_hits = _signal_hits(signal, QUALITY_TOKENS)
    has_tests = bool(test_hits)
    has_quality = bool(quality_hits)
    has_setup = any(token in signal for token in SETUP_TOKENS)
    has_triggers = any(token in signal for token in TRIGGER_TOKENS)

    if has_tests and has_quality:
        score = 15
    elif has_tests:
        score = 12
    elif has_quality:
        score = 10
    else:
        score = 6

    parts: list[str] = []
    if has_tests:
        parts.append("tests")
    if has_quality:
        # Prefer a short human label from the first quality hit.
        quality_label = "lint" if any("lint" in hit or hit in {"ruff", "eslint", "flake8"} for hit in quality_hits) else "quality"
        parts.append(quality_label)
    if has_setup:
        parts.append("setup")
    if has_triggers:
        parts.append("PR/push triggers")

    if parts:
        message = f"GitHub Actions workflow coverage detected: {' + '.join(parts)}."
    else:
        message = "GitHub Actions workflows found, but no test or quality signals."

    if score == 15:
        status = "pass"
        recommendations: list[str] = []
    elif score >= 12:
        status = "pass"
        recommendations = ["Add linting or type-check steps to the CI workflow."]
    elif score >= 1:
        status = "warn"
        recommendations = ["Name or add workflows for CI, tests, linting, and builds."]
    else:
        status = "fail"
        recommendations = ["Add a CI workflow that runs tests, linting, or builds."]

    return CheckResult(
        key="github_actions",
        title="GitHub Actions",
        status=status,
        score=score,
        max_score=15,
        message=message,
        recommendations=recommendations,
    )
