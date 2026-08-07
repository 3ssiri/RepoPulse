import os
from pathlib import Path

from typer.testing import CliRunner

from repopulse.analyzer import build_local_health_report
from repopulse.cli import app
from repopulse.local_source import (
    IGNORE_DIRS,
    MAX_FILES,
    iter_local_files,
    read_local_text,
    repository_info_from_path,
)


def _seed_healthy_tree(root: Path) -> None:
    (root / "README.md").write_text("# Demo\n\nA healthy local sample.\n", encoding="utf-8")
    (root / "LICENSE").write_text("MIT License\n", encoding="utf-8")
    (root / ".gitignore").write_text("*.pyc\n.env\n", encoding="utf-8")
    (root / "pyproject.toml").write_text(
        '[project]\nname = "demo"\nversion = "0.1.0"\n\n[tool.pytest.ini_options]\n',
        encoding="utf-8",
    )
    tests = root / "tests"
    tests.mkdir()
    (tests / "test_demo.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")
    pkg = root / "demo"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("", encoding="utf-8")


def test_iter_local_files_skips_ignored_dirs(tmp_path: Path):
    (tmp_path / "README.md").write_text("hi", encoding="utf-8")
    ignored = tmp_path / "node_modules" / "pkg"
    ignored.mkdir(parents=True)
    (ignored / "index.js").write_text("x", encoding="utf-8")
    venv = tmp_path / ".venv" / "lib"
    venv.mkdir(parents=True)
    (venv / "site.py").write_text("x", encoding="utf-8")

    files, truncated = iter_local_files(tmp_path)
    paths = {item.path for item in files}

    assert truncated is False

    assert "README.md" in paths
    assert not any(path.startswith("node_modules/") for path in paths)
    assert not any(path.startswith(".venv/") for path in paths)
    assert IGNORE_DIRS  # sanity: constants exported


def test_read_local_text_and_path_traversal(tmp_path: Path):
    (tmp_path / "notes.txt").write_text("hello", encoding="utf-8")
    assert read_local_text(tmp_path, "notes.txt") == "hello"
    assert read_local_text(tmp_path, "missing.txt") is None
    # Traversal outside root
    outside = tmp_path.parent / "outside-secret.txt"
    outside.write_text("secret", encoding="utf-8")
    try:
        assert read_local_text(tmp_path, "../outside-secret.txt") is None
    finally:
        outside.unlink(missing_ok=True)


def test_read_local_text_skips_large_files(tmp_path: Path):
    big = tmp_path / "big.txt"
    big.write_bytes(b"x" * 300)
    assert read_local_text(tmp_path, "big.txt", max_bytes=100) is None


def test_repository_info_from_path_defaults(tmp_path: Path):
    info = repository_info_from_path(tmp_path)
    # Name may be the directory name or a parent git remote repo name.
    assert info.name
    assert info.full_name
    assert info.stars == 0
    assert info.forks == 0
    assert info.open_issues == 0
    # Offline scans cannot verify visibility; must not claim the repo is public.
    assert info.private is None
    assert info.url


def test_build_local_health_report_scores_positive(tmp_path: Path):
    _seed_healthy_tree(tmp_path)
    report = build_local_health_report(tmp_path)
    assert report.total_score > 0
    assert report.max_score > 0
    assert report.repository.name
    keys = {check.key for check in report.checks}
    assert "readme" in keys
    assert "license" in keys


def test_build_local_health_report_rejects_file(tmp_path: Path):
    file_path = tmp_path / "not-a-dir.txt"
    file_path.write_text("x", encoding="utf-8")
    try:
        build_local_health_report(file_path)
        raise AssertionError("expected ValueError")
    except ValueError as error:
        assert "Not a directory" in str(error)


def test_cli_scan_local_path_offline(tmp_path: Path):
    _seed_healthy_tree(tmp_path)
    result = CliRunner().invoke(app, ["scan", str(tmp_path), "--format", "summary", "--quiet"])
    assert result.exit_code == 0, result.output
    assert "Score:" in result.output or "score" in result.output.lower() or "/" in result.output


def test_cli_scan_dot_uses_local_when_cwd_is_dir(tmp_path: Path, monkeypatch):
    _seed_healthy_tree(tmp_path)
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["scan", ".", "--format", "json", "--quiet"])
    assert result.exit_code == 0, result.output
    assert '"total_score"' in result.output
    assert '"schema_version"' in result.output


def test_tool_never_loads_dotenv():
    """Trust boundary: the tool must not auto-load .env files at all — where
    python-dotenv searches depends on invocation context and can land inside
    an untrusted scanned repository (its CWD or a venv parent)."""
    import sys

    import repopulse.cli  # noqa: F401 — importing the CLI must not pull dotenv in

    assert "dotenv" not in sys.modules


def test_scan_does_not_import_env_file_from_scanned_repo(tmp_path: Path, monkeypatch):
    """Trust boundary: a scanned (possibly untrusted) repo's .env must never
    be loaded into the tool's process environment."""
    monkeypatch.setattr(os, "environ", os.environ.copy())
    _seed_healthy_tree(tmp_path)
    (tmp_path / ".env").write_text(
        "REPOPULSE_TEST_CANARY=injected\nHTTPS_PROXY=http://evil.example:8080\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(app, ["scan", ".", "--format", "summary", "--quiet"])

    assert result.exit_code == 0, result.output
    assert "REPOPULSE_TEST_CANARY" not in os.environ
    assert os.environ.get("HTTPS_PROXY") != "http://evil.example:8080"


def test_iter_local_files_caps_count_and_reports_truncation(tmp_path: Path):
    for index in range(10):
        (tmp_path / f"f{index}.txt").write_text("x", encoding="utf-8")
    # Cap artificially low without changing module constant for other tests
    files, truncated = iter_local_files(tmp_path, max_files=3)
    assert len(files) == 3
    assert truncated is True
    assert MAX_FILES >= 3


def test_iter_local_files_exact_cap_is_not_truncated(tmp_path: Path):
    for index in range(3):
        (tmp_path / f"f{index}.txt").write_text("x", encoding="utf-8")
    files, truncated = iter_local_files(tmp_path, max_files=3)
    assert len(files) == 3
    assert truncated is False


def test_build_local_health_report_flags_truncation(tmp_path: Path, monkeypatch):
    import repopulse.analyzer as analyzer_module

    _seed_healthy_tree(tmp_path)
    real_iter = analyzer_module.iter_local_files
    monkeypatch.setattr(
        analyzer_module,
        "iter_local_files",
        lambda root: (real_iter(root)[0], True),
    )
    report = build_local_health_report(tmp_path)
    assert report.scan_truncated is True


def test_build_local_health_report_not_truncated_by_default(tmp_path: Path):
    _seed_healthy_tree(tmp_path)
    report = build_local_health_report(tmp_path)
    assert report.scan_truncated is False
