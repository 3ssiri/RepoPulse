from repopulse.checks.gitignore_check import run_gitignore_check
from repopulse.checks.actions_check import run_actions_check
from repopulse.checks.dependencies_check import run_dependencies_check
from repopulse.checks.package_check import run_package_check
from repopulse.checks.readme_check import run_readme_check
from repopulse.checks.security_check import run_security_check
from repopulse.checks.sensitive_files_check import run_sensitive_files_check
from repopulse.models import FileItem


def item(path: str, type_: str = "blob") -> FileItem:
    return FileItem(path=path, name=path.split("/")[-1], type=type_)


def test_readme_check_scores_complete_readme():
    files = [item("README.md")]
    content = """
    # Project

    This project checks repository health.

    ## Installation
    pip install .

    ## Usage
    repopulse scan URL

    ## Features
    Reports score.

    ## Tech Stack
    Python.
    """

    result = run_readme_check(files, content)

    assert result.status == "pass"
    assert result.score == 20


def test_gitignore_check_detects_common_patterns():
    files = [item(".gitignore")]
    content = ".env\nnode_modules/\n__pycache__/\n.venv/\ncoverage/\n"

    result = run_gitignore_check(files, content)

    assert result.status == "pass"
    assert result.score == 10


def test_sensitive_files_check_never_prints_secret_content():
    files = [item(".env"), item("src/app.py")]

    result = run_sensitive_files_check(files)

    assert result.status == "fail"
    assert result.score == 0
    assert ".env" in result.message
    assert "SECRET" not in result.message


def test_actions_check_reads_workflow_content():
    files = [item(".github/workflows/quality.yml")]
    workflows = {".github/workflows/quality.yml": "jobs:\n  test:\n    steps:\n      - run: pytest\n      - run: ruff check .\n"}

    result = run_actions_check(files, workflows)

    assert result.status == "pass"
    assert result.score == 15


def test_package_check_scores_python_tooling():
    files = [item("pyproject.toml"), item("tests/test_app.py")]
    content = """
    [project.optional-dependencies]
    dev = ["pytest", "ruff", "mypy"]
    """

    result = run_package_check(files, pyproject_content=content)

    assert result.status == "pass"
    assert result.score == 5


def test_dependencies_check_rewards_lockfile_and_dependabot():
    files = [
        item("pyproject.toml"),
        item("uv.lock"),
        item(".github/dependabot.yml"),
    ]

    result = run_dependencies_check(files)

    assert result.status == "pass"
    assert "lockfile" in result.message.lower()


def test_security_check_detects_security_policy_and_codeql():
    files = [
        item("SECURITY.md"),
        item(".github/workflows/codeql.yml"),
        item(".github/dependabot.yml"),
    ]
    workflows = {".github/workflows/codeql.yml": "uses: github/codeql-action/init@v3\n"}

    result = run_security_check(files, workflows)

    assert result.status == "pass"
    assert "CodeQL" in result.message
