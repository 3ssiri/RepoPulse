from pathlib import PurePosixPath

from repopulse.models import CheckResult, FileItem

STRUCTURE_PREFIXES = (
    "src/",
    "app/",
    "lib/",
    "components/",
    "docs/",
    "packages/",
)

# Top-level dirs that are not "source layout" by themselves.
NON_PACKAGE_ROOTS = {
    "tests",
    "test",
    "docs",
    "doc",
    "examples",
    "example",
    "samples",
    "benchmarks",
    "scripts",
    "tools",
    "ci",
    "build",
    "dist",
    "coverage",
    "node_modules",
    "vendor",
    "third_party",
    ".github",
    ".git",
    ".venv",
    "venv",
    "htmlcov",
    "site",
    "public",
    "assets",
    "static",
    "templates",
    "fixtures",
    "testdata",
}

BUILD_ARTIFACTS = ("dist/", "build/", ".next/", "coverage/", "htmlcov/")

# Common OSS root files — not "clutter".
KNOWN_ROOT_FILES = {
    "readme",
    "readme.md",
    "readme.rst",
    "readme.txt",
    "readme.ar.md",
    "readme.es-es.md",
    "license",
    "license.md",
    "license.txt",
    "license.rst",
    "licence",
    "licence.md",
    "licence.txt",
    "copying",
    "copying.txt",
    "changelog",
    "changelog.md",
    "changes",
    "changes.rst",
    "changes.md",
    "history.md",
    "history.rst",
    "contributing",
    "contributing.md",
    "contributing.rst",
    "code_of_conduct.md",
    "security",
    "security.md",
    "authors",
    "authors.md",
    "authors.rst",
    "notice",
    "notice.md",
    "makefile",
    "dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "tox.ini",
    "noxfile.py",
    "poetry.lock",
    "uv.lock",
    "requirements.txt",
    "requirements-dev.txt",
    "requirements.lock",
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "cargo.toml",
    "go.mod",
    "go.sum",
    "gemfile",
    "rakefile",
    "cmakelists.txt",
    "manifest.in",
    ".gitignore",
    ".gitattributes",
    ".editorconfig",
    ".pre-commit-config.yaml",
    ".readthedocs.yaml",
    ".coveragerc",
    "agents.md",
    "architecture.md",
    "installation.md",
    "usage.md",
    "requirements.md",
}


def _has_source_layout(paths: list[str]) -> bool:
    if any(path.startswith(STRUCTURE_PREFIXES) for path in paths):
        return True
    # Python/JS-style package: top-level dir with nested source (not tests/docs/…).
    for path in paths:
        pure = PurePosixPath(path)
        if len(pure.parts) < 2:
            continue
        root = pure.parts[0].lower()
        if root.startswith("."):
            continue
        if root in NON_PACKAGE_ROOTS:
            continue
        return True
    return False


def _root_clutter_count(paths: list[str]) -> int:
    root_files = [path for path in paths if "/" not in path]
    clutter = 0
    for path in root_files:
        name = PurePosixPath(path).name.lower()
        if name in KNOWN_ROOT_FILES:
            continue
        if name.startswith(("license", "licence")):
            continue
        if name.startswith("readme"):
            continue
        clutter += 1
    return clutter


def run_structure_check(files: list[FileItem]) -> CheckResult:
    paths = [file.path.lower() for file in files]
    has_structure = _has_source_layout(paths)
    has_artifacts = any(path.startswith(BUILD_ARTIFACTS) for path in paths)
    clutter = _root_clutter_count(paths)

    if has_structure and clutter <= 12 and not has_artifacts:
        score = 5
    elif has_structure and clutter <= 20 and not has_artifacts:
        score = 4
    elif has_structure or clutter <= 15:
        score = 3
    else:
        score = 1

    if score >= 4:
        status = "pass"
        message = "Project structure looks organized."
        recommendations: list[str] = []
    else:
        status = "warn"
        message = "Project structure could be clearer."
        recommendations = [
            "Group source code into a package or src/ layout and keep build artifacts out of git."
        ]
        if has_artifacts:
            recommendations.append("Avoid committing build outputs (dist/, build/, coverage/).")

    return CheckResult(
        key="structure",
        title="Project Structure",
        status=status,
        score=score,
        max_score=5,
        message=message,
        recommendations=recommendations,
    )
