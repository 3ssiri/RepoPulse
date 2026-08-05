from typing import Literal

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
    "cargo.lock",
    "go.sum",
    "gemfile.lock",
    "composer.lock",
}

# Automated dependency update configs (Dependabot-style).
UPDATE_BOT_NAMES = {
    "dependabot.yml",
    "dependabot.yaml",
    "renovate.json",
    "renovate.json5",
    ".renovaterc",
    ".renovaterc.json",
}


def _has_update_automation(files: list[FileItem]) -> bool:
    # find_file matches basenames anywhere (including .github/dependabot.yml).
    return find_file(files, UPDATE_BOT_NAMES) is not None


def run_dependencies_check(files: list[FileItem]) -> CheckResult:
    status: Literal["pass", "warn", "fail"]
    has_manifest = any(
        find_file(files, {name}) is not None
        for name in (
            "package.json",
            "pyproject.toml",
            "requirements.txt",
            "cargo.toml",
            "go.mod",
            "gemfile",
            "composer.json",
        )
    )
    has_lockfile = any(find_file(files, {name}) is not None for name in LOCKFILES)
    has_update_bot = _has_update_automation(files)

    if has_lockfile and has_update_bot:
        status = "pass"
        message = "Dependency lockfile and automated update config (Dependabot/Renovate) detected."
        recommendations: list[str] = []
    elif has_lockfile:
        status = "pass"
        message = "Dependency lockfile detected; automated updates optional."
        # Soft, single recommendation — not a hard dual requirement.
        recommendations = [
            "Optional: add Dependabot or Renovate for automated dependency updates."
        ]
    elif has_update_bot and has_manifest:
        status = "warn"
        message = "Update automation found without a lockfile."
        recommendations = [
            "Add a lockfile (e.g. uv.lock, poetry.lock, package-lock.json) for reproducible installs."
        ]
    elif has_manifest:
        status = "warn"
        message = "Dependency manifest found without lockfile or update automation."
        recommendations = [
            "Add a lockfile and/or Dependabot/Renovate configuration when dependencies are managed in-repo."
        ]
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
