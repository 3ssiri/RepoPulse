from pathlib import PurePosixPath
from typing import Literal

from repopulse.models import CheckResult, FileItem

# Content-light tokens only (workflow text + basenames). No network.

TEST_TOKENS = (
    "pytest",
    "python -m pytest",
    "py.test",
    "npm test",
    "npm run test",
    "pnpm test",
    "yarn test",
    "vitest",
    "jest",
    "mocha",
    "cargo test",
    "go test",
    "unittest",
    "python -m unittest",
    "tox",
    "nox",
    "hatch test",
    "uv run pytest",
    "coverage run",
    "make test",
    "ctest",
    "phpunit",
    "rspec",
)

QUALITY_TOKENS = (
    "ruff",
    "eslint",
    "flake8",
    "mypy",
    "pyright",
    "pylint",
    "lint",
    "prettier",
    "black",
    "isort",
    "format",
    "pre-commit",
    "typecheck",
    "type-check",
    "bandit",
)

SETUP_TOKENS = (
    "actions/setup-python",
    "actions/setup-node",
    "actions/setup-go",
    "actions/setup-java",
    "astral-sh/setup-uv",
    "pip install",
    "pipx",
    "npm ci",
    "npm install",
    "pnpm install",
    "yarn install",
    "uv sync",
    "uv pip",
    "poetry install",
)

TRIGGER_TOKENS = (
    "pull_request",
    "push:",
    "workflow_dispatch",
    "schedule:",
)

# Basename fragments that imply a CI/test workflow even when content is thin/missing.
TEST_NAME_HINTS = (
    "test",
    "tests",
    "ci",
    "check",
    "checks",
    "unit",
    "e2e",
    "integration",
    "matrix",
    "build",
    "verify",
)


def _signal_hits(signal: str, tokens: tuple[str, ...]) -> list[str]:
    return [token for token in tokens if token in signal]


def _workflow_name_hints(workflow_paths: list[str]) -> bool:
    """True if any workflow basename looks like a CI/test job (e.g. tests.yaml, run-tests.yml)."""
    for path in workflow_paths:
        stem = PurePosixPath(path).stem.lower().replace("_", "-")
        parts = [p for p in stem.replace(".", "-").split("-") if p]
        joined = " ".join(parts)
        for hint in TEST_NAME_HINTS:
            if hint in parts or hint in joined:
                return True
    return False


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
    has_tests_content = bool(test_hits)
    has_test_name_hint = _workflow_name_hints(workflows)
    has_tests = has_tests_content or has_test_name_hint
    has_quality = bool(quality_hits)
    has_setup = any(token in signal for token in SETUP_TOKENS)
    has_triggers = any(token in signal for token in TRIGGER_TOKENS)
    multi_workflow = len(workflows) >= 2

    # Scoring prioritizes content; filename hints and solid CI plumbing raise floors
    # so mature repos (tests.yaml + tox, lint + run-tests) are not under-scored.
    if has_tests_content and has_quality:
        score = 15
    elif has_tests_content and (has_setup or has_triggers):
        score = 13
    elif has_tests_content:
        score = 12
    elif has_quality and has_test_name_hint:
        score = 13
    elif has_quality and has_setup and has_triggers:
        score = 12
    elif has_quality and (has_setup or has_triggers or multi_workflow):
        score = 11
    elif has_quality or (has_test_name_hint and (has_setup or has_triggers)):
        score = 10
    elif has_test_name_hint or (has_setup and has_triggers):
        score = 8
    else:
        score = 6

    parts: list[str] = []
    if has_tests_content:
        parts.append("tests")
    elif has_test_name_hint:
        parts.append("test-named workflows")
    if has_quality:
        quality_label = (
            "lint"
            if any(
                "lint" in hit or hit in {"ruff", "eslint", "flake8", "pylint"}
                for hit in quality_hits
            )
            else "quality"
        )
        parts.append(quality_label)
    if has_setup:
        parts.append("setup")
    if has_triggers:
        parts.append("PR/push triggers")
    if multi_workflow:
        parts.append(f"{len(workflows)} workflows")

    if parts:
        message = f"GitHub Actions workflow coverage detected: {' + '.join(parts)}."
    else:
        message = "GitHub Actions workflows found, but no test or quality signals."

    recommendations: list[str] = []
    if score == 15:
        status: Literal["pass", "warn", "fail"] = "pass"
    elif score >= 12:
        status = "pass"
        if not has_quality:
            recommendations = ["Add linting or type-check steps to the CI workflow."]
        elif not has_tests_content:
            recommendations = [
                "Add an explicit test step in CI (for example pytest, tox, npm test, or go test)."
            ]
    elif score >= 8:
        status = "warn"
        if not has_tests and not has_quality:
            recommendations = [
                "Add CI jobs that run tests and linting (content matters more than workflow file names)."
            ]
        elif not has_tests_content:
            recommendations = [
                "Add an explicit test step in CI (for example pytest, tox, npm test, or go test)."
            ]
        elif not has_quality:
            recommendations = ["Add linting or type-check steps to the CI workflow."]
        else:
            recommendations = ["Expand CI coverage (matrix, caching, or additional quality gates)."]
    else:
        status = "warn"
        recommendations = [
            "Strengthen CI: run tests and lint/type-check on pull_request or push."
        ]

    return CheckResult(
        key="github_actions",
        title="GitHub Actions",
        status=status,
        score=score,
        max_score=15,
        message=message,
        recommendations=recommendations,
    )
