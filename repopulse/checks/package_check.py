from pathlib import PurePosixPath

from repopulse.models import CheckResult, FileItem
from repopulse.utils import find_file, parse_json_content

PYTHON_TOOLING = ("pytest", "ruff", "mypy", "tox", "nox", "black", "hatch", "coverage")

# File-name signals that a runnable project command exists (content-light).
COMMAND_ENTRY_FILES = frozenset(
    {
        "makefile",
        "gnumakefile",
        "justfile",
        "taskfile.yml",
        "taskfile.yaml",
        "tox.ini",
        "noxfile.py",
        "hatch.toml",
    }
)

# pyproject sections that document entrypoints / tasks.
PYPROJECT_COMMAND_MARKERS = (
    "[project.scripts]",
    "project.scripts",
    "[project.entry-points",
    "[tool.poetry.scripts]",
    "tool.poetry.scripts",
    "[tool.hatch.envs",
    "tool.hatch.envs",
    "[tool.poe.tasks]",
    "tool.poe.tasks",
    "[tool.taskipy.tasks]",
    "tool.taskipy.tasks",
    "[tool.pdm.scripts]",
    "tool.pdm.scripts",
)


def _has_command_entry_file(files: list[FileItem]) -> bool:
    for file in files:
        if file.type != "blob":
            continue
        name = PurePosixPath(file.path).name.lower()
        if name in COMMAND_ENTRY_FILES:
            return True
    return False


def _pyproject_has_command_section(pyproject_content: str | None) -> bool:
    if not pyproject_content:
        return False
    lower = pyproject_content.lower()
    return any(marker in lower for marker in PYPROJECT_COMMAND_MARKERS)


def run_package_check(
    files: list[FileItem],
    package_json_content: str | None = None,
    pyproject_content: str | None = None,
) -> CheckResult:
    package = parse_json_content(package_json_content)
    scripts = package.get("scripts", {}) if isinstance(package.get("scripts"), dict) else {}
    script_keys = {
        key
        for key in ("dev", "build", "test", "lint", "start", "check")
        if key in scripts and str(scripts[key]).strip()
    }

    has_pyproject = find_file(files, {"pyproject.toml"}) is not None
    has_requirements = find_file(files, {"requirements.txt"}) is not None
    has_package_json = find_file(files, {"package.json"}) is not None

    python_tools = {
        tool for tool in PYTHON_TOOLING if pyproject_content and tool in pyproject_content.lower()
    }
    has_py_commands = _pyproject_has_command_section(pyproject_content) or _has_command_entry_file(files)

    # Strong: npm scripts and/or Python tooling / task entrypoints.
    strong = (has_package_json and bool(script_keys)) or (
        has_pyproject and (bool(python_tools) or has_py_commands)
    )
    # Soft: project metadata without explicit command lists (common healthy libraries).
    soft = has_package_json or has_pyproject or has_requirements

    if strong:
        score = 5
        status = "pass"
        message = "Package or project commands are documented."
        recommendations: list[str] = []
    elif soft:
        score = 4
        status = "pass"
        message = "Project package metadata detected."
        recommendations = []
    else:
        score = 0
        status = "fail"
        message = "No package scripts or Python project config detected."
        recommendations = ["Add clear dev, build, test, or lint commands in package metadata."]

    return CheckResult(
        key="package_scripts",
        title="Package Scripts",
        status=status,
        score=score,
        max_score=5,
        message=message,
        recommendations=recommendations,
    )
