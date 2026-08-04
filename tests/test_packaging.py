"""Assert distribution metadata stays aligned with the public install name."""

from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"


def _load_project() -> dict:
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    return data["project"]


def test_pyproject_distribution_name_is_repopulse_cli():
    project = _load_project()
    assert project["name"] == "repopulse-cli"


def test_pyproject_cli_entry_is_repopulse():
    project = _load_project()
    scripts = project.get("scripts") or {}
    assert scripts.get("repopulse") == "repopulse.cli:app"


def test_pyproject_version_matches_package():
    import repopulse

    project = _load_project()
    assert project["version"] == repopulse.__version__
