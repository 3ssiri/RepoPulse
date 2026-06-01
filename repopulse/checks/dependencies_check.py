from repopulse.models import CheckResult, FileItem
from repopulse.utils import find_file

LOCKFILES = {
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "poetry.lock",
    "uv.lock",
    "pdm.lock",
    "requirements.lock",
}


def run_dependencies_check(files: list[FileItem]) -> CheckResult:
    has_manifest = any(
        find_file(files, {name}) is not None
        for name in ("package.json", "pyproject.toml", "requirements.txt")
    )
    has_lockfile = any(find_file(files, {name}) is not None for name in LOCKFILES)
    has_dependabot = find_file(files, {"dependabot.yml", "dependabot.yaml"}) is not None

    if has_lockfile and has_dependabot:
        status = "pass"
        message = "Dependency manifest includes a lockfile and Dependabot configuration."
        recommendations: list[str] = []
    elif has_manifest and (has_lockfile or has_dependabot):
        status = "warn"
        message = "Dependency metadata is partially covered."
        recommendations = ["Add both a lockfile and Dependabot configuration for safer dependency updates."]
    elif has_manifest:
        status = "warn"
        message = "Dependency manifest found without lockfile or Dependabot configuration."
        recommendations = ["Add a lockfile and Dependabot configuration."]
    else:
        status = "warn"
        message = "No supported dependency manifest detected."
        recommendations = ["Add package metadata if this repository has installable dependencies."]

    return CheckResult(
        key="dependencies",
        title="Dependencies",
        status=status,
        score=0,
        max_score=0,
        message=message,
        recommendations=recommendations,
    )
