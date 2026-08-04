from repopulse.checks.actions_check import run_actions_check
from repopulse.checks.dependencies_check import run_dependencies_check
from repopulse.checks.gitignore_check import run_gitignore_check
from repopulse.checks.package_check import run_package_check
from repopulse.checks.readme_check import run_readme_check
from repopulse.checks.security_check import run_security_check
from repopulse.checks.sensitive_files_check import run_sensitive_files_check
from repopulse.checks.tests_check import run_tests_check
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


def test_sensitive_files_fixture_env_is_warn_not_fail():
    files = [item("tests/test_apps/.env"), item("src/app.py")]

    result = run_sensitive_files_check(files)

    assert result.status == "warn"
    assert result.score == 7
    assert "tests/test_apps/.env" in result.message
    assert "fixture" in result.message.lower()


def test_license_check_accepts_license_txt():
    from repopulse.checks.license_check import run_license_check

    files = [item("LICENSE.txt"), item("README.md")]
    result = run_license_check(files)
    assert result.status == "pass"
    assert result.score == 10
    assert "LICENSE.txt" in result.message


def test_license_check_ignores_nested_license_only():
    from repopulse.checks.license_check import run_license_check

    files = [item("docs/license.rst"), item("examples/app/LICENSE.txt")]
    result = run_license_check(files)
    assert result.status == "fail"
    assert result.score == 0


def test_structure_check_python_package_with_docs_passes():
    from repopulse.checks.structure_check import run_structure_check

    files = [
        item("repopulse/cli.py"),
        item("repopulse/checks/license_check.py"),
        item("README.md"),
        item("CHANGELOG.md"),
        item("CONTRIBUTING.md"),
        item("LICENSE"),
        item("pyproject.toml"),
        item("USAGE.md"),
        item("INSTALLATION.md"),
        item("ARCHITECTURE.md"),
    ]
    result = run_structure_check(files)
    assert result.score >= 4
    assert result.status == "pass"


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


def test_tests_check_scores_python_pytest_configuration():
    files = [item("tests/test_app.py"), item("pyproject.toml")]
    pyproject = """
    [project.optional-dependencies]
    dev = ["pytest"]

    [tool.pytest.ini_options]
    testpaths = ["tests"]
    """

    result = run_tests_check(files, pyproject_content=pyproject)

    assert result.status == "pass"
    assert result.score == 15
    assert "pytest" in result.message.lower()


def test_tests_check_detects_vitest_via_package_json():
    files = [item("src/app.test.ts"), item("package.json")]
    package = """
    {
      "scripts": {"test": "vitest run"},
      "devDependencies": {"vitest": "^1.0.0"}
    }
    """

    result = run_tests_check(files, package_json_content=package)

    assert result.status == "pass"
    assert result.score == 15
    assert "vitest" in result.message.lower()


def test_tests_check_detects_jest_via_package_json():
    files = [item("__tests__/app.spec.js"), item("package.json")]
    package = """
    {
      "scripts": {"test": "jest"},
      "devDependencies": {"jest": "^29.0.0"}
    }
    """

    result = run_tests_check(files, package_json_content=package)

    assert result.status == "pass"
    assert result.score == 15
    assert "jest" in result.message.lower()


def test_tests_check_conftest_signals_pytest_framework():
    files = [
        item("tests/test_app.py"),
        item("tests/conftest.py"),
    ]

    result = run_tests_check(files)

    # Dir + files + conftest → 13 pass (framework present; optional command rec).
    assert result.score == 13
    assert result.status == "pass"
    assert "pytest" in result.message.lower()


def test_tests_check_noxfile_counts_as_command():
    files = [
        item("tests/test_app.py"),
        item("noxfile.py"),
    ]
    result = run_tests_check(files)
    assert result.score == 15
    assert result.status == "pass"


def test_tests_check_hatch_in_pyproject_counts_as_command():
    files = [item("tests/test_app.py"), item("pyproject.toml")]
    pyproject = """
    [tool.hatch.envs.test]
    dependencies = ["pytest"]
    """
    result = run_tests_check(files, pyproject_content=pyproject)
    assert result.score == 15
    assert result.status == "pass"


def test_tests_check_pytest_ini_counts_as_test_command():
    files = [
        item("tests/test_app.py"),
        item("tests/conftest.py"),
        item("pytest.ini"),
    ]

    result = run_tests_check(files)

    assert result.score == 15
    assert result.status == "pass"
    assert "pytest" in result.message.lower()


def test_tests_check_framework_config_only_scores_four():
    files = [item("pyproject.toml")]
    pyproject = """
    [project.optional-dependencies]
    dev = ["pytest"]

    [tool.pytest.ini_options]
    testpaths = ["tests"]
    """

    result = run_tests_check(files, pyproject_content=pyproject)

    assert result.score == 4
    assert result.status == "warn"
    assert "pytest" in result.message.lower()


def test_actions_check_workflows_only_scores_six():
    files = [item(".github/workflows/noop.yml")]
    workflows = {".github/workflows/noop.yml": "jobs:\n  greet:\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo hello\n"}

    result = run_actions_check(files, workflows)

    assert result.score == 6
    assert result.status == "warn"


def test_actions_check_tests_without_quality_scores_twelve_or_higher():
    files = [item(".github/workflows/ci.yml")]
    workflows = {
        ".github/workflows/ci.yml": "on:\n  push:\njobs:\n  test:\n    steps:\n      - run: python -m pytest\n"
    }

    result = run_actions_check(files, workflows)

    # Content tests + trigger → at least 12; setup/triggers can raise to 13.
    assert result.score >= 12
    assert result.status == "pass"
    assert "tests" in result.message.lower()


def test_actions_check_quality_only_scores_ten():
    files = [item(".github/workflows/lint.yml")]
    workflows = {
        ".github/workflows/lint.yml": "jobs:\n  quality:\n    steps:\n      - run: ruff check .\n      - run: eslint src\n"
    }

    result = run_actions_check(files, workflows)

    assert result.score == 10
    assert result.status == "warn"
    # Do not tell maintainers to "add workflows" when they already have one.
    assert "name or add workflows" not in " ".join(result.recommendations).lower()


def test_actions_check_quality_plus_setup_triggers_is_pass():
    """Mature lint CI without pytest string should not be stuck at a weak warn."""
    files = [item(".github/workflows/lint.yml")]
    workflows = {
        ".github/workflows/lint.yml": (
            "on:\n  pull_request:\n  push:\n"
            "jobs:\n  lint:\n    steps:\n"
            "      - uses: actions/setup-python@v5\n"
            "      - run: ruff check .\n"
        )
    }

    result = run_actions_check(files, workflows)

    assert result.score >= 12
    assert result.status == "pass"


def test_actions_check_test_filename_hint_with_quality():
    files = [
        item(".github/workflows/tests.yaml"),
        item(".github/workflows/pre-commit.yaml"),
    ]
    workflows = {
        ".github/workflows/tests.yaml": (
            "on: [push]\njobs:\n  t:\n    steps:\n"
            "      - uses: actions/setup-python@v5\n"
            "      - run: echo run suite\n"
        ),
        ".github/workflows/pre-commit.yaml": (
            "jobs:\n  pc:\n    steps:\n      - run: pre-commit run --all-files\n"
        ),
    }

    result = run_actions_check(files, workflows)

    assert result.score >= 12
    assert result.status == "pass"
    assert "test-named" in result.message.lower() or "quality" in result.message.lower()


def test_actions_check_detects_tox_as_test_signal():
    files = [item(".github/workflows/ci.yml")]
    workflows = {
        ".github/workflows/ci.yml": "jobs:\n  test:\n    steps:\n      - run: tox -e py\n"
    }

    result = run_actions_check(files, workflows)

    assert result.score >= 12
    assert result.status == "pass"
    assert "tests" in result.message.lower()


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
    assert result.recommendations == []


def test_security_check_lists_missing_pieces_specifically():
    files = [item("SECURITY.md")]
    result = run_security_check(files, {})

    assert result.status == "warn"
    assert "SECURITY.md" in result.message
    assert any("Dependabot" in item for item in result.recommendations)
    assert any("scanning" in item.lower() or "CodeQL" in item for item in result.recommendations)


def test_security_check_accepts_trivy_as_scanner():
    files = [
        item("SECURITY.md"),
        item(".github/dependabot.yml"),
        item(".github/workflows/security.yml"),
    ]
    workflows = {".github/workflows/security.yml": "run: trivy fs .\n"}

    result = run_security_check(files, workflows)

    assert result.status == "pass"
    assert "trivy" in result.message.lower()
