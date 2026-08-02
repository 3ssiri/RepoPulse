"""Load repository files from a local filesystem path (offline scan)."""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path, PurePosixPath

from repopulse.models import FileItem, RepositoryInfo

IGNORE_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    ".tox",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
    ".eggs",
}

MAX_FILES = 5000
DEFAULT_MAX_BYTES = 200_000

_GITHUB_HTTPS = re.compile(
    r"^https?://(?:www\.)?github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$",
    re.IGNORECASE,
)
_GITHUB_SSH = re.compile(
    r"^(?:git@github\.com:|ssh://git@github\.com/)([^/]+)/([^/]+?)(?:\.git)?/?$",
    re.IGNORECASE,
)


def iter_local_files(root: Path, max_files: int = MAX_FILES) -> list[FileItem]:
    """Walk *root* and return blob FileItems with relative POSIX paths.

    Skips common dependency/cache directories. Caps at *max_files* for large trees.
    Does not follow directory symlinks outside the walk (followlinks=False).
    """
    root = root.resolve()
    files: list[FileItem] = []
    for dirpath, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
        dirnames[:] = [name for name in dirnames if name not in IGNORE_DIRS]
        current = Path(dirpath)
        for filename in filenames:
            if len(files) >= max_files:
                return files
            full = current / filename
            if full.is_symlink():
                # List symlink files by name only; do not resolve outside root.
                try:
                    if not full.resolve().is_relative_to(root):
                        continue
                except (OSError, ValueError):
                    continue
            try:
                size = full.stat().st_size if full.is_file() else None
            except OSError:
                size = None
            rel = full.relative_to(root).as_posix()
            files.append(
                FileItem(
                    path=rel,
                    name=PurePosixPath(rel).name,
                    type="blob",
                    size=size,
                )
            )
    return files


def read_local_text(root: Path, rel_path: str, max_bytes: int = DEFAULT_MAX_BYTES) -> str | None:
    """Read a UTF-8 text file under *root*. Returns None if missing, too large, or not a file."""
    root = root.resolve()
    # Prevent path traversal: resolve and require under root.
    candidate = (root / rel_path).resolve()
    try:
        if not candidate.is_relative_to(root):
            return None
    except (OSError, ValueError):
        return None
    if not candidate.is_file():
        return None
    try:
        if candidate.stat().st_size > max_bytes:
            return None
        return candidate.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None


def _run_git(root: Path, *args: str, timeout: float = 5.0) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    text = (result.stdout or "").strip()
    return text or None


def _parse_github_remote(remote_url: str) -> tuple[str, str] | None:
    cleaned = remote_url.strip()
    for pattern in (_GITHUB_HTTPS, _GITHUB_SSH):
        match = pattern.match(cleaned)
        if match:
            owner, repo = match.group(1), match.group(2)
            repo = repo.removesuffix(".git")
            return owner, repo
    return None


def repository_info_from_path(root: Path) -> RepositoryInfo:
    """Build RepositoryInfo from a local directory, enriching with git metadata when available."""
    root = root.resolve()
    name = root.name or "local"
    owner = "local"
    full_name = f"local/{name}"
    url = root.as_uri()
    default_branch = "main"
    last_pushed_at: str | None = None

    remote = _run_git(root, "remote", "get-url", "origin")
    if remote:
        parsed = _parse_github_remote(remote)
        if parsed:
            owner, repo_name = parsed
            name = repo_name
            full_name = f"{owner}/{repo_name}"
            url = f"https://github.com/{owner}/{repo_name}"

    branch = _run_git(root, "rev-parse", "--abbrev-ref", "HEAD")
    if branch and branch != "HEAD":
        default_branch = branch

    commit_date = _run_git(root, "log", "-1", "--format=%cI")
    if commit_date:
        last_pushed_at = commit_date

    return RepositoryInfo(
        owner=owner,
        name=name,
        full_name=full_name,
        description=None,
        url=url,
        default_branch=default_branch,
        private=False,
        stars=0,
        forks=0,
        open_issues=0,
        last_pushed_at=last_pushed_at,
    )
