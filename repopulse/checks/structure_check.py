from pathlib import PurePosixPath

from repopulse.models import CheckResult, FileItem

STRUCTURE_PREFIXES = (
    "src/",
    "app/",
    "apps/",
    "lib/",
    "components/",
    "docs/",
    "packages/",
    "services/",
    "crates/",
    "modules/",
    "workspaces/",
    "backend/",
    "frontend/",
    "internal/",
    "cmd/",
    "pkg/",
)

# Root markers that imply a monorepo / multi-package layout.
MONOREPO_ROOT_NAMES = frozenset(
    {
        "pnpm-workspace.yaml",
        "pnpm-workspace.yml",
        "lerna.json",
        "nx.json",
        "turbo.json",
        "go.work",
        "go.work.sum",
        "cargo.toml",  # often a workspace root
        "rush.json",
        "workspace.json",
        "moon.yml",
        "moon.yaml",
    }
)

MONOREPO_PATH_PREFIXES = (
    "packages/",
    "apps/",
    "services/",
    "crates/",
    "modules/",
    "workspaces/",
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
    "gnumakefile",
    "justfile",
    "taskfile.yml",
    "taskfile.yaml",
    "dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "compose.yml",
    "compose.yaml",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "tox.ini",
    "noxfile.py",
    "hatch.toml",
    "poetry.lock",
    "uv.lock",
    "pdm.lock",
    "requirements.txt",
    "requirements-dev.txt",
    "requirements.lock",
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "pnpm-workspace.yaml",
    "pnpm-workspace.yml",
    "lerna.json",
    "nx.json",
    "turbo.json",
    "rush.json",
    "cargo.toml",
    "cargo.lock",
    "go.mod",
    "go.sum",
    "go.work",
    "go.work.sum",
    "gemfile",
    "gemfile.lock",
    "rakefile",
    "cmakelists.txt",
    "manifest.in",
    ".gitignore",
    ".gitattributes",
    ".editorconfig",
    ".pre-commit-config.yaml",
    ".readthedocs.yaml",
    ".coveragerc",
    ".npmrc",
    ".nvmrc",
    ".node-version",
    ".python-version",
    ".tool-versions",
    ".ruby-version",
    ".env.example",
    "renovate.json",
    "renovate.json5",
    ".renovaterc",
    ".renovaterc.json",
    "agents.md",
    "architecture.md",
    "installation.md",
    "usage.md",
    "requirements.md",
    "codeowners",
    "owners",
    "citation.cff",
    "codecov.yml",
    "codecov.yaml",
    ".codecov.yml",
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


def _is_monorepo(paths: list[str], root_names: set[str]) -> bool:
    if any(name in MONOREPO_ROOT_NAMES for name in root_names):
        return True
    return any(path.startswith(MONOREPO_PATH_PREFIXES) for path in paths)


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
    root_names = {PurePosixPath(path).name.lower() for path in paths if "/" not in path}
    has_structure = _has_source_layout(paths)
    has_artifacts = any(path.startswith(BUILD_ARTIFACTS) for path in paths)
    clutter = _root_clutter_count(paths)
    monorepo = _is_monorepo(paths, root_names)

    # Monorepos legitimately carry more root config (workspaces, tooling).
    clutter_pass = 20 if monorepo else 12
    clutter_soft = 28 if monorepo else 20
    clutter_ok = 22 if monorepo else 15

    if has_structure and clutter <= clutter_pass and not has_artifacts:
        score = 5
    elif has_structure and clutter <= clutter_soft and not has_artifacts:
        score = 4
    elif has_structure or clutter <= clutter_ok:
        score = 3
    else:
        score = 1

    if score >= 4:
        status = "pass"
        if monorepo:
            message = "Monorepo / multi-package structure looks organized."
        else:
            message = "Project structure looks organized."
        recommendations: list[str] = []
    else:
        status = "warn"
        message = "Project structure could be clearer."
        recommendations = [
            "Group source code into a package, src/, packages/, or apps/ layout and keep build artifacts out of git."
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
