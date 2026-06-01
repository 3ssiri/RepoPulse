from repopulse.checks.gitignore_check import run_gitignore_check
from repopulse.checks.readme_check import run_readme_check
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
